# Future Ideas

## From user research Week 1

- **Rejection pattern analysis**: help engineers understand why 
  they are being rejected and what to fix
- **Values and interest alignment**: before skills matching, 
  help users identify what kind of work makes them happy — 
  2 of 6 users did this reflection independently before job searching
- **File upload**: allow CV upload as PDF/Word instead of text paste
- **Transferable skills taxonomy**: map extracted skills to named 
  categories (structured problem-solving, change management etc.)
- **Automotive-adjacent role track**: validate whether displaced 
  engineers are aware of and targeting SDV, digital twin, Industry 4.0, 
  autonomous roles specifically. If confirmed in follow-up interviews, 
  add as Tier 1 role families alongside cross-domain AI roles.

## Enhancement — Bridge Actions
Bridge actions in automotive_to_ai_mappings.yaml are currently generic. 
Revisit on Day 12 with real course data (Day 18 corpus) and real job ad 
requirements (Day 8). Target: every bridge action cites a real, 
named, BG-eligible course where possible.

**Gap Analysis v2**: connect Job Ads ChromaDB directly to ground 
  gap analysis in live market requirements, not just ontology. 
  Useful when ontology and market diverge over time.

## Prompt improvements
- **Transferable skills quality**: Current extraction produces 
  generic or low-value transferable skills. Needs prompt improvement 
  after eval framework is built on Day 16 — fix with evidence, 
  not guessing. Possible fix: few-shot examples of good vs bad 
  transferable skill extraction.

## HuggingFace persistent ChromaDB
ChromaDB on HF free tier is ephemeral — resets on Space restart.
Options for v2: HF Datasets as persistent storage, or hosted 
vector DB (Pinecone free tier). Needed before public launch.

## ESCO integration (v2)
ESCO taxonomy currently unused in pipeline — job ads corpus 
produced better ontology for AI/ML skills. Potential v2 use:
skill label standardisation (mapping messy CV text to canonical 
ESCO labels) and German↔English skill equivalence for multilingual
CV processing.