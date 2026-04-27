import streamlit as st
import anthropic
import os
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

st.title("Automotive Reskill — Skill Extractor")
st.write("Paste any CV or work experience text below.")

user_input = st.text_area("Your text", height=200)

if st.button("Extract Skills"):
    if not user_input.strip():
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Analysing..."):
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"Extract exactly 3 key technical skills from this CV text. Be specific. Return them as a numbered list.\n\n{user_input}"
                    }
                ]
            )
            st.subheader("Top 3 Skills")
            st.write(message.content[0].text)

            st.caption(f"Tokens used: {message.usage.input_tokens} in / {message.usage.output_tokens} out")