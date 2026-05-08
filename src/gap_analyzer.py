import json
import yaml
import anthropic
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DATA_DIR = Path(__file__).parent.parent / "data"
ONTOLOGY_PATH = DATA_DIR / "skill_ontology.yaml"
MAPPINGS_PATH = DATA_DIR / "automotive_to_ai_mappings.yaml"

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Load data ────────────────────────────────────────────────────
def load_ontology() -> dict:
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_mappings() -> list:
    with open(MAPPINGS_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["mappings"]

# ── Get relevant mappings ────────────────────────────────────────
def get_relevant_mappings(
    source_profile: str,
    role_family: str,
    mappings: list
) -> list:
    """Find mappings relevant to this user's profile and target role."""
    relevant = []
    source_lower = source_profile.lower()

    for m in mappings:
        # Match by role family
        if role_family not in m.get("role_families", []):
            continue

        # Match by source profile — fuzzy match on keywords
        m_source = m.get("source_profile", "").lower()
        if any(
            kw in source_lower or kw in m_source
            for kw in ["engineer", "manager", "architect", "lead"]
        ):
            relevant.append(m)

    return relevant[:5]  # top 5 most relevant

# ── Core gap analysis ────────────────────────────────────────────
def analyze_gap(
    skills_profile: dict,
    target_role_family: str,
    domain_preference: str = "both"
) -> dict:
    """
    Analyze skill gaps for a given profile and target role family.

    Args:
        skills_profile: extracted skills dict from skills extractor
        target_role_family: one of mlops_engineer, ml_engineer,
                           ml_test, ai_mngr
        domain_preference: automotive_adjacent, cross_domain, or both

    Returns:
        structured gap report dict
    """

    ontology = load_ontology()
    mappings = load_mappings()

    # Get role profile from ontology
    role_profile = ontology["role_families"].get(target_role_family, {})
    if not role_profile:
        return {"error": f"Role family {target_role_family} not found"}

    required_skills = role_profile.get("required_skills", [])
    preferred_skills = role_profile.get("preferred_skills", [])
    bridge_skills = role_profile.get("bridge_skills", [])
    transferable = role_profile.get("transferable_from_automotive", [])

    # Get automotive mappings relevant to this profile
    source_hint = _extract_source_hint(skills_profile)
    relevant_mappings = get_relevant_mappings(
        source_hint, target_role_family, mappings
    )

    # Build context for Claude
    skills_text = _format_skills_for_prompt(skills_profile)
    ontology_text = _format_ontology_for_prompt(
        required_skills, preferred_skills, transferable,
        domain_preference
    )
    mappings_text = _format_mappings_for_prompt(relevant_mappings)

    # Claude prompt
    prompt = f"""You are an expert career transition advisor for automotive engineers moving into AI roles.

Analyze the skill gap for this engineer targeting {target_role_family} roles.
Domain preference: {domain_preference}

ENGINEER'S CURRENT SKILLS:
{skills_text}

TARGET ROLE REQUIREMENTS (from ontology):
{ontology_text}

AUTOMOTIVE TO AI MAPPINGS (transferability context):
{mappings_text}

Analyze the gap and return ONLY a JSON object with exactly these fields:

{{
  "target_role_family": "{target_role_family}",
  "domain_preference": "{domain_preference}",
  "already_have": [
    {{
      "skill": "skill name",
      "relevance": "why this is directly valuable in the target role",
      "strength": "high/medium/low"
    }}
  ],
  "transfers_with_bridging": [
    {{
      "current_skill": "what they have",
      "target_skill": "what it maps to",
      "bridge_action": "specific step to bridge the gap",
      "effort": "1-2 weeks / 2-4 weeks / 1-2 months"
    }}
  ],
  "need_to_learn": [
    {{
      "skill": "skill name",
      "priority": "high/medium/low",
      "reason": "why this is needed"
    }}
  ],
  "recommended_first_steps": [
    "step 1",
    "step 2",
    "step 3",
    "step 4",
    "step 5"
  ],
  "overall_readiness": "strong/moderate/early",
  "readiness_summary": "2-3 sentence honest assessment"
}}

Rules:
- Return ONLY the JSON object. No explanation, no markdown, no code fences.
- Be specific — reference actual skills from the engineer's profile
- Be honest — don't inflate readiness
- already_have should highlight automotive skills that are genuinely 
  valuable in AI roles (make invisible skills visible)
- recommended_first_steps should be ordered by priority
- maximum 6 items in already_have, 5 in transfers_with_bridging, 
  6 in need_to_learn, 5 in recommended_first_steps
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        gap_report = json.loads(raw)
        gap_report["_tokens"] = {
            "input": message.usage.input_tokens,
            "output": message.usage.output_tokens,
            "cost_usd": (
                message.usage.input_tokens * 3 / 1_000_000 +
                message.usage.output_tokens * 15 / 1_000_000
            )
        }
        return gap_report
    except json.JSONDecodeError:
        return {"error": "Failed to parse gap analysis", "raw": raw}


# ── Helper functions ─────────────────────────────────────────────
def _extract_source_hint(skills_profile: dict) -> str:
    """Extract a hint about the user's background for mapping lookup."""
    domain = skills_profile.get("domain_knowledge", {})
    if isinstance(domain, dict):
        all_items = []
        for items in domain.values():
            all_items.extend(items)
        return " ".join(all_items[:5])
    elif isinstance(domain, list):
        return " ".join(domain[:5])
    return "engineer"

def _format_skills_for_prompt(skills_profile: dict) -> str:
    """Format extracted skills profile for prompt."""
    lines = []

    tech = skills_profile.get("technical_skills", {})
    if isinstance(tech, dict):
        for category, items in tech.items():
            lines.append(f"Technical ({category}): {', '.join(items)}")
    elif tech:
        lines.append(f"Technical: {', '.join(tech)}")

    domain = skills_profile.get("domain_knowledge", {})
    if isinstance(domain, dict):
        for category, items in domain.items():
            lines.append(f"Domain ({category}): {', '.join(items)}")
    elif domain:
        lines.append(f"Domain: {', '.join(domain)}")

    tools = skills_profile.get("tools", [])
    if tools:
        lines.append(f"Tools: {', '.join(tools)}")

    transferable = skills_profile.get("transferable_skills", [])
    if transferable:
        lines.append(f"Transferable: {', '.join(transferable[:5])}")

    years = skills_profile.get("years_experience_per_area", {})
    if years:
        exp = [f"{area}({y}yrs)" for area, y in years.items()]
        lines.append(f"Experience: {', '.join(exp)}")

    return "\n".join(lines)

def _format_ontology_for_prompt(
    required, preferred, transferable, domain_preference
) -> str:
    """Format ontology data for prompt."""
    lines = []
    lines.append(f"Required skills: {', '.join(required)}")
    lines.append(f"Preferred skills: {', '.join(preferred[:8])}")

    if domain_preference in ["automotive_adjacent", "both"]:
        trans_items = [
            f"{t['source']} → {t['target']} ({t['transferability']})"
            for t in transferable[:6]
        ]
        lines.append(
            f"Known automotive transfers:\n  " +
            "\n  ".join(trans_items)
        )

    return "\n".join(lines)

def _format_mappings_for_prompt(mappings: list) -> str:
    """Format automotive mappings for prompt."""
    if not mappings:
        return "No specific mappings found for this profile."

    lines = []
    for m in mappings:
        skills = m.get("skills_to_learn", {})
        both = skills.get("both_paths", [])[:4]
        why = m.get("why_this_works", "")
        lines.append(
            f"- {m['source_profile']} → {m['target_role']}: "
            f"learn {', '.join(both)}. {why}"
        )

    return "\n".join(lines)


# ── Test run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test with a sample automotive engineer profile
    test_profile = {
        "technical_skills": {
            "Testing & Validation": [
                "HIL testing", "SIL testing", "requirements-based testing"
            ],
            "Automotive Tools": [
                "dSPACE", "CANoe", "DOORS"
            ]
        },
        "domain_knowledge": {
            "Automotive Testing": [
                "functional safety", "ISO 26262", "ASPICE",
                "defect tracking"
            ]
        },
        "tools": ["dSPACE", "CANoe", "MATLAB", "DOORS"],
        "transferable_skills": [
            "Requirements-based test case design",
            "Root cause analysis",
            "Cross-functional collaboration"
        ],
        "years_experience_per_area": {
            "automotive testing": 12,
            "HIL/SIL": 8
        }
    }

    print("Running gap analysis...")
    print("Profile: Test/Validation Engineer → ml_test")
    print("Domain: automotive_adjacent\n")

    result = analyze_gap(
        skills_profile=test_profile,
        target_role_family="ml_test",
        domain_preference="automotive_adjacent"
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        if "raw" in result:
            print(f"Raw response:\n{result['raw'][:500]}")
    else:
        print("✅ ALREADY HAVE:")
        for item in result.get("already_have", []):
            print(f"  • {item['skill']} ({item['strength']}) — {item['relevance']}")

        print("\n↗️  TRANSFERS WITH BRIDGING:")
        for item in result.get("transfers_with_bridging", []):
            print(f"  • {item['current_skill']} → {item['target_skill']}")
            print(f"    Bridge: {item['bridge_action']} ({item['effort']})")

        print("\n⬆️  NEED TO LEARN:")
        for item in result.get("need_to_learn", []):
            print(f"  • {item['skill']} [{item['priority']}] — {item['reason']}")

        print("\n🌉 RECOMMENDED FIRST STEPS:")
        for i, step in enumerate(result.get("recommended_first_steps", []), 1):
            print(f"  {i}. {step}")

        print(f"\n📊 OVERALL READINESS: {result.get('overall_readiness', 'N/A')}")
        print(f"   {result.get('readiness_summary', '')}")

        tokens = result.get("_tokens", {})
        print(f"\n💰 Cost: ${tokens.get('cost_usd', 0):.4f}")