# Engineering Learnings — Automotive Reskill Build

## AI Product Engineering

### LLM Behaviour
- LLMs return plausible text, not correct text. Without grounding 
  (RAG, ontology, rules), outputs hallucinate.
- Structured output (JSON) requires explicit prompt engineering. 
  Three techniques in order of reliability:
  1. Ask for JSON (~70% reliable)
  2. Show example JSON (~90%)
  3. Tool-use / strict schema (~99%)
- Persona in prompt sets quality ceiling. "Expert CV reviewer" 
  produces better output than "skills extraction assistant."
- JSON schema constrains what Claude can express — richer schema, 
  richer output. Flat list vs subcategory grouping produces 
  dramatically different quality.
- max_tokens truncation causes silent JSON parse failures — always 
  set max_tokens higher than you think you need.

### Prompt Engineering
- Chat Claude feels smarter than app Claude because chat is 
  interactive and adaptive. App Claude has one shot — prompt quality 
  is the ceiling.
- Compare chat output vs app output to find prompt gaps — fastest 
  debugging technique.
- Transferable skills prompt: "implicit skills reusable in any 
  cross-domain role" produces better output than "non-technical skills."
- Calibration rules in classifier prompt are essential — without them
  Claude is too generous with scores for junior profiles.
- Change ONE thing at a time when iterating prompts — otherwise you 
  can't know what caused the improvement.

### RAG Systems
- RAG = Retrieval + Augmented + Generation. Three distinct steps,
  each can fail independently.
- Embeddings find semantic similarity, not correctness. Narrow score
  range (0.64-0.69) means system can't differentiate good from poor 
  matches — requires metadata filtering on top.
- Corpus imbalance affects retrieval quality — 35 technical ads vs 
  15 management ads caused management roles to be underrepresented 
  in results.
- Static corpus + reproducible eval beats live search for v1 — 
  can't measure improvement if corpus changes every run.
- Multilingual model (BAAI/bge-m3) handles DE+EN in same vector 
  space — "Funktionale Sicherheit" lands near "Functional Safety."
- Extract signal sections before embedding — embedding full job ad 
  including boilerplate dilutes the semantic signal.

### Architecture Decisions
- Rules for deterministic logic (BG checker, eligibility), 
  LLM for ambiguous reasoning (gap analysis, CV reframing).
- Classification before retrieval is architecturally cleaner than 
  patching retrieval results — classifier → retriever pipeline.
- Lazy loading for heavy models (SentenceTransformer) — load once,
  reuse across requests. Critical for Streamlit performance.
- YAML over database for ontology at <500 entries — version 
  controllable, human readable, Claude can read directly in prompts.
- Modular architecture pays off — swapping naive semantic search for
  classifier+search required changing only role_matcher.py.

### Evaluation
- Testing with simplified profiles gives false confidence — always 
  test with real extracted output, not handcrafted fixtures.
- Bug found in production that wasn't found in unit test: classifier 
  scored junior profile 0.52 in standalone test but 0.72 in live app 
  because extracted profile was richer than test fixture.
- End-to-end testing is irreplaceable — component tests are necessary
  but not sufficient.
- Non-deterministic systems require measurement not intuition — 
  "looks good" is not an engineering standard.

---

## Data Engineering

### Corpus Design
- Quality over quantity — 60 curated job ads from right industries 
  beats 150 generic ads.
- Real market reality check: Industry 4.0, Digital Twin, Functional 
  Safety AI not findable as distinct job titles in target industries.
  Titles in conference talks ≠ titles in job postings.
- Job ad requirements are often inflated — "5 years ML experience" 
  appears in roles where 2 years + domain background suffices.
  Tagging experience_level: realistic/inflated adds signal.
- Domain split matters — automotive MLOps requires Terraform/IaC 
  ownership and ISO 26262 awareness; cross-domain MLOps does not.
  Same title, genuinely different role.
- International ads acceptable for skill extraction — skills are 
  universal, geography only matters for job recommendations.

### ESCO Limitations
- ESCO is weak on modern AI/ML skills — MLOps, RAG, transformer 
  architecture not in taxonomy. Good for transferable/engineering 
  foundation skills only.
- Two-pass filter works for corpus cleaning: include if relevant 
  AND exclude if noisy domain. Single-pass catches too much noise.

### Knowledge Engineering
- Domain expertise is the moat, not the model. Automotive→AI 
  mappings encode knowledge no model can derive independently.
- Ontology built from job ads corpus (not ESCO) for AI/ML skills —
  ESCO too slow to update for emerging roles.
- Skill ontology structure: required / preferred / transferable / 
  bridge — four categories serve different purposes in gap analysis.
- Bridge actions need real course data to be specific — placeholder
  bridge actions (Day 12) will be enriched after course corpus 
  built (Day 18).

---

## Python & Tooling

### Git
- .gitignore only prevents future commits — files already committed 
  remain tracked regardless of .gitignore.
- To untrack already-committed file: git rm --cached filename → 
  commit → push. Never git add . after git rm --cached.
- git add . is dangerous when data/ has content — always add 
  files explicitly by name.
- Three remotes pattern: local → origin (GitHub) → space (HuggingFace).
  Push to both after significant changes.
- Detached HEAD happens during failed rebase — fix with 
  git rebase --abort then git checkout main.

### Python
- Virtual environment must be activated every session — (.venv) 
  in prompt confirms it's active.
- Path loading for .env: use Path(__file__).parent / ".env" — 
  avoids working directory issues on Windows/Git Bash.
