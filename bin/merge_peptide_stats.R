#! /usr/local/bin/R

library(tidyverse)

######################################################################################
# Merge peptide stats with metadata
# Merge results from DeepSig, peptides.py, and DIAMOND Blastp results against database
######################################################################################

# command-line arguments
args <- commandArgs(trailingOnly = TRUE)

# input files
peptides_info_tsv <- args[1]
deep_sig_tsv <- args[2]
diamond_tsv <- args[3]
autopeptideml_dir <- args[4]
output_tsv <- args[5]


# read in files
peptides_info <- read_tsv(peptides_info_tsv, col_names = TRUE)
deepsig_info <- read_tsv(
    deep_sig_tsv,
    col_names = c(
        "peptide_id", "tool", "deepsig_feature",
        "deepsig_feature_start", "deepsig_feature_end",
        "deepsig_feature_score", "tmp1", "tmp2",
        "deepsig_description"
    )
) %>% 
    select(-tool, -tmp1, -tmp2)

diamond_blast_results <- read_tsv(diamond_tsv)  %>% 
    mutate(peptide_id = qseqid)  %>% 
    select(-qseqid)

# read in autopeptideml results
autopeptideml_files <- list.files(path = autopeptideml_dir, pattern = "autopeptideml_.*\\.tsv$", full.names=TRUE)

autopeptideml_df <- map_dfr(autopeptideml_files, function(file) {
    read_tsv(file) %>%
        # Rename the third column to 'value' and get bioactivity name from column name
        rename(bioactivity = 3) %>%
        # Add column for bioactivity name (original column name)
        mutate(bioactivity_name = names(read_tsv(file))[3])
}) %>%
    # Pivot wider to get one column per bioactivity
    pivot_wider(
        id_cols = c(peptide_id, sequence),
        names_from = bioactivity_name,
        values_from = bioactivity
    )

# merge peptides info with deepsig results
# merge with diamond blastp results
# merge with autopeptideml results
all_peptide_info <- deepsig_info  %>% 
    left_join(peptides_info, by = "peptide_id") %>% 
    left_join(diamond_blast_results, by = "peptide_id") %>% 
    left_join(autopeptideml_df, by = "peptide_id")

# write to tsv
write_tsv(all_peptide_info, output_tsv)
