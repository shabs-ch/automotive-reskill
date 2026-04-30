# User Research Synthesis — Week 1

**Interviews completed**: 6
**Profiles**: PMO Lead, Systems Requirements Lead, Technical PM, 
SW Requirements Lead, SW Test Validation Lead, SW Project Manager
**Experience range**: 15–20 years automotive
**Date**: Week 1, Days 4–5

---

## Top 5 Pain Points

**1. Transferable skills are invisible — to tools, to recruiters, to themselves**
All 6 interviewees struggled to identify and articulate their own 
transferable skills. Job search tools match on role titles and keywords, 
missing the cross-domain potential entirely. Agentur für Arbeit 
recommendations were seen as misaligned — matching role labels, not 
actual capabilities or interests.

*Direct signal*: "Current job search tools blindly look for the role 
match" — Person A

**2. AI role landscape is opaque**
Nobody had a clear picture of which AI roles exist, which fit their 
background, and what the realistic entry path looks like. The question 
"what AI roles are right for me given where I come from?" was universal 
and unanswered.

*Direct signal*: "Unable to understand what type of AI skills could 
complement my current skills and for what roles" — Person B

**3. Course overload with no personalised path**
All interviewees felt overwhelmed by the volume of AI courses available. 
The missing piece is not more courses — it's a personalised, realistic 
roadmap that starts from where they are today, not from zero.

*Direct signal*: "AI skills and courses are overwhelmingly present 
everywhere. What is that where I can start?" — Person C
*Direct signal*: "Recommend a realistic roadmap on AI transition 
for the relevant jobs" — Person F

**4. Bildungsgutschein friction**
AZAV and ZFU approved AI courses exist but are predominantly in German. 
English-language courses are not funded. This is a significant barrier 
for engineers who learned their technical vocabulary in English and 
prefer English-language learning materials.

*Direct signal*: "Unable to find English language supported courses 
funded with Bildungsgutschein" — Person B

**5. Rejection patterns are invisible**
No feedback loop from applications. Engineers cannot understand why 
they are being rejected or what to fix. This compounds the anxiety of 
transition without giving actionable direction.

*Direct signal*: "Understanding pattern of the rejections from the 
companies is difficult" — Person B

---

## Top 3 Surprises

**1. Reflection before job search**
Two of six interviewees spent significant time reflecting on what kind 
of work actually makes them happy before searching for roles. This is 
not captured by any existing tool. The transition is not just 
skills-matching — it's values and interest alignment first.

**2. Agentur für Arbeit gap for senior profiles**
Senior roles like PMO Lead are not well recognised by Agentur für Arbeit 
systems. Recommendations defaulted to tangentially related roles that 
didn't match interests or implicit skills. This is a systemic gap our 
tool can partially address.

**3. Currently employed engineers are already anxious**
A second user segment emerged beyond displaced engineers — SW engineers 
still employed but anticipating displacement. This segment may be highly 
motivated to act early and may have access to employer training budgets 
in addition to Bildungsgutschein.

**4. Most users prefer automotive-adjacent transition over full domain switch**
4 of 6 users expressed preference to stay within automotive and upskill 
rather than fully switch domains. Only 2 are actively targeting 
cross-domain AI roles. 

This suggests role recommendations should prioritise automotive AI 
adjacent roles (SDV, digital twin, Industry 4.0, autonomous) alongside 
cross-domain AI roles — not cross-domain first.

**Validation needed**: users expressed preference to stay in automotive 
but did not specifically name SDV/digital twin/Industry 4.0 roles. 
Follow-up interviews should ask: "What specific roles are you targeting 
within automotive?" before building this assumption into the ontology.

---

## What They DON'T Need

- Another job board or keyword-matching tool
- Generic AI course aggregation without personalisation
- CV keyword stuffing for ATS
- More information about AI in general — they know it's coming

---

## Profile Gap — Action Required

All 6 interviews were PMO/TPM/Requirements/Test profiles. 
Embedded SW engineers (AUTOSAR, C, HIL) were not represented. 
These profiles have a distinct pain: deep technical skills with 
unclear ML pivot path. 

**Action**: conduct 2–3 interviews with embedded SW engineers 
before Week 3 ontology work begins. Use existing network of 
currently-employed engineers anticipating displacement.

---

## Product Implications

These findings validate the core product direction and sharpen priorities:

1. **Transferable skills extraction** — already built in Day 2. 
   Validated as the #1 need.
2. **Role matching** — Week 2 priority. Most urgent unanswered question.
3. **Personalised roadmap** — Week 4 priority. "Realistic" is the 
   keyword — grounded in their actual starting point.
4. **Bildungsgutschein checker** — Week 5 priority. English course 
   gap is a specific finding to address in corpus design.
5. **Rejection pattern analysis** — not in current plan. 
   Add to `notes/future.md`.
6. **Values/interest alignment** — not in current plan. 
   Add to `notes/future.md`.