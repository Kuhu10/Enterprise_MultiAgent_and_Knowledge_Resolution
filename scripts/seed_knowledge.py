import os
import json
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")

# Configure Vector Store
persist_directory = os.environ.get("CHROMA_DB_PATH", "./vectorstore")
vector_store = Chroma(
    collection_name="enterprise_knowledge",
    embedding_function=embeddings,
    persist_directory=persist_directory
)

# Define mock enterprise knowledge documents
mock_documents = [
    Document(
        page_content="Step 1: Check Database metrics for connection count. Step 2: If connections are exhausted, restart the AuthenticationService safely using runbook RS-Auth-01. Step 3: Monitor for 15 minutes.",
        metadata={
            "id": "SOP-849",
            "title": "Handling Authentication Database Connection Exhaustion",
            "category": "SOP"
        }
    ),
    Document(
        page_content="To safely restart the AuthenticationService, drain traffic from the load balancer, stop the service, start the service, run health checks, and re-add to the load balancer.",
        metadata={
            "id": "Runbook RS-Auth-01",
            "title": "Safe Restart of AuthenticationService",
            "category": "Runbook"
        }
    ),
    Document(
        page_content="Historical Incident INC-301: AuthenticationService outage due to db connection leak. Resolution: Restarted service, applied patch to connection pool logic.",
        metadata={
            "id": "INC-301",
            "title": "Historical Incident: Connection Leak",
            "category": "Historical Incident"
        }
    ),
    Document(
        page_content="Step 1: Verify Redis cache is reachable. Step 2: Flush cache if memory is over 95%. Step 3: Scale up Redis nodes if issue persists.",
        metadata={
            "id": "SOP-112",
            "title": "Handling Cache Memory Issues",
            "category": "SOP"
        }
    )
]

print("Adding documents to ChromaDB...")
vector_store.add_documents(mock_documents)
print(f"Successfully seeded {len(mock_documents)} documents into {persist_directory}!")
