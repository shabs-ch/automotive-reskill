import json
import anthropic
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

ROLE_FAMILY_DESCRIPTIONS = {
    "mlops_engineer": """
        Builds and maintains ML pipelines, deployment infrastructure,
        and monitoring systems. Requires: Python, Kubernetes, Docker,
        CI/CD, cloud platforms, model monitoring. Suits engineers with
        systems integration, DevOps, or infrastructure background.
    """,
    "ml_engineer": """
        Builds and trains ML models. Requires: Python, PyTorch/TensorFlow,
        ML fundamentals, C++. Suits engineers with embedded SW, signal
        processing, computer vision, or data science background.
    """,
    "ml_test": """
        Tests and validates ML systems. Requires: Python, test automation,
        simulation, ML evaluation metrics. Suits test/validation engineers
        with HIL/SIL, ISO 26262, scenario-based testing background.
    """,
    "ai_mngr": """
        Leads AI programs, products, and transformation initiatives.
        Requires: stakeholder management, business/technical translation,
        change management, agile delivery. Suits TPMs, PMO leads,
        program managers, product managers with domain expertise.
    """
}

def classify_profile(skills_profile: dict) -> list[dict]:
    """
    Classify a skills profile into ranked role families.

    Returns:
        List of dicts ordered by fit score:
        [{"family": "ai_mngr", "score": 0.9, "rationale": "..."}]
    """

    # Format profile for prompt
    lines = []

    tech = skills_profile.get("technical_skills", {})
    if isinstance(tech, dict):
        for cat, items in tech.items():
            lines.append(f"Technical ({cat}): {', '.join(items)}")
    elif tech:
        lines.append(f"Technical: {', '.join(tech)}")

    domain = skills_profile.get("domain_knowledge", {})
    if isinstance(domain, dict):
        for cat, items in domain.items():
            lines.append(f"Domain ({cat}): {', '.join(items)}")
    elif domain:
        lines.append(f"Domain: {', '.join(domain)}")

    tools = skills_profile.get("tools", [])
    if tools:
        lines.append(f"Tools: {', '.join(tools)}")

    transferable = skills_profile.get("transferable_skills", [])
    if transferable:
        lines.append(f"Transferable: {', '.join(transferable[:6])}")

    years = skills_profile.get("years_experience_per_area", {})
    if years:
        total = sum(years.values()) if years else 0
        exp = [f"{area}({y}yrs)" for area, y in years.items()]
        lines.append(f"Experience: {', '.join(exp)}")
        lines.append(f"Total experience: approximately {total} years")

    profile_text = "\n".join(lines)

    # Format role family descriptions
    families_text = "\n\n".join([
        f"{family}:\n{desc.strip()}"
        for family, desc in ROLE_FAMILY_DESCRIPTIONS.items()
    ])

    prompt = f"""You are a career transition advisor for automotive engineers moving into AI roles.

Classify this engineer's profile into the most suitable AI role families.

IMPORTANT CALIBRATION RULES:
- ai_mngr requires demonstrated leadership experience — managing teams, 
  owning programs, stakeholder management at senior level. 
  Junior profiles (<5 years total experience) should score BELOW 0.5 
  for ai_mngr regardless of transferable skills.
- ml_engineer requires hands-on technical depth — Python, ML frameworks,
  or strong embedded/signal processing background.
- ml_test requires testing/validation background — HIL/SIL, test automation,
  or quality engineering experience.
- mlops_engineer requires infrastructure/DevOps/cloud background —
  CI/CD pipelines, Docker, Kubernetes, or cloud platforms are strong 
  signals. Embedded SW engineers with CI/CD experience should score 
  higher here than pure coding profiles without infrastructure exposure.
- Be honest about junior profiles — low scores across all families 
  is a valid and correct output if the profile is early career.
- ISO 26262 and ASPICE knowledge in an embedded SW or architecture 
  context signals ml_engineer or mlops_engineer — NOT ai_mngr or ml_test.
  Only classify as ai_mngr if there is explicit program/product 
  management experience. Only classify as ml_test if there is explicit 
  test/validation engineering experience.
- C++ and embedded C are strong ml_engineer signals — prioritise 
  these over soft signals like process knowledge.
- Software architects and systems engineers with cloud, Docker, 
  or CI/CD exposure should score higher for mlops_engineer — 
  their architecture background maps well to ML platform design.
- MBSE, SysML, and system architecture are NOT ml_test signals —
  they map to ml_engineer or mlops_engineer.
  
ENGINEER PROFILE:
{profile_text}

AVAILABLE ROLE FAMILIES:
{families_text}

Return ONLY a JSON array ranking ALL four role families by fit.
Order from best fit to worst fit.

[
  {{
    "family": "role_family_name",
    "score": 0.0 to 1.0,
    "rationale": "one sentence why this fits or doesn't fit"
  }}
]

Rules:
- Include ALL four families in the response
- Score reflects genuine fit — be honest, don't inflate
- Score above 0.6 = realistic target
- Score below 0.4 = poor fit
- Return ONLY the JSON array, no explanation, no markdown
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text

    try:
        classifications = json.loads(raw)
        return classifications
    except json.JSONDecodeError:
        # Fallback — return equal scores if parsing fails
        return [
            {"family": f, "score": 0.5, "rationale": "Classification failed"}
            for f in ROLE_FAMILY_DESCRIPTIONS.keys()
        ]


if __name__ == "__main__":
    # Test with TPM profile
    test_profile = {
        "technical_skills": {
            "Automotive Systems": [
                "ADAS", "EPS", "steer-by-wire", "embedded software"
            ]
        },
        "domain_knowledge": {
            "Program Management": [
                "technical program management", "agile delivery",
                "cross-functional leadership", "OEM relationships"
            ]
        },
        "tools": ["MATLAB", "dSPACE", "Vector tools", "Python"],
        "transferable_skills": [
            "Cross-functional program leadership across 3 sites",
            "Stakeholder management from shop floor to C-suite",
            "Change management and process redesign",
            "Business development and customer engagement",
            "Coaching and team development"
        ],
        "years_experience_per_area": {
            "program management": 15,
            "ADAS delivery": 8
        }
    }

    print("Classifying TPM profile...\n")
    results = classify_profile(test_profile)

    for r in results:
        bar = "█" * int(r["score"] * 10)
        print(f"{r['family']:<20} {r['score']:.2f} {bar}")
        print(f"  {r['rationale']}")
        print()