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
        for i, match in enumerate(matches):
            with st.expander(
                f"#{i+1} — {match['title']} at {match['company']} "
                f"(Score: {match['match_score']})",
                expanded=(i == 0)
            ):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Role Family", match["role_family"])
                with col2:
                    st.metric("Domain", match["domain"])
                with col3:
                    st.metric("Experience Level", match["experience_level"])

                st.caption(f"📍 {match['location']}")

                if match["experience_level"] == "inflated":
                    st.warning(
                        "⚠️ This role's requirements appear inflated — "
                        "candidates with strong domain background are "
                        "regularly hired without meeting all listed "
                        "requirements."
                    )

                st.markdown("**Why this matches — key requirements:**")
                st.text(match["snippet"])

    else:
        st.info("No matches found. Try changing your role preference filter.")

    # ── Cost tracker ─────────────────────────────────────────────
    st.divider()
    st.caption(
        f"💰 Total cost this session: "
        f"${st.session_state.total_cost:.4f}"
    )