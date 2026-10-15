"""Download RCSB PDB structure files (.pdb) for a list of PDB IDs.

Usage:
    python source/search.py --ids ribosomal_subunits_results.txt --out-dir pdb_files
"""

import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

BASE_URL = "https://files.rcsb.org/download/{}.pdb"
TIMEOUT_SECONDS = 30
RETRIES = 3
BACKOFF_SECONDS = 2.0
MAX_WORKERS = 5


def read_ids(path: Path) -> list[str]:
    """Read one PDB ID per line, skipping blank lines."""
    with open(path, "r") as file:
        return [line.strip() for line in file if line.strip()]


def download_pdb(
    session: requests.Session,
    pdb_id: str,
    out_dir: Path,
    retries: int = RETRIES,
    backoff: float = BACKOFF_SECONDS,
    sleep=time.sleep,
) -> bool:
    """Download one .pdb file. Returns True on success.

    Retries on network errors, 5xx, and 429 (rate limit). Other 4xx responses
    (e.g. 404 for an unknown ID) fail immediately, since retrying won't change them.
    """
    url = BASE_URL.format(pdb_id)
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=TIMEOUT_SECONDS)
        except requests.exceptions.RequestException as err:
            print(f"Error downloading {pdb_id} (attempt {attempt}/{retries}): {err}")
        else:
            if response.status_code == 200:
                (out_dir / f"{pdb_id}.pdb").write_text(response.text)
                print(f"Downloaded: {pdb_id}")
                return True
            is_permanent = 400 <= response.status_code < 500 and response.status_code != 429
            if is_permanent:
                print(f"Failed to download: {pdb_id}, Status Code: {response.status_code}")
                return False
            print(f"Failed to download: {pdb_id}, Status Code: {response.status_code} "
                  f"(attempt {attempt}/{retries})")

        if attempt < retries:
            sleep(backoff)

    print(f"Failed to download {pdb_id} after {retries} attempts")
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download RCSB PDB structure files.")
    parser.add_argument("--ids", type=Path, default=Path("ribosomal_subunits_results.txt"),
                        help="Text file with one PDB ID per line.")
    parser.add_argument("--out-dir", type=Path, default=Path("pdb_files"),
                        help="Directory to save .pdb files into.")
    args = parser.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    pdb_ids = read_ids(args.ids)

    with requests.Session() as session, ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # list() forces the results so any unexpected exception surfaces instead of being dropped
        results = list(executor.map(lambda pid: download_pdb(session, pid, args.out_dir), pdb_ids))

    print(f"Downloaded {sum(results)} of {len(pdb_ids)} files to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
