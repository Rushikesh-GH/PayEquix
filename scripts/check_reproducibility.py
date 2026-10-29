"""
Dataset Reproducibility Verification Script.
Generates dataset twice in separate isolated temporary directories using fixed seed 20261022.
Compares row counts, deterministic identifiers, payloads, and SHA-256 checksums.
"""

import sys
import shutil
import hashlib
import tempfile
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from generate_data import generate_synthetic_dataset

def compute_dir_hashes(dir_path: Path):
    hashes = {}
    for f in sorted(dir_path.glob("*.csv")):
        with open(f, "rb") as fh:
            hashes[f.name] = hashlib.sha256(fh.read()).hexdigest()
    return hashes

def check_reproducibility(seed: int = 20261022, profile: str = "starter"):
    print(f"\n========================================================")
    print(f"CHECKING REPRODUCIBILITY (Seed: {seed}, Profile: {profile})")
    print(f"========================================================\n")

    temp1 = Path(tempfile.mkdtemp(prefix="repro_run1_"))
    temp2 = Path(tempfile.mkdtemp(prefix="repro_run2_"))

    try:
        # Run 1
        print("Executing Run 1 in temporary directory...")
        import generate_data
        orig_gen = generate_data.GENERATED_DIR
        orig_gt = generate_data.GROUND_TRUTH_DIR
        orig_exp = generate_data.EXPORTS_DIR
        orig_man = generate_data.MANIFESTS_DIR

        # Point generate_data to temp1
        generate_data.GENERATED_DIR = temp1 / "generated"
        generate_data.GROUND_TRUTH_DIR = temp1 / "ground_truth"
        generate_data.EXPORTS_DIR = temp1 / "exports"
        generate_data.MANIFESTS_DIR = temp1 / "manifests"
        for d in [generate_data.GENERATED_DIR, generate_data.GROUND_TRUTH_DIR, generate_data.EXPORTS_DIR, generate_data.MANIFESTS_DIR]:
            d.mkdir(parents=True, exist_ok=True)

        manifest1 = generate_data.generate_synthetic_dataset(seed=seed, profile=profile)
        hashes1 = compute_dir_hashes(generate_data.GENERATED_DIR)

        # Run 2
        print("\nExecuting Run 2 in temporary directory...")
        generate_data.GENERATED_DIR = temp2 / "generated"
        generate_data.GROUND_TRUTH_DIR = temp2 / "ground_truth"
        generate_data.EXPORTS_DIR = temp2 / "exports"
        generate_data.MANIFESTS_DIR = temp2 / "manifests"
        for d in [generate_data.GENERATED_DIR, generate_data.GROUND_TRUTH_DIR, generate_data.EXPORTS_DIR, generate_data.MANIFESTS_DIR]:
            d.mkdir(parents=True, exist_ok=True)

        manifest2 = generate_data.generate_synthetic_dataset(seed=seed, profile=profile)
        hashes2 = compute_dir_hashes(generate_data.GENERATED_DIR)

        # Restore
        generate_data.GENERATED_DIR = orig_gen
        generate_data.GROUND_TRUTH_DIR = orig_gt
        generate_data.EXPORTS_DIR = orig_exp
        generate_data.MANIFESTS_DIR = orig_man

        # Compare row counts
        print("\nVerifying Entity Row Counts Match:")
        for ent, count1 in manifest1["row_counts"].items():
            count2 = manifest2["row_counts"].get(ent)
            assert count1 == count2, f"Row count mismatch for {ent}: {count1} != {count2}"
            print(f"  - {ent:25s}: {count1} == {count2} [MATCH]")

        # Compare SHA-256
        print("\nVerifying File Bitwise SHA-256 Checksums Match:")
        mismatches = []
        for fname, h1 in hashes1.items():
            h2 = hashes2.get(fname)
            match = (h1 == h2)
            if not match:
                mismatches.append(fname)
            print(f"  - {fname:25s}: {h1[:12]}... == {h2[:12]}... [{'MATCH' if match else 'MISMATCH'}]")

        if mismatches:
            print(f"\n[FAIL] Found {len(mismatches)} file checksum mismatches: {mismatches}")
            return False

        print("\n========================================================")
        print("REPRODUCIBILITY CHECK PASSED: 100% BITWISE DETERMINISM")
        print("========================================================\n")
        return True

    finally:
        shutil.rmtree(temp1, ignore_errors=True)
        shutil.rmtree(temp2, ignore_errors=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="starter", choices=["starter", "medium", "full"])
    parser.add_argument("--seed", type=int, default=20261022)
    args = parser.parse_args()

    success = check_reproducibility(seed=args.seed, profile=args.profile)
    if not success:
        sys.exit(1)
