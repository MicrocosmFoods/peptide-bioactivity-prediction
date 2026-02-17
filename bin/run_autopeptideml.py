import argparse
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
from Bio import SeqIO

"""
This script is modified from the Arcadia-Science/peptigate pipeline for interacting with the AutoPeptideML package.
See https://github.com/Arcadia-Science/peptigate/blob/main/scripts/run_autopeptideml.py for original source code.

Updated for AutoPeptideML v2.0.6, which uses a CLI-based predict command:
  autopeptideml predict <result_dir> <features_path> --feature-field <field> --output-path <output.csv>
"""


def fasta_to_csv(input_fasta, output_csv):
    """
    Converts a FASTA file to a CSV with 'peptide_id' and 'sequence' columns.

    Args:
    input_fasta (str): Path to the FASTA file.
    output_csv (str): Path to write the CSV file.

    Returns:
    pd.DataFrame: DataFrame with columns 'peptide_id' and 'sequence'.
    """
    sequences = []
    for seq_record in SeqIO.parse(input_fasta, "fasta"):
        sequences.append({"peptide_id": seq_record.id, "sequence": str(seq_record.seq)})
    df = pd.DataFrame(sequences)
    df.to_csv(output_csv, index=False)
    return df


def predict_sequences(features_csv, model_folder, output_csv):
    """
    Runs AutoPeptideML v2 CLI predict command.

    Args:
    features_csv (str): Path to the input CSV with a 'sequence' column.
    model_folder (str): Path to the model result directory.
    output_csv (str): Path for the predictions output CSV.
    """
    cmd = [
        "autopeptideml", "predict",
        str(model_folder),
        str(features_csv),
        "--feature-field", "sequence",
        "--output-path", str(output_csv),
    ]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Predict sequences using AutoPeptideML v2.")
    parser.add_argument("--input_fasta", required=True, help="Path to the FASTA file.")
    parser.add_argument("--model_folder", required=True, help="Path to the model result directory.")
    parser.add_argument("--model_name", required=True, help="Name of the model. Used to rename the prediction column.")
    parser.add_argument("--output_tsv", required=True, help="Path to the output TSV file.")

    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        features_csv = Path(tmpdir) / "features.csv"
        predictions_csv = Path(tmpdir) / "predictions.csv"

        # Convert FASTA to CSV for autopeptideml input
        input_df = fasta_to_csv(args.input_fasta, features_csv)

        # Run autopeptideml v2 CLI predict
        predict_sequences(features_csv, args.model_folder, predictions_csv)

        # Read predictions and merge with model name for output
        predictions = pd.read_csv(predictions_csv)
        predictions.rename(
            columns={
                "preds": f"{args.model_name}_prediction",
                "uncertainty": f"{args.model_name}_uncertainty",
            },
            inplace=True,
        )

        # If peptide_id isn't in predictions, merge from input
        if "peptide_id" not in predictions.columns:
            predictions = pd.concat([input_df[["peptide_id"]], predictions], axis=1)

        predictions.to_csv(args.output_tsv, sep="\t", index=False)


if __name__ == "__main__":
    main()