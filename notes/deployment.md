# Deployment Notes

## HuggingFace Spaces

**Live URL**: https://huggingface.co/spaces/shabs-ch/automotive-reskill

**Stack**: Streamlit SDK on HuggingFace Spaces (free tier)

**To deploy updates:**
1. Make changes locally
2. Test with `streamlit run app.py`
3. Commit: `git add . && git commit -m "your message"`
4. Push to GitHub: `git push origin main`
5. Push to HF: `git push space main`

**Critical config notes:**
- Never override port in `.streamlit/config.toml` — Streamlit Spaces uses 8501 by default
- API key stored as HF Space secret named `ANTHROPIC_API_KEY`
- `.streamlit/config.toml` must have `headless = true`

**Secret management:**
- Local: stored in `.env` file (gitignored)
- HuggingFace: stored in Space Settings → Variables and Secrets
- Never commit API keys to any repo