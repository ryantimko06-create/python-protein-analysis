"""Fetch RCSB PDB metadata for a list of PDB IDs and export it to Excel.

Usage:
    python source/data.py --ids ribosomal_subunits_results.txt --out rcsb_statistical_data_enhanced.xlsx
"""

import argparse
from pathlib import Path

import pandas as pd

FIELDS = [
    "rcsb_id",
    "struct.title",
    "exptl.method",
    "rcsb_accession_info.initial_release_date",
    "rcsb_entry_info.resolution_combined",
    "rcsb_entry_info.polymer_entity_count",
    "rcsb_entry_info.nonpolymer_entity_count",
    "rcsb_entry_info.molecular_weight",
]


def read_ids(path: Path) -> list[str]:
    """Read one PDB ID per line, skipping blank lines."""
    with open(path, "r") as file:
        return [line.strip() for line in file if line.strip()]


def fetch_entry(pdb_id: str) -> dict:
    """Query the RCSB PDB API for one entry and return its raw JSON entry.

    rcsbapi is imported here rather than at module top so parse_entry() can be
    tested without the package installed.
    """
    from rcsbapi.data import DataQuery as Query

    query = Query(input_type="entries", input_ids=[pdb_id], return_data_list=FIELDS)
    result = query.exec()
    return result.get("data", {}).get("entries", [{}])[0]


def parse_entry(entry: dict) -> dict:
    """Flatten one API entry into a record. Missing fields become empty values, not errors."""
    info = entry.get("rcsb_entry_info", {})

    method_list = entry.get("exptl", [])
    method = method_list[0].get("method", "") if isinstance(method_list, list) and method_list else ""

    resolution_list = info.get("resolution_combined", [])
    resolution = resolution_list[0] if isinstance(resolution_list, list) and resolution_list else None

    return {
        "PDB ID": entry.get("rcsb_id", ""),
        "Title": entry.get("struct", {}).get("title", ""),
        "Experimental Method": method,
        "Release Date": entry.get("rcsb_accession_info", {}).get("initial_release_date", ""),
        "Resolution": resolution,
        "Polymer Entity Count": info.get("polymer_entity_count", 0) or 0,
        "Non-Polymer Entity Count": info.get("nonpolymer_entity_count", 0) or 0,
        "Molecular Weight": info.get("molecular_weight", 0.0) or 0.0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch RCSB PDB metadata to Excel.")
    parser.add_argument("--ids", type=Path, default=Path("ribosomal_subunits_results.txt"),
                        help="Text file with one PDB ID per line.")
    parser.add_argument("--out", type=Path, default=Path("rcsb_statistical_data_enhanced.xlsx"),
                        help="Output Excel file.")
    args = parser.parse_args(argv)

    pdb_ids = read_ids(args.ids)
    records = []
    for index, pdb_id in enumerate(pdb_ids, start=1):
        print(f"Processing {index}/{len(pdb_ids)}: {pdb_id}")
        try:
            entry = fetch_entry(pdb_id)
        except Exception as err:  # one bad ID shouldn't stop the run
            print(f"Error fetching {pdb_id}: {err}")
            continue
        records.append(parse_entry(entry))

    pd.DataFrame(records).to_excel(args.out, index=False)
    print(f"Wrote {len(records)} of {len(pdb_ids)} records to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
