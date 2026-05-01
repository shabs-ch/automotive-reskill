import pandas as pd
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw" / "esco"
OUTPUT_DIR = DATA_DIR / "processed"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── 1. Load skills ──────────────────────────────────────────────
print("Loading skills...")
skills_df = pd.read_csv(RAW_DIR / "skills_en.csv", low_memory=False)

print(f"Total skills: {len(skills_df)}")
print(f"Skill types: {skills_df['skillType'].value_counts().to_dict()}")

# Keep only relevant columns
skills_df = skills_df[[
    "conceptUri",
    "skillType",
    "preferredLabel",
    "description"
]].copy()

# Drop rows with no label
skills_df = skills_df.dropna(subset=["preferredLabel"])
print(f"Skills after cleaning: {len(skills_df)}")

# ── 2. Load skill groups ────────────────────────────────────────
print("\nLoading skill groups...")
groups_df = pd.read_csv(RAW_DIR / "skillGroups_en.csv", low_memory=False)
groups_df = groups_df[["conceptUri", "preferredLabel", "code"]].copy()
groups_df = groups_df.dropna(subset=["preferredLabel"])
print(f"Skill groups: {len(groups_df)}")

# ── 3. Load occupations ─────────────────────────────────────────
print("\nLoading occupations...")
occ_df = pd.read_csv(RAW_DIR / "occupations_en.csv", low_memory=False)
occ_df = occ_df[[
    "conceptUri",
    "preferredLabel",
    "code",
    "description"
]].copy()
occ_df = occ_df.dropna(subset=["preferredLabel"])
print(f"Occupations: {len(occ_df)}")

# ── 4. Filter skills relevant to AI/tech/engineering ───────────
print("\nFiltering relevant skills...")

# Keywords relevant to automotive→AI transition
RELEVANT_KEYWORDS = [
    # Technical/AI
    "machine learning", "artificial intelligence", "python", "data analysis",
    "software", "programming", "algorithm", "neural", "deep learning",
    "computer vision", "natural language", "cloud", "devops", "mlops",
    # Automotive/Engineering
    "embedded", "automotive", "functional safety", "testing", "validation",
    "requirements", "systems engineering", "quality assurance", "simulation",
    "control systems", "autonomous",
    # Management/transferable
    "project management", "program management", "stakeholder management",
    "requirements engineering", "process improvement", "agile", "change management",
    "risk management", "leadership"
]
EXCLUDE_KEYWORDS = [
    "food", "cage", "ramp", "wild game", "cleaning", "railway",
    "catering", "livestock", "agricultural", "fishing", "mining",
    "hairdress", "beauty", "nursing", "dental", "veterinary",
    "hospitality", "hotel", "cooking", "baking", "textile"
]

def is_relevant(label):
    if pd.isna(label):
        return False
    label_lower = str(label).lower()
    # Must match at least one relevant keyword
    if not any(kw in label_lower for kw in RELEVANT_KEYWORDS):
        return False
    # Must not match any exclusion keyword
    if any(ex in label_lower for ex in EXCLUDE_KEYWORDS):
        return False
    return True

skills_filtered = skills_df[
    skills_df["preferredLabel"].apply(is_relevant)
].copy()

print(f"Relevant skills after filtering: {len(skills_filtered)}")

# ── 5. Save outputs ─────────────────────────────────────────────
print("\nSaving outputs...")

# Save filtered skills as JSON
skills_out = skills_filtered.to_dict(orient="records")
with open(OUTPUT_DIR / "esco_skills_filtered.json", "w", encoding="utf-8") as f:
    json.dump(skills_out, f, ensure_ascii=False, indent=2)

# Save all occupations as JSON
occ_out = occ_df.to_dict(orient="records")
with open(OUTPUT_DIR / "esco_occupations.json", "w", encoding="utf-8") as f:
    json.dump(occ_out, f, ensure_ascii=False, indent=2)

# Save skill groups as JSON
groups_out = groups_df.to_dict(orient="records")
with open(OUTPUT_DIR / "esco_skill_groups.json", "w", encoding="utf-8") as f:
    json.dump(groups_out, f, ensure_ascii=False, indent=2)

print(f"\n✅ Done. Outputs saved to {OUTPUT_DIR}")
print(f"   esco_skills_filtered.json  — {len(skills_filtered)} relevant skills")
print(f"   esco_occupations.json      — {len(occ_df)} occupations")
print(f"   esco_skill_groups.json     — {len(groups_df)} skill groups")

# ── 6. Quick verification query ─────────────────────────────────
print("\n── Sample query: skills containing 'machine learning' ──")
ml_skills = skills_filtered[
    skills_filtered["preferredLabel"].str.contains(
        "machine learning", case=False, na=False
    )
]
for _, row in ml_skills.head(5).iterrows():
    print(f"  • {row['preferredLabel']} ({row['skillType']})")

print("\n── Sample query: skills containing 'safety' ──")
safety_skills = skills_filtered[
    skills_filtered["preferredLabel"].str.contains(
        "safety", case=False, na=False
    )
]
for _, row in safety_skills.head(5).iterrows():
    print(f"  • {row['preferredLabel']} ({row['skillType']})")