import os
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JOBS_DIR = DATA_DIR / "raw" / "jobs"
OUTPUT_DIR = DATA_DIR / "processed"
OUTPUT_DIR.mkdir(exist_ok=True)

def parse_job_file(filepath):
    """Parse a job ad text file into structured record."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split header and description at the --- separator
    if "---" not in content:
        print(f"  ⚠️  No separator found in {filepath.name} — skipping")
        return None

    header_part, description = content.split("---", 1)

    # Parse header fields
    record = {
        "filename": filepath.name,
        "filepath": str(filepath),
        "description": description.strip()
    }

    for line in header_part.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            record[key.strip().lower()] = value.strip()

    # Validate required fields
    required = ["title", "role_family", "language", "source"]
    for field in required:
        if field not in record:
            print(f"  ⚠️  Missing field '{field}' in {filepath.name}")
            record[field] = "unknown"

    return record


def ingest_all_jobs():
    """Load all job ad text files into structured records."""
    all_jobs = []
    skipped = 0

    # Walk all subdirectories under jobs/
    for txt_file in sorted(JOBS_DIR.rglob("*.txt")):
        record = parse_job_file(txt_file)
        if record:
            all_jobs.append(record)
        else:
            skipped += 1

    return all_jobs, skipped


def summarise(jobs):
    """Print summary statistics."""
    print(f"\nTotal job ads loaded: {len(jobs)}")

    # Count by role family
    families = {}
    for job in jobs:
        family = job.get("role_family", "unknown")
        families[family] = families.get(family, 0) + 1

    print("\nBy role family:")
    for family, count in sorted(families.items()):
        print(f"  {family}: {count}")

    # Count by language
    languages = {}
    for job in jobs:
        lang = job.get("language", "unknown")
        languages[lang] = languages.get(lang, 0) + 1

    print("\nBy language:")
    for lang, count in sorted(languages.items()):
        print(f"  {lang}: {count}")

    # Count by domain
    domains = {}
    for job in jobs:
        domain = job.get("domain", "unknown")
        domains[domain] = domains.get(domain, 0) + 1

    print("\nBy domain:")
    for domain, count in sorted(domains.items()):
        print(f"  {domain}: {count}")


if __name__ == "__main__":
    print("Loading job ads...")
    jobs, skipped = ingest_all_jobs()

    if skipped:
        print(f"Skipped {skipped} files (missing separator or parse error)")

    summarise(jobs)

    # Save to processed/
    output_path = OUTPUT_DIR / "jobs_corpus.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(jobs)} job ads to {output_path}")