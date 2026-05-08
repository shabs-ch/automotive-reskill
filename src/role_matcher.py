import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import Optional
from src.profile_classifier import classify_profile

# ── Paths ────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
CHROMA_DIR = DATA_DIR / "chromadb"

# ── Lazy loading ─────────────────────────────────────────────────
_model = None
_collection = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("BAAI/bge-m3")
    return _model

def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_collection("job_ads")
    return _collection

# ── Main function ────────────────────────────────────────────────
def match_roles(
    skills_profile: dict,
    n_results: int = 5,
    domain_filter: Optional[str] = None
) -> list[dict]:
    """
    Given a skills profile, classify it then query ChromaDB
    for matching roles proportional to classification scores.
    """

    model = _get_model()
    collection = _get_collection()

    # ── Step 1: Classify profile ──────────────────────────────────
    classifications = classify_profile(skills_profile)

    # Filter to families scoring above threshold
    THRESHOLD = 0.6
    qualifying = [
        c for c in classifications
        if c["score"] >= THRESHOLD
    ]

    # Always have at least one family
    if not qualifying:
        # No strong match — show 1 result from each family
        # so user can explore all directions
        for c in classifications:
            c["low_confidence"] = True
            c["slots"] = 1
        qualifying = classifications  # all four, 1 slot each

    # ── Step 2: Allocate result slots proportionally ──────────────
    # Top family gets 3 slots, second gets 2, third gets 1
    slot_allocation = [3, 2, 1]
    family_slots = []

    # Check if this is a low confidence fallback
    is_low_confidence = any(
        c.get("low_confidence", False) for c in qualifying
    )

    if is_low_confidence:
        # Low confidence — 1 slot per family, show all 4
        for c in qualifying:
            family_slots.append({
                "family": c["family"],
                "slots": 1,
                "score": c["score"],
                "rationale": c["rationale"]
            })
    else:
        # Normal flow — proportional allocation
        for i, classification in enumerate(qualifying[:3]):
            slots = slot_allocation[i] if i < len(slot_allocation) else 1
            family_slots.append({
                "family": classification["family"],
                "slots": slots,
                "score": classification["score"],
                "rationale": classification["rationale"]
            })

    # ── Step 3: Build query text ──────────────────────────────────
    query_parts = []

    tech = skills_profile.get("technical_skills", {})
    if isinstance(tech, dict):
        for category, skills in tech.items():
            query_parts.append(f"{category}: {', '.join(skills)}")
    elif tech:
        query_parts.append(f"Technical: {', '.join(tech)}")

    domain = skills_profile.get("domain_knowledge", {})
    if isinstance(domain, dict):
        for category, items in domain.items():
            query_parts.append(f"{category}: {', '.join(items)}")
    elif domain:
        query_parts.append(f"Domain: {', '.join(domain)}")

    tools = skills_profile.get("tools", [])
    if tools:
        query_parts.append(f"Tools: {', '.join(tools)}")

    transferable = skills_profile.get("transferable_skills", [])
    if transferable:
        query_parts.append(
            f"Transferable: {', '.join(transferable)}"
        )

    years = skills_profile.get("years_experience_per_area", {})
    if years:
        exp = [f"{area}({y}yrs)" for area, y in years.items()]
        query_parts.append(f"Experience: {', '.join(exp)}")

    query_text = "\n".join(query_parts)
    if not query_text.strip():
        return []

    query_embedding = model.encode(query_text).tolist()

    # ── Step 4: Query ChromaDB per qualifying family ──────────────
    all_matches = []
    seen_ids = set()

    for fs in family_slots:
        family = fs["family"]
        slots = fs["slots"]

        # Build where filter
        where = {"role_family": family}
        if domain_filter:
            where = {"$and": [
                {"role_family": family},
                {"domain": domain_filter}
            ]}

        # Try realistic first
        try:
            realistic_where = {"$and": [
                {"role_family": family},
                {"experience_level": "realistic"}
            ]}
            if domain_filter:
                realistic_where = {"$and": [
                    {"role_family": family},
                    {"experience_level": "realistic"},
                    {"domain": domain_filter}
                ]}

            r = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(slots, 32),
                where=realistic_where,
                include=["documents", "metadatas", "distances"]
            )
            metas = r["metadatas"][0]
            dists = r["distances"][0]
            docs = r["documents"][0]
        except Exception:
            metas, dists, docs = [], [], []

        # Fill remaining slots with inflated if needed
        if len(metas) < slots:
            try:
                inflated_where = {"$and": [
                    {"role_family": family},
                    {"experience_level": "inflated"}
                ]}
                if domain_filter:
                    inflated_where = {"$and": [
                        {"role_family": family},
                        {"experience_level": "inflated"},
                        {"domain": domain_filter}
                    ]}

                ri = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(slots - len(metas), 32),
                    where=inflated_where,
                    include=["documents", "metadatas", "distances"]
                )
                metas += ri["metadatas"][0]
                dists += ri["distances"][0]
                docs += ri["documents"][0]
            except Exception:
                pass

        # Add to results, deduplicate
        for meta, dist, doc in zip(metas, dists, docs):
            filename = meta.get("filename", "")
            if filename in seen_ids:
                continue
            seen_ids.add(filename)

            score = round(1 - dist, 3)
            all_matches.append({
                "title": meta.get("title", "Unknown"),
                "company": meta.get("company", "Unknown"),
                "location": meta.get("location", "Unknown"),
                "role_family": meta.get("role_family", "Unknown"),
                "domain": meta.get("domain", "Unknown"),
                "language": meta.get("language", "Unknown"),
                "experience_level": meta.get(
                    "experience_level", "Unknown"
                ),
                "match_score": score,
                "snippet": doc[:300],
                "filename": filename,
                "family_fit_score": fs["score"],
                "family_rationale": fs["rationale"],
                "low_confidence": fs.get("low_confidence", False)
            })

    # Sort by family fit score first, then match score
    all_matches.sort(
        key=lambda x: (x["family_fit_score"], x["match_score"]),
        reverse=True
    )
    


    return all_matches[:n_results]