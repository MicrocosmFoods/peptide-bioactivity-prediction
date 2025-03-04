# Peptide Bioactivity Predictor

This repository contains a Nextflow pipeline for predicting bioactivity of peptides from input FASTA files. This workflow requires that you are directly inputting protein/peptide sequences, such as those already predicted from genome sequences or from proteomics experiments for example. For predicting peptides from bacterial genomes, you can use the [bacMAGmining workflow](https://github.com/elizabethmcd/bacMAGmining) for example.

## Workflow Usage
The main input is a directory of FASTA files, which you can split per sample or combine into one file if the headers can be linked back to the original sample name. The workflow predicts characteristics of peptides such as signal peptides, physicochemical properties, and compares them to an input database of known peptides. It then uses multiple classification models to predict the bioactivity of hte peptides. 

Importantly, the workflow does not handle automatic downloading of databases or other external data. You will need to provide the peptides database of known peptides and any additional models you want to use. 

For predicting signal peptides with deepsig, you will need to provide the appropriate kingdom for your input sequences. By default the workfklow will use the gram-positive kingdom, but you can select from eukaryotic (euk) or gram-negative (gramn) kingdoms. 

The workflow can be run using either docker or conda, and this can be specified with the `-profile` flag. The workflow must be run with GPU resources available, as DeepSig requires GPUs.

To run the workflow:
```
nextflow run main.nf \\
--input_fastas <INPUT_DIRECTORY> \\
--peptides_db <PEPTIDES_DB> \\
--models_dir <MODELS_DIR> \\
--models_list <MODELS_LIST> \\
--kingdom <euk|gramp|gramn>
--outdir <OUTPUT_DIRECTORY> \\
--threads <THREADS>
-profile docker
```
