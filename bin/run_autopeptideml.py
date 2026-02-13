import argparse
import os
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
from Bio import SeqIO

"""
Updated for AutoPeptideML >= 2.0.x (current PyPI: 2.0.5).

Key change vs 1.0.x:
- Prediction is now exposed as a stable CLI:
    autopeptideml predict <result_dir> <features_path> --feature-field <feature_field> --output-path <preds.csv>
  Output includes `score` and `std` columns.
See: PyPI + GitHub README.
"""


def read_fasta(input_fasta: str) -> pd.DataFrame:
    """Reads FASTA and returns DataFrame with columns: peptide_id, sequence."""
    sequences = []
    for seq_record in SeqIO.parse(input_fasta, "fasta"):
        sequences.append({"peptide_id": seq_record.id, "sequence": str(seq_record.seq)})
    return pd.DataFrame(sequences)


def run_autopeptideml_predict_cli(
    df: pd.DataFrame,
    result_dir: str,
    feature_field: str = "sequence",
    model_name: str = "model",
    keep_all_columns: bool = True,
) -> pd.DataFrame:
    """
    Runs `autopeptideml predict` and returns a DataFrame containing predictions.

    AutoPeptideML 2.x CLI writes output with two added columns:
      - score : prediction
      - std   : ensemble std (uncertainty proxy)

    We rename:
      score -> <model_name>
      std   -> <model_name>_std
    """
    result_dir = str(result_dir)

    if feature_field not in df.columns:
        raise ValueError(
            f"feature_field='{feature_field}' not found in df columns {list(df.columns)}. "
            f"Set --feature_field to the column that contains sequences/SMILES."
        )

    with tempfile.TemporaryDirectory(prefix="autopeptideml_predict_") as td:
        td_path = Path(td)

        features_csv = td_path / "features.csv"
        output_csv = td_path / "predictions.csv"

        # The CLI expects a CSV with a column named exactly feature_field.
        df.to_csv(features_csv, index=False)

        cmd = [
            "autopeptideml",
            "predict",
            result_dir,
            str(features_csv),
            "--feature-field",
            feature_field,
            "--output-path",
            str(output_csv),
        ]

        # Run CLI
        subprocess.run(cmd, check=True)

        # Load predictions
        preds = pd.read_csv(output_csv)

    # Normalize column names
    rename_map = {}
    if "score" in preds.columns:
        rename_map["score"] = model_name
    if "std" in preds.columns:
        rename_map["std"] = f"{model_name}_std"
    preds = preds.rename(columns=rename_map)

    if not keep_all_columns:
        # Keep only id + feature + outputs (if present)
        keep = []
        for c in ["peptide_id", feature_field, model_name, f"{model_name}_std"]:
            if c in preds.columns:
                keep.append(c)
        preds = preds[keep]

    return preds


def save_predictions(predictions: pd.DataFrame, output_path: str) -> None:
    """Saves predictions to TSV."""
    predictions.to_csv(output_path, sep="\t", index=False)


def main():
    parser = argparse.ArgumentParser(description="Predict sequences using AutoPeptideML >= 2.0 (CLI-based).")
    parser.add_argument("--input_fasta", required=True, help="Path to the FASTA file.")
    parser.add_argument(
        "--result_dir",
        required=True,
        help="Path to the AutoPeptideML results/experiment directory produced by build-model.",
    )
    parser.add_argument("--model_name", required=True, help="Name used to label the prediction columns.")
    parser.add_argument("--output_tsv", required=True, help="Path to the output TSV file.")

    # New knobs (2.x)
    parser.add_argument(
        "--feature_field",
        default="sequence",
        help="Column name in the features CSV containing sequences/SMILES (default: sequence).",
    )
    parser.add_argument(
        "--keep_all_columns",
        action="store_true",
        help="Keep all original columns in output (default: False -> only id/feature/preds).",
    )

    args = parser.parse_args()

    df = read_fasta(args.input_fasta)
    preds = run_autopeptideml_predict_cli(
        df=df,
        result_dir=args.result_dir,
        feature_field=args.feature_field,
        model_name=args.model_name,
        keep_all_columns=args.keep_all_columns,
    )
    save_predictions(preds, args.output_tsv)


if __name__ == "__main__":
    main()