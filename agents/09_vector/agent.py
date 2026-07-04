"""
AGENT 9 - Vector Database Agent
Parses local Australian guidelines under clinical_guidelines/
and indexes them locally using TF-IDF for semantic document retrieval.
"""
from pathlib import Path
import json
import pickle
import re
from datetime import datetime, timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

OUTPUT_DIR = Path("outputs/09_vector_db")
STORE_PKL = OUTPUT_DIR / "vector_store.pkl"
GUIDELINES_DIR = Path("clinical_guidelines")

class LocalTFIDFStore:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.chunks = []
        self.tfidf_matrix = None

    def chunk_document(self, text: str, filename: str, chunk_size: int = 400, overlap: int = 100) -> list[dict]:
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            words_count = len(sentence.split())
            if current_length + words_count > chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "source": filename,
                    "word_count": len(chunk_text.split())
                })
                # Handle overlap: keep last few sentences that fit in overlap
                overlap_chunk = []
                overlap_len = 0
                for s in reversed(current_chunk):
                    s_words = len(s.split())
                    if overlap_len + s_words <= overlap:
                        overlap_chunk.insert(0, s)
                        overlap_len += s_words
                    else:
                        break
                current_chunk = overlap_chunk
                current_length = overlap_len
                
            current_chunk.append(sentence)
            current_length += words_count
            
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "source": filename,
                "word_count": len(chunk_text.split())
            })
        return chunks

    def build_index(self, guidelines_path: Path):
        self.chunks = []
        if not guidelines_path.exists():
            # Seed empty if not found
            return
            
        for file in guidelines_path.glob("*.md"):
            try:
                content = file.read_text(encoding='utf-8')
                doc_chunks = self.chunk_document(content, file.name)
                self.chunks.extend(doc_chunks)
            except Exception as e:
                print(f"Error parsing {file.name}: {str(e)}")
                
        if self.chunks:
            texts = [c["text"] for c in self.chunks]
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        if not self.chunks or self.tfidf_matrix is None:
            return []
            
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Sort indices by highest similarity
        top_indices = similarities.argsort()[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.05: # Relevance threshold
                results.append({
                    "text": self.chunks[idx]["text"],
                    "source": self.chunks[idx]["source"],
                    "score": round(score, 4)
                })
        return results

def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Expose utility for RAG Agent to query guideline database."""
    if not STORE_PKL.exists():
        # Fallback to run index on-the-fly
        store = LocalTFIDFStore()
        store.build_index(GUIDELINES_DIR)
        return store.retrieve(query, top_k)
        
    try:
        with STORE_PKL.open("rb") as f:
            store = pickle.load(f)
        return store.retrieve(query, top_k)
    except Exception:
        # Fallback if pickle load fails
        store = LocalTFIDFStore()
        store.build_index(GUIDELINES_DIR)
        return store.retrieve(query, top_k)

def run() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        store = LocalTFIDFStore()
        store.build_index(GUIDELINES_DIR)
        
        with STORE_PKL.open("wb") as f:
            pickle.dump(store, f)
            
        status = {
            "vector_db": "LocalTFIDFStore",
            "document_count": len(list(GUIDELINES_DIR.glob("*.md"))),
            "chunk_count": len(store.chunks),
            "status": "indexed",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        cfg_json = OUTPUT_DIR / "vector_db_config.json"
        cfg_json.write_text(json.dumps(status, indent=2))
        return {"success": True, "artifact": str(cfg_json)}
    except Exception as e:
        return {"success": False, "error": str(e), "artifact": ""}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
