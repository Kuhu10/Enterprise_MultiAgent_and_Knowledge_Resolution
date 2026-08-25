import os
from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class RetrievalAgent:
    def __init__(self):
        # Configure embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
        
        # Connect to ChromaDB
        persist_directory = os.environ.get("CHROMA_DB_PATH", "./vectorstore")
        self.vector_store = Chroma(
            collection_name="enterprise_knowledge",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )

    def retrieve(self, diagnostic_result: Any) -> List[Dict[str, str]]:
        """Retrieves relevant SOPs and knowledge based on the diagnostic result."""
        
        # Use the diagnostic result text as the search query
        query = str(diagnostic_result)
        
        # Retrieve the top 3 most relevant documents
        docs = self.vector_store.similarity_search(query, k=3)
        
        # Format the retrieved documents into the schema expected by the Recommendation Agent
        retrieved_knowledge = []
        for doc in docs:
            retrieved_knowledge.append({
                "id": doc.metadata.get("id", "Unknown"),
                "title": doc.metadata.get("title", "Untitled"),
                "category": doc.metadata.get("category", "General"),
                "content": doc.page_content
            })
            
        return retrieved_knowledge
