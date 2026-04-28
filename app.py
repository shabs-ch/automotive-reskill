import streamlit as st
import anthropic
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PROMPT_PATH = Path(__file__).parent / "prompts" / "extract_skills_v1.txt"
PROMPT_TEMPLATE = PROMPT_PATH.read_text(encoding="utf-8")

st.title("Automotive Reskill — Skills Extractor")
st.write("Paste your CV or work experience text below.")

user_input = st.text_area("Your CV text", height=250)

if st.button("Extract Skills"):
    if not user_input.strip():
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Analysing..."):
            prompt = PROMPT_TEMPLATE.replace("{cv_text}", user_input)

            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            raw = message.content[0].text

            try:
                skills = json.loads(raw)

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

                st.subheader("Tools")
                tools = skills.get("tools", [])
                if tools:
                    for s in tools:
                        st.markdown(f"- {s}")
                else:
                    st.caption("No tools identified.")

                st.subheader("Transferable Skills")
                transferable = skills.get("transferable_skills", [])
                if transferable:
                    for s in transferable:
                        st.markdown(f"- {s}")
                else:
                    st.caption("No transferable skills identified.")

                st.subheader("Years of Experience")
                years = skills.get("years_experience_per_area", {})
                if years:
                    for area, y in years.items():
                        st.markdown(f"- {area}: {y} years")
                else:
                    st.caption("No experience dates found.")

                st.divider()
                input_tokens = message.usage.input_tokens
                output_tokens = message.usage.output_tokens
                cost_usd = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)
                st.caption(f"Tokens: {input_tokens} in / {output_tokens} out — Est. cost: ${cost_usd:.4f}")

            except json.JSONDecodeError:
                st.error("Claude returned malformed JSON. Raw response below:")
                st.code(raw)