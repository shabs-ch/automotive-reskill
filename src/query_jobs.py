import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
CHROMA_DIR = DATA_DIR / "chromadb"

# ── Load model + collection ──────────────────────────────────────
print("Loading model and ChromaDB...")
model = SentenceTransformer("BAAI/bge-m3")
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_collection("job_ads")
print(f"Collection loaded: {collection.count()} job ads\n")

# ── Query function ───────────────────────────────────────────────
def search_roles(query_text, n_results=5, domain_filter=None):
    """Search for matching roles given a skills profile."""

    # Embed the query
    query_embedding = model.encode(query_text).tolist()

    # Build filter
    where = None
    if domain_filter:
        where = {"domain": domain_filter}

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"]
    )

    return results


def print_results(results, query_label=""):
    """Pretty print search results."""
    print(f"── Results for: {query_label} ──")
    
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    documents = results["documents"][0]

    for i, (meta, distance, doc) in enumerate(
        zip(metadatas, distances, documents)
    ):
        score = round(1 - distance, 3)  # cosine similarity
        print(f"\n#{i+1} — {meta['title']}")
        print(f"     Company:     {meta['company']}")
        print(f"     Role family: {meta['role_family']}")
        print(f"     Domain:      {meta['domain']}")
        print(f"     Language:    {meta['language']}")
        print(f"     Exp level:   {meta['experience_level']}")
        print(f"     Match score: {score}")
        print(f"     Snippet:     {doc[:150]}...")


# ── Test queries ─────────────────────────────────────────────────
if __name__ == "__main__":

    # Query 1 — Embedded SW / AUTOSAR background
    query1 = """
    Senior embedded software engineer with 15 years automotive experience.
    Skills: AUTOSAR Classic Platform, ISO 26262 functional safety, 
    embedded C, CAN bus, LIN, requirements engineering, 
    real-time systems, ECU development, Vector tools, DOORS.
    Looking to transition into AI roles.
    """
    results1 = search_roles(query1, n_results=5)
    print_results(results1, "Embedded SW / AUTOSAR Engineer")

    print("\n" + "="*60 + "\n")

    # Query 2 — TPM / Program Manager background
    query2 = """
    Technical Program Manager with 20 years automotive experience.
    Skills: cross-functional program leadership, stakeholder management,
    OKR tracking, risk management, change management, agile delivery,
    requirements engineering, supplier management, budget ownership.
    Looking for AI program or product management roles.
    """
    results2 = search_roles(query2, n_results=5)
    print_results(results2, "TPM / Program Manager")

    print("\n" + "="*60 + "\n")

    # Query 3 — Test/Validation Engineer background
    query3 = """
    Test and validation engineer with 18 years automotive experience.
    Skills: HIL testing, dSPACE, CANoe, SIL testing, 
    test automation, validation processes, ISTQB certified,
    requirements-based testing, defect tracking.
    Interested in ML testing and AI validation roles.
    """
    results3 = search_roles(query3, n_results=5)
    print_results(results3, "Test/Validation Engineer")

    print("\n" + "="*60 + "\n")

    # Query 4 — automotive_adjacent filter only
    query4 = """
    Automotive software architect with systems engineering background.
    Python basics, strong domain knowledge in vehicle systems,
    safety-critical software development experience.
    """
    results4 = search_roles(
        query4, n_results=3,
        domain_filter="automotive_adjacent"
    )
    print_results(results4, "Automotive SW Architect (automotive_adjacent only)")