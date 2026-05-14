import json
import yaml
import anthropic
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DATA_DIR = Path(__file__).parent.parent / "data"
COURSES_PATH = DATA_DIR / "courses.yaml"

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Load courses ─────────────────────────────────────────────────
def load_courses() -> list:
    with open(COURSES_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["courses"]

# ── Retrieve relevant courses ────────────────────────────────────
def retrieve_relevant_courses(
    gap_report: dict,
    target_role_family: str,
    domain_preference: str,
    max_courses: int = 20
) -> list:
    """
    Retrieve courses relevant to the user's skill gaps.
    This is the RAG retrieval step — no embeddings needed here
    because we can filter by role_family and skill keywords directly.
    """
    all_courses = load_courses()

    # Filter by role family
    family_courses = [
        c for c in all_courses
        if target_role_family in c.get("role_families", [])
    ]

    # Extract skills to learn from gap report
    need_to_learn = [
        item["skill"].lower()
        for item in gap_report.get("need_to_learn", [])
    ]
    transfers = [
        item["target_skill"].lower()
        for item in gap_report.get("transfers_with_bridging", [])
    ]
    all_gaps = need_to_learn + transfers

    # Score each course by relevance to gaps
    def relevance_score(course):
        score = 0
        course_skills = [
            str(s).lower() for s in course.get("target_skills", [])
            if s is not None
        ]
        course_text = " ".join(course_skills).lower()

        # Skill match bonus
        for gap in all_gaps:
            gap_words = set(gap.split())
            if any(
                len(gap_words & set(s.split())) >= 1
                for s in course_skills
            ):
                score += 2

        # Language preference bonus
        lang = course.get("language", "EN")
        if domain_preference == "automotive_adjacent" and lang in ["DE", "DE/EN"]:
            score += 1
        elif domain_preference == "cross_domain" and lang in ["EN", "DE/EN"]:
            score += 1

        # BG eligible bonus
        if course.get("bildungsgutschein_eligible") == "yes":
            score += 3

        # Level preference — beginners first
        level = course.get("level", "intermediate")
        if level == "beginner":
            score += 1

        return score

    # Sort by relevance
    scored = sorted(
        family_courses,
        key=relevance_score,
        reverse=True
    )

    return scored[:max_courses]


# ── Generate roadmap ─────────────────────────────────────────────
def generate_roadmap(
    skills_profile: dict,
    gap_report: dict,
    target_role_family: str,
    domain_preference: str = "both"
) -> dict:
    """
    Generate a personalised learning roadmap grounded in real courses.

    Args:
        skills_profile: extracted skills from CV
        gap_report: output from gap_analyzer
        target_role_family: target role family
        domain_preference: automotive_adjacent / cross_domain / both

    Returns:
        structured roadmap dict with cited courses
    """

    # ── Step 1: Retrieve relevant courses (RAG retrieval) ─────────
    relevant_courses = retrieve_relevant_courses(
        gap_report, target_role_family, domain_preference
    )

    if not relevant_courses:
        return {"error": "No relevant courses found for this profile"}

    # ── Step 2: Format courses for prompt (RAG augmentation) ──────
    courses_text = _format_courses_for_prompt(relevant_courses)

    # ── Step 3: Format gap report for prompt ──────────────────────
    gaps_text = _format_gaps_for_prompt(gap_report)

    # ── Step 4: Format profile summary ───────────────────────────
    profile_text = _format_profile_summary(skills_profile)

    # ── Step 5: Generate roadmap (RAG generation) ─────────────────
    prompt = f"""You are an expert career transition advisor for automotive engineers moving into AI roles.

Generate a personalised learning roadmap for this engineer.

ENGINEER PROFILE SUMMARY:
{profile_text}

SKILL GAPS TO CLOSE:
{gaps_text}

TARGET ROLE: {target_role_family}
DOMAIN PREFERENCE: {domain_preference}

AVAILABLE COURSES (you may ONLY recommend courses from this list):
{courses_text}

Generate a month-by-month learning roadmap. Return ONLY a JSON object:

{{
  "target_role_family": "{target_role_family}",
  "domain_preference": "{domain_preference}",
  "total_duration_months": 0,
  "estimated_cost_eur": "€X - €Y range",
  "monthly_plan": [
    {{
      "month": "Month 1",
      "theme": "short theme title",
      "courses": [
        {{
          "name": "exact course name from the list above",
          "provider": "exact provider from the list above",
          "url": "exact URL from the list above",
          "duration_weeks": 0,
          "cost_eur": 0,
          "cost_audit_eur": 0,
          "bildungsgutschein_eligible": "yes/no/unknown",
          "language": "DE/EN/DE/EN",
          "why_recommended": "one sentence specific to this engineer",
          "priority": "essential/recommended/optional"
        }}
      ],
      "milestone": "what the engineer can do after this month"
    }}
  ],
  "portfolio_project": {{
    "title": "project title",
    "description": "2-3 sentences describing the project",
    "skills_demonstrated": ["skill1", "skill2"],
    "automotive_connection": "how it connects to automotive background"
  }},
  "bg_eligible_courses": ["course name 1", "course name 2"],
  "total_courses_recommended": 0,
  "roadmap_summary": "2-3 sentence honest overview"
}}

CRITICAL RULES:
- Recommend ONLY courses that appear in the AVAILABLE COURSES list above
- Copy course name, provider, and URL EXACTLY as they appear in the list
- Never invent or modify course details
- If no suitable course exists for a gap, say so in roadmap_summary
- Order months by priority — most critical gaps first
- Maximum 3 courses per month — don't overwhelm
- Portfolio project must connect to the engineer's automotive background
- Return ONLY the JSON. No explanation, no markdown, no code fences.
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text

    try:
        roadmap = json.loads(raw)
        roadmap["_tokens"] = {
            "input": message.usage.input_tokens,
            "output": message.usage.output_tokens,
            "cost_usd": (
                message.usage.input_tokens * 3 / 1_000_000 +
                message.usage.output_tokens * 15 / 1_000_000
            )
        }
        return roadmap
    except json.JSONDecodeError:
        return {"error": "Failed to parse roadmap", "raw": raw}


# ── Helper functions ─────────────────────────────────────────────
def _format_courses_for_prompt(courses: list) -> str:
    """Format retrieved courses for the prompt."""
    lines = []
    for i, c in enumerate(courses, 1):
        bg = c.get("bildungsgutschein_eligible", "unknown")
        bg_tag = "✅ BG-eligible" if bg == "yes" else \
                 "❌ Not BG-eligible" if bg == "no" else \
                 "❓ BG unknown"
        cost = c.get("cost_eur")
        audit = c.get("cost_audit_eur")
        cost_str = f"€{cost}" if cost else "price unknown"
        if audit == 0:
            cost_str += " (free audit available)"
        elif audit:
            cost_str += f" (audit €{audit})"

        lines.append(
            f"{i}. {c['name']}\n"
            f"   Provider: {c.get('provider', 'Unknown')}\n"
            f"   URL: {c.get('url', 'N/A')}\n"
            f"   Duration: {c.get('duration_weeks', 'unknown')} weeks | "
            f"Language: {c.get('language', 'EN')} | "
            f"Level: {c.get('level', 'intermediate')}\n"
            f"   Cost: {cost_str} | {bg_tag}\n"
            f"   Skills: {', '.join(c.get('target_skills', [])[:5])}\n"
        )
    return "\n".join(lines)


def _format_gaps_for_prompt(gap_report: dict) -> str:
    """Format gap report for prompt."""
    lines = []

    need = gap_report.get("need_to_learn", [])
    if need:
        high = [i["skill"] for i in need if i.get("priority") == "high"]
        med = [i["skill"] for i in need if i.get("priority") == "medium"]
        if high:
            lines.append(f"High priority gaps: {', '.join(high)}")
        if med:
            lines.append(f"Medium priority gaps: {', '.join(med)}")

    transfers = gap_report.get("transfers_with_bridging", [])
    if transfers:
        bridge = [
            f"{t['current_skill']} → {t['target_skill']}"
            for t in transfers[:4]
        ]
        lines.append(f"Transfers needing bridging: {', '.join(bridge)}")

    bridge_skills = gap_report.get("recommended_first_steps", [])
    if bridge_skills:
        lines.append(
            f"Recommended first steps: "
            f"{'; '.join(bridge_skills[:3])}"
        )

    return "\n".join(lines)


def _format_profile_summary(skills_profile: dict) -> str:
    """Format a brief profile summary."""
    lines = []

    years = skills_profile.get("years_experience_per_area", {})
    if years:
        exp = [f"{area} ({y}yrs)" for area, y in years.items()]
        lines.append(f"Experience: {', '.join(exp)}")

    tools = skills_profile.get("tools", [])
    if tools:
        lines.append(f"Current tools: {', '.join(tools[:6])}")

    transferable = skills_profile.get("transferable_skills", [])
    if transferable:
        lines.append(
            f"Key strengths: {', '.join(transferable[:3])}"
        )

    return "\n".join(lines)


# ── Test run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test with TPM profile gap report
    test_profile = {
        "technical_skills": {
            "Program Management": ["agile delivery", "risk management"],
            "Technical": ["Python scripting basics", "MATLAB exposure"]
        },
        "domain_knowledge": {
            "Automotive": ["ADAS delivery", "OEM management", "ASPICE"]
        },
        "tools": ["JIRA", "Python", "MATLAB", "MS Project"],
        "transferable_skills": [
            "Cross-functional program leadership",
            "Stakeholder management shop floor to C-suite",
            "Change management and process redesign"
        ],
        "years_experience_per_area": {
            "program management": 20,
            "ADAS delivery": 8
        }
    }

    test_gap_report = {
        "need_to_learn": [
            {"skill": "AI and ML fundamentals", "priority": "high"},
            {"skill": "LLMs and GenAI tools", "priority": "high"},
            {"skill": "EU AI Act and governance", "priority": "medium"},
            {"skill": "Cloud and IT architecture", "priority": "medium"},
            {"skill": "Data platforms and analytics", "priority": "low"}
        ],
        "transfers_with_bridging": [
            {
                "current_skill": "ISO 26262 / ASPICE",
                "target_skill": "EU AI Act compliance"
            },
            {
                "current_skill": "Program management",
                "target_skill": "AI programme delivery"
            }
        ],
        "recommended_first_steps": [
            "Complete AI fundamentals course",
            "Study EU AI Act basics",
            "Learn LLM working knowledge"
        ]
    }

    print("Generating roadmap for TPM → ai_mngr...\n")

    result = generate_roadmap(
        skills_profile=test_profile,
        gap_report=test_gap_report,
        target_role_family="ai_mngr",
        domain_preference="automotive_adjacent"
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        if "raw" in result:
            print(f"Raw: {result['raw'][:300]}")
    else:
        print(f"Duration: {result.get('total_duration_months')} months")
        print(f"Cost estimate: {result.get('estimated_cost_eur')}")
        print(f"\nMonthly plan:")
        for month in result.get("monthly_plan", []):
            print(f"\n{month['month']} — {month['theme']}")
            for course in month.get("courses", []):
                bg = course.get("bildungsgutschein_eligible", "unknown")
                bg_tag = "✅" if bg == "yes" else \
                         "❌" if bg == "no" else "❓"
                print(f"  {bg_tag} {course['name']}")
                print(f"     {course['provider']}")
                print(f"     {course['why_recommended']}")
            print(f"  🎯 Milestone: {month['milestone']}")

        print(f"\n📁 Portfolio Project:")
        proj = result.get("portfolio_project", {})
        print(f"  {proj.get('title')}")
        print(f"  {proj.get('description')}")
        print(f"  Automotive connection: {proj.get('automotive_connection')}")

        print(f"\nBG-eligible courses: "
              f"{result.get('bg_eligible_courses', [])}")
        print(f"\nSummary: {result.get('roadmap_summary')}")

        tokens = result.get("_tokens", {})
        print(f"\n💰 Cost: ${tokens.get('cost_usd', 0):.4f}")