- isinstance() check handles both dict and list gracefully when 
  Claude occasionally returns wrong type.
- Lazy loading pattern for heavy models — global variable + 
  if None check prevents reloading on every Streamlit rerender.

### Streamlit
- Streamlit reruns entire script on every interaction — state must
  be stored in st.session_state, not local variables.
- HuggingFace Spaces Streamlit port: never override port in 
  config.toml — Streamlit SDK uses 8501 by default.
- headless = true required in .streamlit/config.toml for 
  HuggingFace deployment.

### Windows/Git Bash
- Git Bash on Windows uses forward slashes and bash syntax — 
  not PowerShell syntax.
- mkdir with multiple args works in bash but not PowerShell.
- touch creates empty files (bash) vs echo. > file (cmd).
- Long paths with spaces must be quoted in Git Bash.

---

## Product & User Research

### User Research
- Past behaviour beats future intention — "what did you do last 
  time" gives truth, "would you use this" gives politeness.
- If interviews don't change your mind about something, 
  you weren't really listening.
- 5 users find 80%+ of usability issues (Nielsen Norman).
- Be transparent about building a product — hiding intent 
  destroys trust in a small community.
- Most users (4/6) prefer automotive-adjacent transition over 
  full domain switch — validate before building assumptions in.

### Product Decisions
- Extraction alone is not the product — it's the input layer. 
  The value is the end-to-end pipeline grounded in real data.
- Scope creep prevention: new ideas → notes/future.md. 
  Do not implement.
- Ugly UI is fine until Week 7 — substance first.
- File upload deferred — text paste sufficient for user research,
  adds parsing complexity for no user research benefit yet.
- Static corpus chosen over live search for eval reproducibility —
  document the tradeoff honestly in Week 8 write-up.

### AI Product Specific
- Gap between "Claude in conversation" and "Claude in a product" 
  is what prompt engineering, RAG, evaluation, and ontologies 
  are all trying to close.
- Honest limitations section in write-up is strongest signal — 
  junior engineers oversell, senior engineers acknowledge gaps.
- Eval-first thinking: "what does good look like?" before building.
  Most builders skip this. The ones who don't ship better products.

---

## Cost & Performance

- Two API consumers on one budget: Claude Code (dev tool) + 
  app (product). Check console.anthropic.com weekly.
- Cost model: claude-sonnet-4-6 = $3/M input tokens, 
  $15/M output tokens.
- Gap analysis cost: ~$0.033 per run. Skills extraction: ~$0.005.
  Profile classification: ~$0.010. Full pipeline: ~$0.05 per user.
- Use Haiku for cheap tasks (extraction, classification), 
  Sonnet for reasoning tasks (gap analysis, roadmap generation).
  (Currently using Sonnet everywhere — optimise in v2.)
- Latency: embedding model loads once, reused. 
  First run slow (~10s model load), subsequent runs fast.

- **Day 11**: ESCO taxonomy too weak for modern AI/ML skills — 
  MLflow, Kubeflow, LLMs, SOTIF absent. Job ads corpus produced 
  richer, more current ontology. ESCO useful for transferable/
  engineering foundation skills only, and even there Claude 
  handles skill standardisation gracefully without it.
  ESCO ingest script kept for potential v2 use (multilingual 
  skill standardisation) but not in current pipeline.

- **Day 14**: First 30-min review with 1 user surfaced 6 real 
  problems missed during solo development. Most impactful: 
  section labels unclear, raw snippet not useful, dropdown 
  showing irrelevant families. Nielsen Norman principle: 
  5 users find 80% of issues — 4 more tests scheduled Week 7.

  ## Days 16-17 — Evaluation Framework

**Eval-driven development in practice:**
- Built 15 hand-graded test cases before optimising anything
- Baseline: classification 67%, gap analysis 40%
- After 2 iterations: classification 87%, gap analysis 87%
- Without the eval set, prompt changes would have been guesses

**Always inspect raw model output before concluding model is wrong:**
- need_to_learn = 0% looked like gap analyzer failure
- Actual cause: scorer using exact string matching, Claude using 
  different but correct wording
- Lesson: diagnose before fixing. The model was right, the test was wrong.

**Fuzzy matching beats exact matching for LLM output evaluation:**
- "AI and ML fundamentals" ≠ "AI fundamentals" by exact match
- 50% word overlap threshold catches semantically equivalent outputs
- LLMs paraphrase — eval scorers must account for this

**Prompt calibration is iterative, not one-shot:**
- First prompt: TPM profiles scored "strong" (wrong)
- Added readiness calibration rules: fixed to "moderate"
- First classifier: ISO 26262 triggered ml_test (wrong)
- Added disambiguation rules: fixed to ml_engineer/mlops
- Each fix was evidence-based — a failing test case, not a hunch

**Test with real extracted profiles, not simplified fixtures:**
- TC002 passed standalone test at 0.52 (below threshold)
- Same profile scored 0.72 in live app (above threshold)
- Extracted profile richer than handcrafted fixture
- Always run end-to-end before declaring a component working

**Eval set design insights:**
- Expected outputs need domain expertise — not just technical knowledge
- Too specific = brittle (fails on wording variation)
- Too generic = meaningless (everything passes)
- Right level: concept keywords, not exact phrases
- Stopping criteria matter — 87% is good enough, further iteration 
  risks overfitting to 15 cases

**Cost insight:**
- Full pipeline per user: ~$0.033 (classification + gap analysis)
- 15 eval cases: $0.49 total
- At $0.033/run, 1000 users/month = $33 — very manageable