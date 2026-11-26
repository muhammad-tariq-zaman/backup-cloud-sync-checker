# backup-cloud-sync-checker

Check local files against a cloud backup manifest: local.csv and cloud.csv both list path, size_bytes and sha256 (sha256 may be empty) — MISSING IN CLOUD for files in the local manifest but not the cloud, SIZE MISMATCH when both have the file but the sizes differ, HASH MISMATCH when the sizes match but the SHA-256 differs, EXTRA IN CLOUD for files in the cloud manifest but not local, IN SYNC when size and hash match (or neither side has a hash) — MISSING IN CLOUD first, then SIZE MISMATCH, then HASH MISMATCH, then EXTRA IN CLOUD; in-sync files are counted, not listed one by one. Rows with a non-numeric size_bytes are reported as skipped, not silently dropped.

Sample input is included (sample-local.csv with four files and sample-cloud.csv with four files).

## How to run

```sh
python3 main.py sample-local.csv sample-cloud.csv
```

## Example output

```
Notes/todo.txt: MISSING IN CLOUD - not in cloud manifest
Photos/office.jpg: SIZE MISMATCH - local 120400 byte(s), cloud 119000 byte(s)
Old/archive.zip: EXTRA IN CLOUD - not in local manifest
2 in sync, 1 missing in cloud, 1 size mismatch(es), 0 hash mismatch(es), 1 extra in cloud.
```

Standard library only. Run the tests with `python3 -m unittest discover`.
