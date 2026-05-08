import pandas as pd
import yaml
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
EXCEL_PATH = DATA_DIR / "AI_Automotive_Transition_Enhanced.xlsx"
OUTPUT_PATH = DATA_DIR / "automotive_to_ai_mappings.yaml"

def clean(value):
    if pd.isna(value):
        return None
    return str(value).strip()

def split_skills(value):
    if pd.isna(value):
        return []
    return [s.strip() for s in str(value).split(",") if s.strip()]

def split_roles(value):
    if pd.isna(value):
        return []
    # Handle both "/" and "," as separators
    raw = str(value).replace(",", "/")
    return list(dict.fromkeys(
        [r.strip() for r in raw.split("/") if r.strip()]
    ))

def map_to_family(role_title):
    """Map a target role to one or two role families."""
    role_lower = role_title.lower()
    families = []

    # Roles to skip entirely
    SKIP_ROLES = [
        "ai systems engineer",
        "simulation",
        "rl engineer"
    ]
    if any(skip == role_lower.strip() for skip in SKIP_ROLES):
        return ["skip"]

    if any(kw in role_lower for kw in [
        "mlops", "platform engineer", "cloud ai", "devops",
        "ai integration",      # remapped to mlops
        "ai architect",        # remapped to mlops
        "ai system engineer",  # remapped to mlops (singular)
    ]):
        families.append("mlops_engineer")

    if any(kw in role_lower for kw in [
        "ml engineer", "ai software", "machine learning engineer",
        "sdv engineer", "embedded ai", "edge ai", "computer vision",
        "digital twin", "ai engineer", "data scientist",
        "autonomous control", "predictive model", "surrogate model",
        "generative design", "industrial ai",
    ]):
        families.append("ml_engineer")

    if any(kw in role_lower for kw in [
        "test", "validation", "qa", "quality",
        "ai simulation",       # added to ml_test
    ]):
        families.append("ml_test")

    if any(kw in role_lower for kw in [
        "manager", "product", "program", "transformation",
        "consultant", "lead", "director", "owner",
        "responsible ai", "ai safety", "ai security", "ai risk"
    ]):
        families.append("ai_mngr")

    return families if families else ["unclassified"]


def convert():
    df = pd.read_excel(EXCEL_PATH)
    print(f"Loaded {len(df)} rows from Excel")

    mappings = []
    seen = set()  # track duplicates

    for _, row in df.iterrows():
        source_profile = clean(row["Automotive Current Role"])
        if not source_profile:
            continue

        target_roles = split_roles(row["Target Role"])
        transferability = clean(row["Transferability"]) or "medium"
        skills_both = split_skills(row["Skills (both paths)"])
        skills_auto = split_skills(row["Skills (Automotive Path Only)"])
        bridge_cross = clean(row["Bridge Action (Cross-Domain Path)"])
        bridge_auto = clean(row["Bridge Action (Automotive Path)"])
        why = clean(row["Why This Mapping Works"])

        for target_role in target_roles:
            # Deduplicate
            key = (source_profile.lower(), target_role.lower())
            if key in seen:
                continue
            seen.add(key)

            role_families = map_to_family(target_role)

            # Skip roles marked for removal
            if role_families == ["skip"]:
                print(f"  ⏭️  Skipping: {target_role}")
                continue

            entry = {
                "source_profile": source_profile,
                "target_role": target_role,
                "role_families": role_families,
                "transferability": transferability.lower(),
                "skills_to_learn": {
                    "both_paths": skills_both,
                    "automotive_path_only": skills_auto
                },
                "bridge_actions": {
                    "cross_domain_path": bridge_cross,
                    "automotive_path": bridge_auto
                },
                "why_this_works": why
            }
            mappings.append(entry)

    # Build final YAML
    output = {
        "metadata": {
            "version": "1.0",
            "source": "AI_Automotive_Transition_Enhanced.xlsx",
            "last_updated": "2026-05-08",
            "total_mappings": len(mappings),
            "scope": "v1 — will enrich after Day 18 course corpus"
        },
        "mappings": mappings
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        yaml.dump(
            output,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )

    print(f"\n✅ Written {len(mappings)} mappings to {OUTPUT_PATH}")

    # Summary
    families = Counter(
        f for m in mappings
        for f in m["role_families"]
    )
    print("\nBy role family (can belong to multiple):")
    for family, count in sorted(families.items()):
        print(f"  {family}: {count}")

    unclassified = [
        m["target_role"] for m in mappings
        if m["role_families"] == ["unclassified"]
    ]
    if unclassified:
        print(f"\n⚠️  Still unclassified ({len(unclassified)}):")
        for r in set(unclassified):
            print(f"  - {r}")
    else:
        print("\n✅ No unclassified roles")


if __name__ == "__main__":
    convert()