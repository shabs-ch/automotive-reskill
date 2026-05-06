import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import Optional

# ── Paths ────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
CHROMA_DIR = DATA_DIR / "chromadb"

# ── Lazy loading — load once, reuse ─────────────────────────────
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
    Given an extracted skills profile, return top N matching roles.
    Returns realistic roles first (top 3), inflated roles after (top 2).

    Args:
        skills_profile: dict from skills extractor
        n_results: total number of matches to return
        domain_filter: optional "automotive_adjacent" or "cross_domain"

    Returns:
        list of role match dicts
    """

    model = _get_model()
    collection = _get_collection()

    # ── Build query text from skills profile ─────────────────────
    query_parts = []

    if skills_profile.get("technical_skills"):
        tech = skills_profile["technical_skills"]
        if isinstance(tech, dict):
            for category, skills in tech.items():
                query_parts.append(f"{category}: {', '.join(skills)}")
        else:
            query_parts.append(f"Technical skills: {', '.join(tech)}")

    if skills_profile.get("domain_knowledge"):
        domain = skills_profile["domain_knowledge"]
        if isinstance(domain, dict):
            for category, items in domain.items():
                query_parts.append(f"{category}: {', '.join(items)}")
        else:
            query_parts.append(
                f"Domain knowledge: {', '.join(domain)}"
            )

    if skills_profile.get("tools"):
        tools = skills_profile.get("tools", [])
        if tools:
            query_parts.append(f"Tools: {', '.join(tools)}")

    if skills_profile.get("transferable_skills"):
        transferable = skills_profile.get("transferable_skills", [])
        if transferable:
            query_parts.append(
                f"Transferable skills: {', '.join(transferable)}"
            )

    if skills_profile.get("years_experience_per_area"):
        years = skills_profile["years_experience_per_area"]
        exp_parts = [
            f"{area} ({y} years)" for area, y in years.items()
        ]
        query_parts.append(f"Experience: {', '.join(exp_parts)}")

    query_text = "\n".join(query_parts)

    if not query_text.strip():
        return []

    # ── Embed query ───────────────────────────────────────────────
    query_embedding = model.encode(query_text).tolist()

    # ── Build domain filter ───────────────────────────────────────
    domain_where = {"domain": domain_filter} if domain_filter else None

    # ── Helper: build combined where filter ───────────────────────
    def build_where(exp_level):
        exp_filter = {"experience_level": exp_level}
        if domain_where:
            return {"$and": [domain_where, exp_filter]}
        return exp_filter

    # ── Query realistic roles first (3 results) ───────────────────
    try:
        realistic_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where=build_where("realistic"),
            include=["documents", "metadatas", "distances"]
        )
        realistic_meta = realistic_results["metadatas"][0]
        realistic_dist = realistic_results["distances"][0]
        realistic_docs = realistic_results["documents"][0]
    except Exception:
        realistic_meta, realistic_dist, realistic_docs = [], [], []

    # ── Query inflated roles after (2 results) ────────────────────
    try:
        inflated_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=2,
            where=build_where("inflated"),
            include=["documents", "metadatas", "distances"]
        )
        inflated_meta = inflated_results["metadatas"][0]
        inflated_dist = inflated_results["distances"][0]
        inflated_docs = inflated_results["documents"][0]
    except Exception:
        inflated_meta, inflated_dist, inflated_docs = [], [], []

    # ── Combine: realistic first, inflated after ──────────────────
    combined_metadatas = realistic_meta + inflated_meta
    combined_distances = realistic_dist + inflated_dist
    combined_documents = realistic_docs + inflated_docs

    # ── Format results ────────────────────────────────────────────
    matches = []
    for meta, distance, doc in zip(
        combined_metadatas, combined_distances, combined_documents
    ):
        score = round(1 - distance, 3)
        matches.append({
            "title": meta.get("title", "Unknown"),
            "company": meta.get("company", "Unknown"),
            "location": meta.get("location", "Unknown"),
            "role_family": meta.get("role_family", "Unknown"),
            "domain": meta.get("domain", "Unknown"),
            "language": meta.get("language", "Unknown"),
            "experience_level": meta.get("experience_level", "Unknown"),
            "match_score": score,
            "snippet": doc[:300],
            "filename": meta.get("filename", "")
        })

    return matches