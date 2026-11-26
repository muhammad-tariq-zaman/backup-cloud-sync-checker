"""Check local files against a cloud backup manifest.

Usage: python3 main.py local.csv cloud.csv
Both files have columns: path,size_bytes,sha256 (sha256 may
be empty). For each file this reports:
- MISSING IN CLOUD: in the local manifest but not the cloud.
- SIZE MISMATCH: in both, but the sizes differ.
- HASH MISMATCH: same size in both, but the SHA-256 differs.
- EXTRA IN CLOUD: in the cloud manifest but not local.
- IN SYNC: same size and same hash (or no hash on either side).
MISSING IN CLOUD first, then SIZE MISMATCH, then HASH
MISMATCH, then EXTRA IN CLOUD; in-sync files are not listed
one by one, only counted. Rows with a non-numeric size_bytes
are reported as skipped, not silently dropped.
"""
import argparse, csv, sys

VERDICT_ORDER = {"MISSING IN CLOUD": 0, "SIZE MISMATCH": 1,
                 "HASH MISMATCH": 2, "EXTRA IN CLOUD": 3}

def _load(rows):
    files = {}
    skipped = 0
    for row in rows:
        try:
            path = row["path"].strip()
            size = int(row["size_bytes"])
            sha = (row.get("sha256") or "").strip()
            if not path or size < 0:
                raise ValueError("bad value")
        except (KeyError, AttributeError, ValueError, TypeError):
            skipped += 1
            continue
        files[path] = (size, sha)
    return files, skipped

def check(local_rows, cloud_rows):
    local, skipped_local = _load(local_rows)
    cloud, skipped_cloud = _load(cloud_rows)
    out = []
    in_sync = 0
    for path, (size, sha) in local.items():
        if path not in cloud:
            out.append((path, "MISSING IN CLOUD", "not in cloud manifest"))
        elif cloud[path][0] != size:
            out.append((path, "SIZE MISMATCH",
                        f"local {size} byte(s), cloud {cloud[path][0]} byte(s)"))
        elif sha and cloud[path][1] and sha != cloud[path][1]:
            out.append((path, "HASH MISMATCH", "same size, different SHA-256"))
        else:
            in_sync += 1
    for path in cloud:
        if path not in local:
            out.append((path, "EXTRA IN CLOUD", "not in local manifest"))
    out.sort(key=lambda r: (VERDICT_ORDER[r[1]], r[0]))
    return out, in_sync, skipped_local + skipped_cloud

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("local")
    parser.add_argument("cloud")
    args = parser.parse_args(argv)
    with open(args.local, newline="", encoding="utf-8") as f:
        local_rows = list(csv.DictReader(f))
    with open(args.cloud, newline="", encoding="utf-8") as f:
        cloud_rows = list(csv.DictReader(f))
    results, in_sync, skipped = check(local_rows, cloud_rows)
    for path, verdict, detail in results:
        print(f"{path}: {verdict} - {detail}")
    counts = {v: sum(1 for _, verdict, _ in results if verdict == v)
              for v in VERDICT_ORDER}
    print(f"{in_sync} in sync, {counts['MISSING IN CLOUD']} missing in cloud, "
          f"{counts['SIZE MISMATCH']} size mismatch(es), "
          f"{counts['HASH MISMATCH']} hash mismatch(es), "
          f"{counts['EXTRA IN CLOUD']} extra in cloud.")
    if skipped:
        print(f"Skipped {skipped} invalid row(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
