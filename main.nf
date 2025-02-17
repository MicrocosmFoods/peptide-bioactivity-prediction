#! /usr/bin/env nextflow

// Description
// Predict bioactivity of peptides from input FASTA files.

log.info """\

PREDICT BIOACTIVITY AND PHYSICOCHEMICAL PROPERTIES OF PEPTIDES.
=================================================================
input_fastas                    : $params.input_fastas
peptides_db                     : $params.peptides_db
models_dir                      : $params.models_dir
models_list                     : $params.models_list
outdir                          : $params.outdir
threads                         : $params.threads
"""

// define channels
input_fastas = Channel.fromPath("${params.input_fastas}/*.{fasta,faa,fa}")

peptides_db_ch = channel.fromPath(params.peptides_db)
peptide_models_dir = channel.fromPath(params.models_dir)
peptide_models_list = channel.fromPath(params.models_list)
    .splitText()
    .map { it.trim()}

// workflow steps

workflow {
    // combine all input fastas into one
    combine_input_fastas(input_fastas.collect())
    combined_fasta = combine_input_fastas.out.combined_fasta

    // deepsig predictions
    deepsig(combined_fasta)
    deepsig_results = deepsig.out.deepsig_tsv

    // peptides.py sequence characterization
    characterize_peptides(combined_fasta)
    peptides_results = characterize_peptides.out.peptides_tsv

    // DIAMOND seq similarity to peptide database
    make_diamond_db(peptides_db_ch)
    peptides_dmnd_db = make_diamond_db.out.peptides_diamond_db
    diamond_blastp_input_ch = peptides_dmnd_db.combine(combined_fasta)
    diamond_blastp(diamond_blastp_input_ch)
    blastp_results = diamond_blastp.out.blastp_hits_tsv

    // autopeptideml predictions
    model_combos_ch = combined_fasta
        .combine(peptide_models_dir)
        .combine(peptide_models_list)
    autopeptideml_predictions(model_combos_ch)
    autopeptideml_results = autopeptideml_predictions.out.autopeptideml_tsv.collect()
    
    // merge all stats
    merge_peptide_stats(peptides_results, deepsig_results, blastp_results, autopeptideml_results)
}

process combine_input_fastas {
    tag "combine_input_fastas"
    publishDir "${params.outdir}/combine_input_fastas", mode: 'copy'

    memory = "10 GB"
    cpus = 1

    container "quay.io/biocontainers/mulled-v2-949aaaddebd054dc6bded102520daff6f0f93ce6:aa2a3707bfa0550fee316844baba7752eaab7802-0"
    conda "envs/biopython.yml"

    input:
    path(input_fastas)

    output:
    path("*.fasta"), emit: combined_fasta

    script:
    """
    python ${baseDir}/bin/combine_input_fastas.py ${input_fastas} --output_file all_samples_combined.fasta
    """
}

process deepsig {
    tag "deepsig_predictions"
    publishDir "${params.outdir}/deepsig", mode: 'copy'
    
    accelerator 1, type: 'nvidia-t4'
    cpus = 8
    
    container "public.ecr.aws/biocontainers/deepsig:1.2.5--pyhca03a8a_1"
    conda "envs/deepsig.yml"

    input: 
    path(combined_fasta)

    output: 
    path("*.tsv"), emit: deepsig_tsv

    script: 
    """
    deepsig -f ${combined_fasta} -o all_deepsig_predictions.tsv -k gramp -t ${task.cpus}
    """
}

process characterize_peptides {
    tag "peptide_characterization"
    publishDir "${params.outdir}/peptide_characterization", mode: 'copy'

    memory = "10 GB"
    cpus = 1

    container "elizabethmcd/peptides"
    conda "envs/peptides.yml"

    input:
    path(combined_fasta)

    output: 
    path("*.tsv"), emit: peptides_tsv

    script:
    """
    python ${baseDir}/bin/characterize_peptides.py ${combined_fasta} all_peptide_characteristics.tsv
    """
}

process make_diamond_db {
    tag "make_diamond_db"

    memory = "5 GB"
    cpus = 1

    container "public.ecr.aws/biocontainers/diamond:2.1.7--h43eeafb_1"
    conda "envs/diamond.yml"

    input:
    path(peptides_fasta)

    output:
    path("*.dmnd"), emit: peptides_diamond_db

    // ignore warnings about DNA only because of short peptides
    script:
    """
    diamond makedb --in ${peptides_fasta} -d peptides_db.dmnd --ignore-warnings 
    """
}

process diamond_blastp {
    tag "diamond_blastp"
    publishDir "${params.outdir}/diamond_blastp", mode: 'copy'

    memory = "10 GB"

    container "public.ecr.aws/biocontainers/diamond:2.1.7--h43eeafb_1"
    conda "envs/diamond.yml"

    input:
    tuple path(peptides_diamond_db), path(combined_fasta)

    output:
    path("*.tsv"), emit: blastp_hits_tsv

    script:
    """
    diamond blastp -d ${peptides_diamond_db} \\
     -q ${combined_fasta} \\
     -o all_blast_results.tsv \\
     --header simple \\
     --max-target-seqs 1 \\
    --outfmt 6 qseqid sseqid full_sseq pident length qlen slen mismatch gapopen qstart qend sstart send evalue bitscore
    """
}

process autopeptideml_predictions {
    tag "${model_name}_autopeptideml"
    publishDir "${params.outdir}/autopeptideml", mode: 'copy'

    memory = "10 GB"
    cpus = 6

    container "elizabethmcd/autopeptideml:latest"
    conda "envs/autopeptideml.yml"

    input:
    tuple path(combined_fasta), path(model_dir), val(model_name)

    output:
    path("*.tsv"), emit: autopeptideml_tsv

    script:
    """
    python3 ${baseDir}/bin/run_autopeptideml.py \\
        --input_fasta ${combined_fasta} \\
        --model_folder "${model_dir}/${model_name}/ensemble" \\
        --model_name ${model_name} \\
        --output_tsv "autopeptideml_${model_name}.tsv"
    """
}

process merge_peptide_stats {
    tag "merge_peptide_stats"
    publishDir "${params.outdir}/main_results", mode: 'copy'

    memory = "10 GB"
    cpus = 1

    container "rocker/tidyverse:latest"
    conda "envs/tidyverse.yml"

    input:
    path(peptides_results)
    path(deepsig_results)
    path(blastp_results)
    path("autopeptideml_*.tsv")

    output:
    path("*.tsv"), emit: main_results_tsv

    script:
    """
    Rscript ${baseDir}/bin/merge_peptide_stats.R \\
    ${peptides_results} \\
    ${deepsig_results} \\
    ${blastp_results} \\
    ./ \\
    all_peptides_predictions.tsv
    """
}
