import chromadb
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
CHROMA_DIR = DATA_DIR / "chromadb"

def check_corpus_health():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection("job_ads")

    results = collection.get(include=["metadatas"])
    metadatas = results["metadatas"]
    total = len(metadatas)

    print(f"Total documents: {total}\n")

    # Distribution by role family
    families = Counter(m["role_family"] for m in metadatas)
    print("By role family:")
    for family, count in sorted(families.items()):
        pct = count / total * 100
        status = "⚠️" if pct < 10 else "✅"
        print(f"  {status} {family}: {count} ({pct:.1f}%)")

    # Distribution by domain
    domains = Counter(m["domain"] for m in metadatas)
    print("\nBy domain:")
    for domain, count in sorted(domains.items()):
        pct = count / total * 100
        print(f"  {domain}: {count} ({pct:.1f}%)")

    # Distribution by experience level
    exp_levels = Counter(m["experience_level"] for m in metadatas)
    print("\nBy experience level:")
    for level, count in sorted(exp_levels.items()):
        pct = count / total * 100
        print(f"  {level}: {count} ({pct:.1f}%)")

# Imbalance warnings — check all three categories
    print("\n── Imbalance Analysis ──")

    # Role family imbalance
    min_family = min(families.values())
    max_family = max(families.values())
    family_ratio = max_family / min_family
    status = "⚠️  WARNING" if family_ratio > 3 else "✅ OK"
    print(f"Role family ratio (max/min): {family_ratio:.1f}x — {status}")
    if family_ratio > 3:
        minority = min(families, key=families.get)
        print(f"   Add more documents for: {minority}")

    # Domain imbalance
    min_domain = min(domains.values())
    max_domain = max(domains.values())
    domain_ratio = max_domain / min_domain
    status = "⚠️  WARNING" if domain_ratio > 2 else "✅ OK"
    print(f"Domain ratio (max/min):      {domain_ratio:.1f}x — {status}")
    if domain_ratio > 2:
        minority = min(domains, key=domains.get)
        print(f"   Add more documents for: {minority}")

    # Experience level imbalance
    min_exp = min(exp_levels.values())
    max_exp = max(exp_levels.values())
    exp_ratio = max_exp / min_exp
    status = "⚠️  WARNING" if exp_ratio > 3 else "✅ OK"
    print(f"Experience level ratio:      {exp_ratio:.1f}x — {status}")
    if exp_ratio > 3:
        minority = min(exp_levels, key=exp_levels.get)
        print(f"   Add more documents for: {minority}")

if __name__ == "__main__":
    check_corpus_health()