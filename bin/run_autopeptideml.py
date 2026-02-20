import argparse
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
from Bio import SeqIO


def fasta_to_csv(input_fasta, output_csv):
    """
    Converts a FASTA file to a CSV with 'peptide_id' and 'sequence' columns.
    """
    sequences = []
    for seq_record in SeqIO.parse(str(input_fasta), "fasta"):
        sequences.append({"peptide_id": seq_record.id, "sequence": str(seq_record.seq)})

    df = pd.DataFrame(sequences)
    df.to_csv(output_csv, index=False)
    return df


def predict_sequences(features_csv, ensemble_path, output_dir):
    """
    Runs AutoPeptideML v1.0.6 CLI predict command.

    Command:
      autopeptideml-predict <features_csv> --ensemble <ensemble_path> --outputdir <output_dir>

    Predictions expected at:
      <output_dir>/predictions.csv
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "autopeptideml-predict",
        str(features_csv),
        "--ensemble",
        str(ensemble_path),
        "--outputdir",
        str(output_dir),
    ]
    subprocess.run(cmd, check=True)

    pred_path = output_dir / "predictions.csv"
    if not pred_path.exists():
        raise FileNotFoundError(
            f"Expected predictions at {pred_path}, but it was not found. "
            f"Command was: {' '.join(cmd)}"
        )
    return pred_path


def main():
    parser = argparse.ArgumentParser(description="Predict sequences using AutoPeptideML v1.0.6.")
    parser.add_argument("--input_fasta", required=True, help="Path to the FASTA file.")
    parser.add_argument("--ensemble", required=True, help="Path to the ensemble directory (e.g., AB_1/ensemble).")
    parser.add_argument("--model_name", required=True, help="Name of the model. Used to rename the prediction/uncertainty columns.")
    parser.add_argument("--output_tsv", required=True, help="Path to the output TSV file.")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        features_csv = tmpdir / "peptides.csv"
        output_dir = tmpdir / "autopeptideml_out"

        # Convert FASTA to CSV for autopeptideml input
        input_df = fasta_to_csv(args.input_fasta, features_csv)

        # Run autopeptideml v1.0.6 CLI predict
        predictions_csv = predict_sequences(features_csv, args.ensemble, output_dir)

        # Read predictions and rename columns
        predictions = pd.read_csv(predictions_csv)

        # Common expected columns: preds, uncertainty
        rename_map = {}
        if "preds" in predictions.columns:
            rename_map["preds"] = f"{args.model_name}_prediction"
        if "uncertainty" in predictions.columns:
            rename_map["uncertainty"] = f"{args.model_name}_uncertainty"
        predictions.rename(columns=rename_map, inplace=True)

        # Ensure peptide_id exists
        if "peptide_id" not in predictions.columns:
            # If predictions are row-aligned with input, prepend peptide_id
            if len(predictions) != len(input_df):
                raise ValueError(
                    "predictions.csv does not contain peptide_id and row counts "
                    "do not match input peptides; cannot safely add peptide_id."
                )
            predictions.insert(0, "peptide_id", input_df["peptide_id"].values)

        predictions.to_csv(args.output_tsv, sep="\t", index=False)


if __name__ == "__main__":
    main()