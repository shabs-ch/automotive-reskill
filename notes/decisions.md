# Decisions Log

## Day 1

**Shell**: Using Git Bash over PowerShell — more consistent with Python/AI tutorials, avoids Windows syntax quirks.

**Virtual environment**: Using .venv in project root — isolates dependencies, required for clean HuggingFace deployment.

**Model**: Using claude-sonnet-4-6 — current Sonnet model, good balance of capability and cost for prototyping.

**API key management**: .env file with python-dotenv, explicit path loading via Path(__file__).parent — avoids working directory issues on Windows.

## Day 2

**Structured output**: Using JSON with subcategory grouping for technical_skills and domain_knowledge — flat lists lose too much signal. Nested objects match chat-quality output.

**Transferable skills**: Added cross-domain implicit skills to extraction. Key prompt insight: "implicit skills reusable in any cross-domain role" produces better output than vague "non-technical skills."

**Persona**: Expert CV reviewer persona in prompt raises quality ceiling — Claude behaves like a senior recruiter not a parser.

**JSON safety**: isinstance check on display handles cases where Claude returns flat list instead of grouped dict.