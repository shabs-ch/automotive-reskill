import streamlit as st
import anthropic
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from src.role_matcher import match_roles

load_dotenv(Path(__file__).parent / ".env")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PROMPT_PATH = Path(__file__).parent / "prompts" / "extract_skills_v1.txt"
PROMPT_TEMPLATE = PROMPT_PATH.read_text(encoding="utf-8")

    # Map role_family display names
family_labels = {
    "mlops_engineer": "MLOps Engineer",
    "ml_engineer": "ML Engineer",
    "ml_test": "ML Test Engineer",
    "ai_mngr": "AI Manager / Product Manager"
}

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Automotive Reskill",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Automotive Reskill")
st.caption("AI-powered career transition tool for automotive engineers")

# ── Session state ────────────────────────────────────────────────
if "skills" not in st.session_state:
    st.session_state.skills = None
if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0.0

# ── Screen 1: CV Input ───────────────────────────────────────────
st.header("Step 1 — Your Profile")
user_input = st.text_area(
    "Paste your CV or work experience text below",
    height=250,
    placeholder="Paste your CV text here..."
)

domain_filter = st.selectbox(
    "Role preference",
    options=["Both", "Automotive-adjacent roles", "Cross-domain AI roles"],
    index=0
)

domain_map = {
    "Both": None,
    "Automotive-adjacent roles": "automotive_adjacent",
    "Cross-domain AI roles": "cross_domain"
}

if st.button("Analyse My Profile", type="primary"):
    if not user_input.strip():
        st.warning("Please paste some CV text first.")
    else:
        with st.spinner("Extracting skills..."):
            prompt = PROMPT_TEMPLATE.replace("{cv_text}", user_input)
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = message.content[0].text

            # Track cost
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            cost = (input_tokens * 3 / 1_000_000) + \
                   (output_tokens * 15 / 1_000_000)
            st.session_state.total_cost += cost

            try:
                st.session_state.skills = json.loads(raw)
            except json.JSONDecodeError:
                st.error("Failed to parse skills. Raw response:")
                st.code(raw)
                st.stop()

