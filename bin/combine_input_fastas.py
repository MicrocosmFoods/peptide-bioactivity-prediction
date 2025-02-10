#!/usr/bin/env python3

from Bio import SeqIO
import os
import argparse
from pathlib import Path

def get_genome_name(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def is_valid_sequence(seq):
    # Check if sequence exists and isn't empty after stripping whitespace
    return bool(str(seq).strip())

def process_fasta_file(input_file, genome_name, add_prefix=False):
    new_records = {}
    with open(input_file, "r") as fasta_file:
        for record in SeqIO.parse(fasta_file, "fasta"):
            if not is_valid_sequence(record.seq):
                print(f"Warning: Skipping empty sequence for {record.id} in {genome_name}")
                continue
                
            if record.seq.endswith('*'):
                record.seq = record.seq[:-1]
            
            # Only add genome name prefix if specified
            if add_prefix:
                record.id = f"{genome_name}_{record.id}"
            new_records[record.id] = record
    return new_records

def combine_fastas(input_files, output_file, add_prefix=False):
    all_records = {}
    for input_file in input_files:
        genome_name = get_genome_name(input_file)
        new_records = process_fasta_file(input_file, genome_name, add_prefix)
        all_records.update(new_records)

    # Final validation before writing
    valid_records = []
    for record_id, record in all_records.items():
        if is_valid_sequence(record.seq):
            valid_records.append(record)
        else:
            print(f"Warning: Removing record with empty sequence: {record_id}")

    # Write combined FASTA
    with open(output_file, "w") as outfile:
        SeqIO.write(valid_records, outfile, "fasta")
        print(f"Wrote {len(valid_records)} valid sequences to {output_file}")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Combine multiple FASTA files into a single FASTA file')
    parser.add_argument('input_files', nargs='+', help='Input FASTA files')
    parser.add_argument('--output_file', required=True, help='Output concatenated FASTA file')
    parser.add_argument('--add_prefix', action='store_true', 
                      help='Add input filename prefix to sequence IDs (default: False)')
    return parser.parse_args()

def main():
    args = parse_arguments()
    combine_fastas(args.input_files, args.output_file, add_prefix=args.add_prefix)

if __name__ == '__main__':
    main()