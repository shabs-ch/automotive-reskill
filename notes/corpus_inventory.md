# Corpus Inventory — v1

## 1. Job Ads Corpus
**Purpose**: Role matching + gap analysis grounding
**Target**: 150-200 job ads
**Format**: Plain text, one file per ad
**Storage**: `data/raw/jobs/<role_family>/<id>.txt`
**Status**: Not started — Day 8

### Role families to cover (15-25 ads each):

#### Automotive-Adjacent (Tier 1 — validated by interviews)
- "Edge AI Engineer" OR "Embedded AI"
- "Digital Twin" Engineer/Developer
- "Industry 4.0" AI OR "Smart Factory" AI
- "ADAS" Validation OR "Autonomous" Test Engineer  
- "Funktionale Sicherheit" AI OR "SOTIF" Engineer OR "Functional Safety" AI

#### Cross-Domain AI (Tier 2)
- MLOps Engineer
- "AI Product Manager"
- "AI Program Manager"  
- "KI Transformation" OR "AI Transformation"
- "ML Test" OR "AI QA" Engineer

**Sources**:
- StepStone.de (primary — German market)
- Indeed.de (secondary)
- LinkedIn (manual copy only — no scraping)
- Company career pages: Bosch, Continental, ZF, BMW, Mercedes, 
  Siemens, Volkswagen Group

**Search terms for StepStone.de / Indeed.de (use these, not role family names):**
Automotive-Adjacent (Tier 1):
- "Edge AI Engineer" OR "Embedded AI Engineer"
- "Digital Twin" AND (Engineer OR Developer)
- "Industry 4.0" AND (AI OR KI) OR "Smart Factory" AND AI
- "ADAS Validation" OR "Autonomous" AND (Test OR Validation) Engineer
- "Funktionale Sicherheit" AND AI OR "SOTIF Engineer"
- "SDV" AND (Software OR AI) Engineer

Cross-Domain AI (Tier 2):
- "MLOps Engineer"
- "AI Product Manager" OR "KI Produktmanager"
- "AI Program Manager" OR "KI Programmmanager"
- "KI Transformation" OR "AI Transformation Lead"
- "ML Test Engineer" OR "AI QA Engineer"
- "AI Solutions Engineer"

**Collection method:**
- Search StepStone.de first (primary German market)
- Search Indeed.de second
- Manual copy-paste only — no scraping
- Collect 15-25 ads per role family
- Tag each ad after collection with: role_family, language (DE/EN), 
  source, date_collected
- Group by YOUR role family labels after collection, not before

**Reality check (April 2026):**
- "Digital Twin Engineer", "Functional Safety AI Engineer", 
  "Industrial AI Engineer" are rare as exact titles
- Search by keywords, collect what exists, label accordingly
- If fewer than 10 ads exist for a role family after searching,
  combine with closest adjacent family






**Language**: collect both German and English ads
**Geography**: Germany only (filter by location)

---

## 2. ESCO Skills Taxonomy
**Purpose**: Standardised skill labels for ontology
**Format**: JSON / SQLite
**Storage**: `data/raw/esco/`
**Status**: Not started — Day 7

**What we need**:
- ICT skills category
- Engineering skills category
- Manufacturing skills category
- Multilingual labels (DE + EN)

**Source**: https://esco.ec.europa.eu/en/use-esco/download
**Method**: Bulk download (free, no API key needed)

---

## 3. Course Corpus
**Purpose**: Roadmap generation grounding
**Target**: 100+ courses
**Format**: YAML or SQLite
**Storage**: `data/courses.yaml`
**Status**: Not started — Day 18

### Providers to cover:
- Coursera (free audit + paid)
- DeepLearning.AI
- Udacity
- IHK Weiterbildung (NRW, BW, BY)
- Volkshochschule
- Fraunhofer Academy
- RWTH Aachen executive education
- Codecademy / DataCamp (practical skills)

### Fields per course:
- name
- provider
- duration (weeks)
- language (DE / EN)
- cost (EUR)
- bildungsgutschein_eligible (yes / no / unknown)
- azav_certified (yes / no / unknown)
- url
- target_skills (list)
- delivery (online / in-person / hybrid)

**Priority**: BG-eligible German courses first,
             English courses second

---

## 4. Skill Ontology
**Purpose**: Gap analysis — what each role requires
**Format**: YAML
**Storage**: `data/skill_ontology.yaml`
**Status**: Not started — Day 11

**Built from**:
- ESCO taxonomy (filtered)
- Job ads corpus (extracted requirements)
- Your Excel mapping file
- Interview findings

**Target**: 200 skills across 10 role families

---

## 5. Automotive→AI Mappings
**Purpose**: Transferability scoring + bridge actions
**Format**: YAML
**Storage**: `data/automotive_to_ai_mappings.yaml`
**Status**: Draft exists as Excel — Day 12

**Source**: Your Excel file (21 profiles, enhanced with
           transferability + second role + bridge actions)
**Enhancement needed**: bridge actions to cite real courses
                        after Day 18 corpus is built

---

## 6. Bildungsgutschein Rules
**Purpose**: Eligibility checker rules engine
**Format**: YAML
**Storage**: `data/bildungsgutschein_rules.yaml`
**Status**: Not started — Day 22

**Source**: 
- Bundesagentur für Arbeit Merkblatt 11
- BA official website
- AZAV certification database
- Kursnet (official BA course database)

**Scope for v1**:
- ALG-I recipients
- ALG-II recipients  
- Employed but seeking (with Beratungsgespräch)
- Self-employed (limited coverage)

**Out of scope for v1**:
- Reha-Maßnahmen
- AsylbLG cases
- Härtefall self-employed

**Edge cases requiring human counselling (flag, don't rule):**
If user indicates disability/health condition → flag Reha-Beratung
If user indicates asylum seeker status → flag individual assessment
If user indicates self-employed → flag Härtefall possibility
In all three cases: direct user to Arbeitsagentur Beratung directly
---

## 7. Anonymized Engineer Profiles (optional)
**Purpose**: Eval set + test fixtures
**Format**: Plain text
**Storage**: `data/eval/profiles/` (gitignored)
**Status**: Partially available from interviews

**Target**: 10-15 anonymized profiles
**Source**: Interview participants who consent to sharing
**Note**: Never commit real CVs — fictional composites only
          in any committed files

---

## Collection Priority Order
Week 2, Day 7  → ESCO taxonomy
Week 2, Day 8  → Job ads (150-200 ads)
Week 3, Day 11 → Skill ontology (built from above)
Week 3, Day 12 → Automotive mappings YAML (from Excel)
Week 4, Day 18 → Course corpus (100+ courses)
Week 5, Day 22 → BG rules YAML


## Data Quality Rules
- No scraping LinkedIn (ToS violation)
- No committing real CVs or personal data
- All data/ folder gitignored
- Tag each job ad with: role_family, language, source, date_collected
- Flag course BG eligibility as unknown if not confirmed — never assume