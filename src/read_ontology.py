import yaml
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
ONTOLOGY_PATH = DATA_DIR / "skill_ontology.yaml"

def load_ontology() -> dict:
    """Load the skill ontology from YAML."""
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_role_families() -> list[str]:
    """Return list of available role family names."""
    ontology = load_ontology()
    return list(ontology["role_families"].keys())

def get_role_profile(role_family: str) -> dict:
    """Return full profile for a specific role family."""
    ontology = load_ontology()
    return ontology["role_families"].get(role_family, {})

def get_required_skills(role_family: str) -> list[str]:
    """Return required skills for a role family."""
    profile = get_role_profile(role_family)
    return profile.get("required_skills", [])

def get_bridge_skills(role_family: str) -> list[str]:
    """Return bridge skills (what to learn first) for a role family."""
    profile = get_role_profile(role_family)
    return profile.get("bridge_skills", [])

def get_transferable_skills(role_family: str) -> list[dict]:
    """Return transferable skills from automotive for a role family."""
    profile = get_role_profile(role_family)
    return profile.get("transferable_from_automotive", [])

if __name__ == "__main__":
    print("── Role families ──")
    for family in get_role_families():
        print(f"  {family}")

    print("\n── Required skills: mlops_engineer ──")
    for skill in get_required_skills("mlops_engineer"):
        print(f"  • {skill}")

    print("\n── Bridge skills: ml_test ──")
    for skill in get_bridge_skills("ml_test"):
        print(f"  • {skill}")

    print("\n── Transferable skills: ai_mngr ──")
    for t in get_transferable_skills("ai_mngr"):
        print(f"  • {t['source']} → {t['target']} ({t['transferability']})")