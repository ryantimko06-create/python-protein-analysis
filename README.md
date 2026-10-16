# python-protein-analysis

A project built with Krish Parmar. It pulls ribosomal structure records from the RCSB Protein Data Bank (PDB), downloads the structure files, and runs descriptive statistics and plots on the collected metadata.

## Pipeline

1. **`source/protein_finder`** searches the RCSB PDB for entries with "RIBOSOME" in their keywords and writes the matching IDs to `ribosomal_subunits_results.txt`. To get smaller datasets, use text files using the following:

```
head -n 10 ribosomal_subunits_results.txt > test_ids.txt
python source/data.py --ids test_ids.txt --out test_metadata.xlsx
python source/search.py --ids test_ids.txt --out-dir test_pdb_files
python source/st_analysis.py --excel test_metadata.xlsx

The args here allow us to manually set input files and output files, plus splice the primary data set
```

2. **`source/data.py`** queries the RCSB API for metadata on each ID (title, method, release date, resolution, entity counts, molecular weight) and writes `rcsb_statistical_data_enhanced.xlsx`.
3. **`source/search.py`** downloads each entry's `.pdb` file into `pdb_files/`, with 5 parallel workers, a 30-second timeout, and retries on network errors and server errors.
4. **`source/st_analysis.py`** prints summary statistics and plots the distributions of molecular weight, resolution, and release date.
5. **`file_sort.py`** deletes files in `pdb_files/` larger than 1.5 MB. It is Windows-specific as written (it uses a backslash path), and it deletes files, so review it before running.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python source/protein_finder
python source/data.py --ids ribosomal_subunits_results.txt --out rcsb_statistical_data_enhanced.xlsx
python source/search.py --ids ribosomal_subunits_results.txt --out-dir pdb_files
python source/st_analysis.py --excel rcsb_statistical_data_enhanced.xlsx
```

## Tests

```bash
pytest
```

The tests cover the metadata parsing and the download retry logic. They don't call the network.
