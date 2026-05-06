import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
import re

# ── Paths ────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
JOBS_DIR = DATA_DIR / "raw" / "jobs"
CHROMA_DIR = DATA_DIR / "chromadb"
CHROMA_DIR.mkdir(exist_ok=True)

# ── Model ────────────────────────────────────────────────────────
print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-m3")
print("Model loaded.")

# ── ChromaDB client ──────────────────────────────────────────────
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

# Delete existing collection if re-running
try:
    client.delete_collection("job_ads")
    print("Deleted existing job_ads collection.")
except:
    pass

collection = client.create_collection(
    name="job_ads",
    metadata={"hnsw:space": "cosine"}
)
print("Created job_ads collection.")

# ── Helper: extract signal sections ─────────────────────────────
SIGNAL_HEADERS = [
    # English
    "requirements", "qualifications", "your profile",
    "what you bring", "what we expect", "responsibilities",
    "your responsibilities", "what you will do",
    "key responsibilities", "your tasks", "tasks",
    # German
    "anforderungen", "ihr profil", "was sie mitbringen",
    "aufgaben", "ihre aufgaben", "was wir erwarten",
    "qualifikationen", "was du mitbringst"
]

def extract_signal(text):
    """Extract requirements and responsibilities sections."""
    lines = text.splitlines()
    signal_lines = []
    capturing = False

    for line in lines:
        line_lower = line.strip().lower()

        # Start capturing when we hit a signal header
        if any(header in line_lower for header in SIGNAL_HEADERS):
            capturing = True

        if capturing:
            signal_lines.append(line)

    # If no headers found, use full text
    if not signal_lines:
        return text.strip()

    return "\n".join(signal_lines).strip()


# ── Helper: parse job file ───────────────────────────────────────
def parse_job_file(filepath):
    """Parse job ad text file into metadata + description."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "---" not in content:
        return None

    header_part, description = content.split("---", 1)

    metadata = {}
    for line in header_part.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()

    metadata["filename"] = filepath.name
    metadata["description"] = description.strip()

    return metadata


# ── Main: embed all job ads ──────────────────────────────────────
print("\nEmbedding job ads...")

embedded = 0
skipped = 0
ids = []
embeddings = []
documents = []
metadatas = []

for txt_file in sorted(JOBS_DIR.rglob("*.txt")):
    job = parse_job_file(txt_file)

    if not job:
        skipped += 1
        continue

    # Extract signal sections for embedding
    signal_text = extract_signal(job["description"])

    if len(signal_text.strip()) < 50:
        print(f"  ⚠️  Too short, skipping: {txt_file.name}")
        skipped += 1
        continue

    # Generate embedding
    embedding = model.encode(signal_text).tolist()

    # Prepare metadata (ChromaDB only accepts str/int/float/bool)
    meta = {
        "title": job.get("title", "unknown"),
        "company": job.get("company", "unknown"),
        "location": job.get("location", "unknown"),
        "role_family": job.get("role_family", "unknown"),
        "domain": job.get("domain", "unknown"),
        "language": job.get("language", "unknown"),
        "experience_level": job.get("experience_level", "unknown"),
        "source": job.get("source", "unknown"),
        "filename": job.get("filename", "unknown")
    }

    doc_id = txt_file.stem  # filename without extension

    ids.append(doc_id)
    embeddings.append(embedding)
    documents.append(signal_text)
    metadatas.append(meta)

    embedded += 1
    print(f"  ✅ {txt_file.name} — {len(signal_text.split())} words")

# ── Batch add to ChromaDB ────────────────────────────────────────
if ids:
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

print(f"\n✅ Embedded {embedded} job ads into ChromaDB")
print(f"   Skipped: {skipped}")
print(f"   Collection size: {collection.count()}")
print(f"   ChromaDB stored at: {CHROMA_DIR}")