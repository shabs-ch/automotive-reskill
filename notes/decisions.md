# Decisions Log

## Day 1

**Shell**: Using Git Bash over PowerShell — more consistent with Python/AI tutorials, avoids Windows syntax quirks.

**Virtual environment**: Using .venv in project root — isolates dependencies, required for clean HuggingFace deployment.

**Model**: Using claude-sonnet-4-6 — current Sonnet model, good balance of capability and cost for prototyping.

**API key management**: .env file with python-dotenv, explicit path loading via Path(__file__).parent — avoids working directory issues on Windows.

