# Project Context Handoff Document
**Last updated**: Week 2, Day 8
**Purpose**: Paste this at the start of any new chat to restore 
full project context instantly.

---

## Project in one sentence
Building an AI-powered skills mapping and reskilling tool for German 
automotive engineers facing displacement — portfolio piece targeting 
AI TPM / AI Solutions Engineer / AI PM roles.

## Builder profile
- 20+ years automotive TPM, embedded SW background
- Python functional but slow from scratch — uses Claude Code as pair
- Based in Cologne, Germany
- ~30 hrs/week available

## Stack
- Python 3.14, Streamlit, Anthropic Claude API (claude-sonnet-4-6)
- ChromaDB (Week 2), HuggingFace Spaces (deployed Day 3)
- Git Bash on Windows, VS Code, virtual env at .venv/

## Live URLs
- App: https://huggingface.co/spaces/shabs-ch/automotive-reskill
- Repo: https://github.com/shabs-ch/automotive-reskill

## Current status
Week 2, Day 8 — job ads collection in progress

## Completed
- Day 1: Environment, GitHub repo, hello world Streamlit + Claude
- Day 2: Structured JSON skill extraction with subcategory grouping
- Day 3: Deployed to HuggingFace Spaces
- Day 4-5: 6 user interviews completed
- Day 6: Architecture diagram, corpus inventory
- Day 7: ESCO ingest script — 349 relevant skills extracted
- Day 8: Job ads collection in progress (src/ingest_jobs.py written)

## Key architecture decisions
- 7-screen linear flow: CV Input → Skills Profile → Role Matches 
  → Gap Analysis → Roadmap → BG Checker → CV Reframing
- Agent/Controller pattern (Week 5) calling 6 tools
- ChromaDB for job ads + courses (semantic search)
- YAML for skill ontology, automotive mappings, BG rules (direct lookup)
- BG Checker = pure rules engine, no Claude API
- Static job ads corpus (not live search) for eval reproducibility
- Bilingual CV reframing (EN + DE) — non-negotiable
- Portfolio projects in roadmap screen — non-negotiable

## Infrastructure layer components
- Claude API — Skills Extractor, Role Matcher, Gap Analysis, 
  Roadmap Generator, CV Updater
- Job Ads ChromaDB — Role Matcher, Roadmap Generator
- Courses ChromaDB — Roadmap Generator
- Skills Ontology.yaml — Role Matcher, Gap Analysis
- Automotive_to_AI_Mapping.yaml — Role Matcher, Gap Analysis, 
  Roadmap Generator
- BG_Info.yaml — BG Checker only

## User research findings (6 interviews)
Profiles: PMO Lead, Systems Requirements Lead, Technical PM, 
SW Requirements Lead, SW Test Validation Lead, SW Project Manager
Experience: 15-20 years automotive

Top 5 pain points:
1. Transferable skills invisible to tools and recruiters
2. AI role landscape opaque — don't know what fits them
3. Course overload — no personalised path
4. Bildungsgutschein friction — English courses not BG-funded
5. Rejection patterns invisible

Top 3 surprises:
1. Most (4/6) prefer to stay in automotive and upskill
2. Agentur für Arbeit doesn't recognise senior PMO roles
3. Currently employed engineers already anxious — second user segment

## User stories (6 total)
US1: Transferable skills mapped to target roles
US2: Role discovery — automotive-adjacent AND cross-domain equally
US3: Personalised realistic learning roadmap
US4: Bildungsgutschein navigation
US5: Bilingual CV reframing (EN + DE)
US6: Gap understanding — what's missing for target role

## Role families (corpus target: 10-15 ads each)
Automotive-Adjacent (Tier 1):
- edge_ai (Edge AI / Embedded AI Engineer)
- digital_twin (Digital Twin Engineer)
- industry40 (Industry 4.0 / Smart Factory AI)
- adas_validation (ADAS / Autonomous Validation)
- functional_safety (Functional Safety AI)
- mlops_auto (MLOps/ML Engineer at automotive companies)

Cross-Domain (Tier 2):
- mlops_engineer (MLOps Engineer)
- ml_engineer (ML Engineer)
- ai_pm (AI Product Manager)
- ai_pgm (AI Program Manager)
- ai_transformation (AI Transformation Lead)
- ml_test (ML Test / AI QA Engineer)
- ai_solutions (AI Solutions Engineer)

## Job ad template
TITLE:
COMPANY:
LOCATION:
DATE_COLLECTED:
SOURCE: stepstone.de / indeed.de
LANGUAGE: EN / DE
LANGUAGE_NOTE: translated to English for processing (if DE original)
ROLE_FAMILY:
DOMAIN: automotive_adjacent / cross_domain
EXPERIENCE_LEVEL: realistic / inflated

----

[full job description]


## Key prompt files
- prompts/extract_skills_v1.txt — CV skills extraction
  Uses subcategory grouping for technical_skills and domain_knowledge
  Persona: expert CV reviewer and career transition specialist

## Budget
- €300 hard cap total
- €50/month Anthropic API limit
- Claude Code + app both draw from same API credits

## Decisions log highlights
- Git Bash over PowerShell (Windows compatibility)
- claude-sonnet-4-6 as primary model
- YAML for ontology/mappings (not DB) — version controllable, 
  human readable, Claude can read directly
- ChromaDB for job ads + courses — semantic search needed
- Static corpus not live search — eval reproducibility
- No file upload v1 — text paste only
- data/ folder entirely gitignored — never commit CVs or job ads
- ESCO filter: keyword inclusion + exclusion list, 349 skills

## Files structure
src/
ingest_esco.py     — ESCO taxonomy ingest (349 skills)
ingest_jobs.py     — Job ads ingest (in progress)
prompts/
extract_skills_v1.txt
notes/
decisions.md
deployment.md
future.md
interview_script.md
user_interviews/   — 6 anonymized interview notes
user_research_synthesis.md
user_stories.md
product_spec.md
corpus_inventory.md
architecture_v1.png
context_handoff.md
data/
raw/esco/          — ESCO CSV files (gitignored)
raw/jobs/          — job ads (gitignored)
processed/         — ingest outputs (gitignored)
AI_Automotive_Transition_Enhanced.xlsx (gitignored)

## Immediate next steps
- Day 8: Complete job ads collection (target 150 total)
- Day 9: Embeddings + ChromaDB setup
- Day 10: Wire skills extractor → role matcher in UI
- Week 3: Skill ontology + gap analysis
- Week 4: Eval framework + roadmap generator
- Week 5: Agent layer + Bildungsgutschein checker

## Open questions
- Are cross-domain non-AI roles worth including in corpus? 
  (Currently: NO — dilutes AI focus)
- Automotive-adjacent role validation needed from follow-up 
  interviews (SDV/digital twin not explicitly named by users)
- English vs German UI toggle — currently English only

## Known limitations to document in Week 8
- v1 covers SW + test engineers only
- BG checker covers standard cases, not Reha/AsylbLG/Härtefall
- Static corpus goes stale — needs monthly refresh in v2
- Eval set at 15 cases — needs scaling to 50+ for confidence
- No file upload, no user accounts, no session saving

## Key reference documents
- notes/learnings.md — running engineering learnings log
- notes/decisions.md — architectural decisions log
- notes/user_research_synthesis.md — user research findings