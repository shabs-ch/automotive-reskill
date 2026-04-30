# Product Spec — v1
**Last updated**: Week 1 Weekend
**Status**: Draft — pre-Week 2 build

---

## What this product is

A tool that helps automotive engineers identify their strongest 
next career move — within automotive AI or beyond — and gives them 
a concrete, funded path to get there.

---

## Target users (v1)
- Displaced automotive engineers: SW, test/validation, requirements, 
  PMO/TPM profiles
- 15-20 years experience
- Based in Germany
- Aware of Bildungsgutschein but confused by it

## Target users (v2 stretch)
- Currently employed automotive engineers anticipating displacement
- Embedded SW engineers (AUTOSAR, C, HIL)
- Production and mechanical engineers

---

## The flow — screen by screen

### Screen 1 — CV Input
**Input**: paste CV text (plain text, any language)
**Action**: "Analyse My Profile" button
**Output**: navigates to Screen 2

### Screen 2 — Skills Profile
**Shows**:
- Technical skills (grouped by subcategory)
- Domain knowledge (grouped by subcategory)
- Tools
- Transferable skills (cross-domain implicit skills)
- Years of experience per area

**Action**: "Find Matching Roles" button
**Output**: navigates to Screen 3

### Screen 3 — Role Matches
**Shows**: top 5 matching roles, each with:
- Role title
- Why it matches (skills alignment)
- Whether it's automotive-adjacent or cross-domain
- Match strength indicator
- 2-3 example real job posting titles

**Action**: user selects one role → "Analyse My Gaps" button
**Output**: navigates to Screen 4

### Screen 4 — Gap Analysis
**Shows**:
- Skills you already have (relevant to target role)
- Skills missing (must learn)
- Skills transferable with bridging (you have the foundation)
- Estimated effort to close gaps

**Action**: "Build My Roadmap" button
**Output**: navigates to Screen 5

### Screen 5 — Learning Roadmap
**Shows**: month-by-month plan with:
- Specific courses (real, cited, not hallucinated)
- 1-2 portfolio project suggestions relevant to target role
  (e.g. "Build a predictive maintenance model using your HIL testing domain knowledge")
- Provider, duration, cost, language
- Bildungsgutschein eligibility flag per course
- Rationale for each recommendation

**Action**: "Check Bildungsgutschein Eligibility" button
**Output**: navigates to Screen 6

### Screen 6 — Bildungsgutschein Checker
**Shows**:
- User's likely eligibility status (based on self-reported status)
- Which courses in their roadmap are BG-eligible
- Step-by-step application guidance
- Warning: verify with Arbeitsagentur before financial decisions

### Screen 7 — CV Reframing (optional, end of flow)
**Shows**: for each CV bullet the user wants to reframe:
- 3 rewritten versions in English (for international applications)
- 3 rewritten versions in German (for German market applications)
- Target role vocabulary used in both languages
- User picks preferred version per language

---

## What each screen needs from the backend

| Screen | Data source | Claude involved? |
|--------|-------------|-----------------|
| Skills Profile | Claude API | Yes — extraction |
| Role Matches | ChromaDB + job ads corpus | Yes — reasoning |
| Gap Analysis | Skill ontology YAML | Yes — nuance |
| Roadmap | Course corpus RAG | Yes — grounded generation |
| BG Checker | Rules engine (YAML) | No — pure rules |
| CV Reframing | Claude API | Yes — generation |

---

## What v1 does NOT do
- File upload (text paste only)
- Save user sessions
- User accounts or login
- Employer-side features
- Turkish or other language UI
- Values/interest alignment
- Rejection pattern analysis

---

## Success criteria for v1
- 5 real users complete the full flow end-to-end
- Hallucination rate on course recommendations < 5%
- Full run completes in under 60 seconds
- At least 1 user says "I would actually use this"

---

## Open questions (resolve by Day 20 review)
- Do users want automotive-adjacent roles as Tier 1 or equal weight 
  with cross-domain? Needs follow-up interview validation.
- English vs German UI — currently English. Should roadmap and CV 
  output be German only or user-selectable?
- Should Screen 6 ask for employment status upfront (Screen 1) 
  to personalise BG eligibility throughout?