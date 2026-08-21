import os
import glob
import uuid
import chromadb
from sentence_transformers import SentenceTransformer

class SOPRetrievalEngine:
    """
    A lightweight RAG (Retrieval-Augmented Generation) engine for Standard Operating Procedures (SOPs).
    Uses SentenceTransformers for generating embeddings and ChromaDB for vector storage.
    """
    def __init__(self, vectorstore_path: str = "vectorstore", collection_name: str = "sop_collection"):
        print("Initializing SentenceTransformer ('all-MiniLM-L6-v2')...")
        # Load embedding model (384-dimensional dense vectors)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print(f"Connecting to ChromaDB at '{vectorstore_path}'...")
        # Initialize persistent Chroma client
        self.chroma_client = chromadb.PersistentClient(path=vectorstore_path)
        
        # Get or create our collection for storing SOP chunks
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

    def _chunk_markdown(self, file_path: str) -> list[dict]:
        """
        Parses a markdown file and chunks it by section/paragraph.
        Aims for chunks of ~300-500 tokens (approx. 250-400 words).
        Keeps track of the source filename and the active header section.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        filename = os.path.basename(file_path)
        paragraphs = content.split("\n\n")
        
        chunks = []
        current_chunk_paragraphs = []
        current_header = "Introduction"
        current_word_count = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Check if this paragraph is a Markdown header (e.g. # Header, ## Subheader)
            if paragraph.startswith("#"):
                # If we have accumulated content, flush it as a chunk before switching sections
                if current_chunk_paragraphs:
                    chunks.append({
                        "text": "\n\n".join(current_chunk_paragraphs),
                        "metadata": {
                            "source_file": filename,
                            "section": current_header
                        }
                    })
                    current_chunk_paragraphs = []
                    current_word_count = 0
                
                # Update current section header (strip leading # characters)
                current_header = paragraph.lstrip("#").strip()
                continue
                
            # Estimate word count of the paragraph
            words = paragraph.split()
            para_word_count = len(words)
            
            # If adding this paragraph exceeds our size limit (~350 words ≈ 450 tokens), 
            # save the current chunk first
            if current_word_count + para_word_count > 350 and current_chunk_paragraphs:
                chunks.append({
                    "text": "\n\n".join(current_chunk_paragraphs),
                    "metadata": {
                        "source_file": filename,
                        "section": current_header
                    }
                })
                current_chunk_paragraphs = [paragraph]
                current_word_count = para_word_count
            else:
                current_chunk_paragraphs.append(paragraph)
                current_word_count += para_word_count
                
        # Flush any remaining paragraphs into a final chunk
        if current_chunk_paragraphs:
            chunks.append({
                "text": "\n\n".join(current_chunk_paragraphs),
                "metadata": {
                    "source_file": filename,
                    "section": current_header
                }
            })
            
        return chunks

    def ingest_sops(self, sops_dir: str = "data/sops"):
        """
        Loads all markdown files from the SOPs directory, chunks them,
        generates embeddings, and stores them in ChromaDB.
        """
        search_path = os.path.join(sops_dir, "*.md")
        sop_files = glob.glob(search_path)
        
        if not sop_files:
            print(f"No SOP markdown files found in '{sops_dir}'. Please add some .md files first.")
            return

        all_documents = []
        all_embeddings = []
        all_metadatas = []
        all_ids = []

        print(f"Found {len(sop_files)} SOP files. Processing...")
        
        for file_path in sop_files:
            print(f"Processing '{file_path}'...")
            chunks = self._chunk_markdown(file_path)
            print(f"  - Split into {len(chunks)} chunks.")
            
            for chunk in chunks:
                text = chunk["text"]
                metadata = chunk["metadata"]
                
                # Generate embedding vector
                embedding = self.embedding_model.encode(text).tolist()
                
                all_documents.append(text)
                all_embeddings.append(embedding)
                all_metadatas.append(metadata)
                all_ids.append(str(uuid.uuid4()))

        if all_documents:
            print(f"Ingesting {len(all_documents)} total chunks into ChromaDB...")
            self.collection.add(
                ids=all_ids,
                embeddings=all_embeddings,
                metadatas=all_metadatas,
                documents=all_documents
            )
            print("Ingestion complete.")

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Queries the database for top_k most relevant chunks matching the query.
        Returns a list of dicts with keys: text, source_file, section, score.
        """
        # Embed the query
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Query ChromaDB collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        formatted_results = []
        
        # Parse query results
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            
            for doc, meta, dist in zip(docs, metadatas, distances):
                # Convert cosine distance to a similarity score: similarity = 1 - distance
                similarity_score = 1.0 - dist
                formatted_results.append({
                    "text": doc,
                    "source_file": meta.get("source_file", "Unknown"),
                    "section": meta.get("section", "Unknown"),
                    "score": round(similarity_score, 4)
                })
                
        return formatted_results

if __name__ == "__main__":
    import sys
    
    # Initialize the engine
    engine = SOPRetrievalEngine()
    
    # Check if we should ingest
    sops_dir = os.path.join("data", "sops")
    print("\n--- Document Ingestion Step ---")
    engine.ingest_sops(sops_dir)
    
    print("\n--- Interactive Retrieval Test ---")
    print("Type a query to search the SOP collection. Type 'exit' to quit.")
    
    while True:
        try:
            query = input("\nEnter query: ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit']:
                print("Exiting test.")
                break
                
            results = engine.retrieve(query, top_k=3)
            
            if not results:
                print("No relevant SOP chunks found.")
                continue
                
            print(f"\nTop {len(results)} matches found:")
            for idx, res in enumerate(results, 1):
                print(f"\n[{idx}] Source: {res['source_file']} | Section: {res['section']}")
                print(f"    Similarity Score: {res['score']}")
                print("    " + "-"*40)
                # Print indented text for clean display
                indented_text = "\n".join("    " + line for line in res['text'].split("\n"))
                print(indented_text)
                print("    " + "-"*40)
                
        except KeyboardInterrupt:
            print("\nExiting.")
            sys.exit(0)