# ── Screen 2: Skills Profile ─────────────────────────────────────
if st.session_state.skills:
    skills = st.session_state.skills

    st.divider()
    st.header("Step 2 — Your Skills Profile")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Technical Skills")
        tech = skills.get("technical_skills", {})
        if tech:
            if isinstance(tech, dict):
                for category, items in tech.items():
                    st.markdown(f"**{category}**")
                    for s in items:
                        st.markdown(f"- {s}")
            else:
                for s in tech:
                    st.markdown(f"- {s}")
        else:
            st.caption("No technical skills identified.")

        st.subheader("Tools")
        tools = skills.get("tools", [])
        if tools:
            for s in tools:
                st.markdown(f"- {s}")
        else:
            st.caption("No tools identified.")

    with col2:
        st.subheader("Domain Knowledge")
        domain = skills.get("domain_knowledge", {})
        if domain:
            if isinstance(domain, dict):
                for category, items in domain.items():
                    st.markdown(f"**{category}**")
                    for s in items:
                        st.markdown(f"- {s}")
            else:
                for s in domain:
                    st.markdown(f"- {s}")
        else:
            st.caption("No domain knowledge identified.")

        st.subheader("Years of Experience")
        years = skills.get("years_experience_per_area", {})
        if years:
            for area, y in years.items():
                st.markdown(f"- {area}: {y} years")
        else:
            st.caption("No experience dates found.")

    st.subheader("Transferable Skills")
    transferable = skills.get("transferable_skills", [])
    if transferable:
        for s in transferable:
            st.markdown(f"- {s}")
    else:
        st.caption("No transferable skills identified.")

    # ── Screen 3: Role Matches ───────────────────────────────────
    st.divider()
    st.header("Step 3 — Matching Roles")

    with st.spinner("Finding matching roles..."):
        selected_domain = domain_map[domain_filter]
        matches = match_roles(
            skills_profile=skills,
            n_results=5,
            domain_filter=selected_domain
        )

    if matches:
        # Check if any match has low confidence
        if matches and matches[0].get("family_fit_score", 1.0) < 0.6:
            st.warning(
            "⚠️ Your profile doesn't strongly match any single AI "
            "role family yet. We're showing one example from each "
            "direction so you can explore which path interests you "
            "most — then use gap analysis to understand what "
            "upskilling each path requires."
        )

        for i, match in enumerate(matches):
            with st.expander(
                f"#{i+1} — {match['title']} at {match['company']}",
                expanded=(i == 0)
            ):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Role Family", family_labels.get(
                        match["role_family"], match["role_family"]
                    ))
                with col2:
                    st.metric("Domain", match["domain"].replace("_", " ").title())
                with col3:
                    st.metric("Experience Level", match["experience_level"].title())
                with col4:
                    fit_pct = int(match.get("family_fit_score", 0) * 100)
                    st.metric("Profile Fit", f"{fit_pct}%",
                        help="How well your overall profile matches "
                             "this role family — based on your skills, "
                             "experience, and background."
                    )

                # Qualitative match label
                fit_score = match.get("family_fit_score", 0)
                semantic_score = match.get("match_score", 0)

                if fit_score >= 0.8:
                    fit_label = "🟢 Strong Match"
                elif fit_score >= 0.6:
                    fit_label = "🟡 Good Match"
                else:
                    fit_label = "🔵 Possible Match"

                st.caption(
                    f"{fit_label} — "
                    f"{match.get('family_rationale', '')}"
                )

                st.caption(f"📍 {match['location']}")

                if match["experience_level"] == "inflated":
                    st.warning(
                        "⚠️ This role's requirements appear inflated — "
                        "candidates with strong domain background are "
                        "regularly hired without meeting all listed "
                        "requirements."
                    )

                with st.expander("See job requirements snippet"):
                    st.text(match["snippet"])
    else:
        st.info("No matches found. Try changing your role preference filter.")

    # ── Screen 4: Gap Analysis ───────────────────────────────────
    st.divider()
    st.header("Step 4 — Gap Analysis")

    # Extract unique role families from matched results
    matched_families = list(dict.fromkeys(
        m["role_family"] for m in matches
        if m["role_family"] in family_labels
    ))

    # Fallback to all families if none found
    if not matched_families:
        matched_families = list(family_labels.keys())

    selected_family = st.selectbox(
        "Select your target role family for gap analysis:",
        options=matched_families,
        format_func=lambda x: family_labels[x]
    )

    if st.button("Analyse My Gaps", type="primary"):
        with st.spinner(
            "Analysing your skill gaps — comparing your profile "
            "against role requirements and automotive mappings. "
            "This takes 20-30 seconds..."
        ):
            from src.gap_analyzer import analyze_gap

            gap_result = analyze_gap(
                skills_profile=skills,
                target_role_family=selected_family,
                domain_preference=domain_map[domain_filter] or "both"
            )

            if "error" in gap_result:
                st.error(f"Gap analysis failed: {gap_result['error']}")
            else:
                # Already Have
                st.subheader("✅ You Already Have")
                st.caption(
                    "Skills from your automotive background that are "
                    "directly valued in this AI role — these are your "
                    "strengths. Highlight them in applications."
                )
                for item in gap_result.get("already_have", []):
                    with st.expander(
                        f"{item['skill']} — {item['strength'].upper()}"
                    ):
                        st.write(item["relevance"])

                # Transfers With Bridging
                st.subheader("↗️ Transfers With Bridging")
                st.caption(
                    "Skills you already have that map to AI role "
                    "requirements with a specific learning step to "
                    "activate the connection. Foundation exists — "
                    "just needs targeted upskilling."
                )
                for item in gap_result.get("transfers_with_bridging", []):
                    with st.expander(
                        f"{item['current_skill']} → {item['target_skill']} "
                        f"({item['effort']})"
                    ):
                        st.write(f"**Bridge action**: {item['bridge_action']}")

                # Need To Learn
                st.subheader("⬆️ You Need To Learn")
                st.caption(
                    "Skills genuinely absent from your profile that "
                    "this role requires. These are your real gaps — "
                    "not covered by any existing skill you have."
                )
                for item in gap_result.get("need_to_learn", []):
                    priority_color = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }.get(item["priority"], "⚪")
                    st.markdown(
                        f"{priority_color} **{item['skill']}** "
                        f"— {item['reason']}"
                    )

                # First Steps
                st.subheader("🌉 Recommended First Steps")
                st.caption(
                    "A prioritised action plan: activate your transfers "
                    "first (quickest wins), then close genuine gaps. "
                    "Completing these steps makes you competitive for "
                    "this role."
                )
                for i, step in enumerate(
                    gap_result.get("recommended_first_steps", []), 1
                ):
                    st.markdown(f"**{i}.** {step}")

                # Readiness
                readiness = gap_result.get("overall_readiness", "")
                readiness_color = {
                    "strong": "🟢",
                    "moderate": "🟡",
                    "early": "🔴"
                }.get(readiness, "⚪")

                st.divider()
                st.subheader(
                    f"📊 Overall Readiness: "
                    f"{readiness_color} {readiness.upper()}"
                )
                st.info(gap_result.get("readiness_summary", ""))

                # Cost tracking
                tokens = gap_result.get("_tokens", {})
                st.session_state.total_cost += tokens.get("cost_usd", 0)

    # ── Cost tracker ─────────────────────────────────────────────
    st.divider()
    st.caption(
        f"💰 Total cost this session: "
        f"${st.session_state.total_cost:.4f}"
    )