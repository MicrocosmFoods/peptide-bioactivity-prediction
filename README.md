# Peptide Bioactivity Predictor

This repository contains a Nextflow pipeline for predicting bioactivity of peptides from input FASTA files. This workflow requires that you are directly inputting protein/peptide sequences, such as those already predicted from genome sequences or from proteomics experiments for example. 

## Workflow Usage
The main input is a directory of FASTA files, which you can split per sample or combine into one file if the headers can be linked back to the original sample name. The workflow predicts characteristics of peptides such as signal peptides, physicochemical properties, and compares them to an input database of known peptides. It then uses multiple classification models to predict the bioactivity of hte peptides. 

Importantly, the workflow does not handle automatic downloading of databases or other external data. You will need to provide the peptides database of known peptides and any additional models you want to use. 

Additionally, this worklfow is designed to only run using docker containers, and must be run with GPU resources available. 

To run the workflow:
```
nextflow run main.nf \\
--input_fastas <INPUT_DIRECTORY> \\
--peptides_db <PEPTIDES_DB> \\
--models_dir <MODELS_DIR> \\
--models_list <MODELS_LIST> \\
--outdir <OUTPUT_DIRECTORY> \\
--threads <THREADS>
-profile docker
```
