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

## Day 3

**HuggingFace deployment**: Streamlit Spaces uses port 8501 by default — 
never override port in config.toml. Only set headless=true, 
enableCORS=false, gatherUsageStats=false.

**Secret management**: ANTHROPIC_API_KEY stored as HF Space secret — 
never in code or committed files.

**Two remotes**: origin (GitHub) for backup/portfolio, 
space (HuggingFace) for deployment. Push to both after every 
significant change.


## Weekend — Week 1

**User story scope**: Added US6 (Gap understanding) based on interview 
finding that rejection patterns are invisible to users. Directly maps 
to Week 3 gap analysis module.

**Role discovery framing**: US2 updated to cover both automotive-adjacent 
and cross-domain roles equally. Automotive-adjacent (SDV, digital twin, 
Industry 4.0) not explicitly named by users — treat as hypothesis until 
confirmed in follow-up interviews.

**Product flow**: 7-screen linear flow defined. BG checker uses pure 
rules engine — no LLM. All other screens use Claude.

**CV reframing**: bilingual output non-negotiable — English + German 
both required. Users applying to both German market and international 
roles.

**Portfolio projects**: added to roadmap screen (Screen 5) as 
non-negotiable. Personalised to target role and user's domain background.

**v1 scope boundary**: no file upload, no user accounts, no session 
saving, no Turkish UI, no values alignment feature — all deferred to 
future.md.

cat >> notes/decisions.md << 'EOF'

## Day 7

**ESCO ingest**: Downloaded ESCO v1.2.0 CSV (English). Filtered 13,960 
skills to 1,255 relevant using keyword matching. Filter is broad — 
some noise (e.g. "cleaning industry safety") expected. Will tighten 
during ontology building on Day 11.

**Processed outputs**: Saved to data/processed/ (gitignored).
Scripts saved to src/ (committed).

**Files used**: skills_en.csv, skillGroups_en.csv, occupations_en.csv,
occupationSkillRelations_en.csv, digitalSkillsCollection_en.csv
EOF
**ESCO filter refinement**: Tightened keyword list (specific phrases 
over single words) + added exclusion list for irrelevant domains 
(food, hospitality, agriculture etc.). Final count: 349 skills. 
Two-pass filter pattern: include if relevant AND exclude if noisy.
