import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever

# Path to the persistent ChromaDB created by ingest_data.py
PERSIST_DIRECTORY = os.path.join(os.getcwd(), "data", "chroma_db")

def get_retriever() -> VectorStoreRetriever:
    """
    Returns a unified retriever that searches across restaurants, hotels, and attractions.
    Since Chroma doesn't natively support querying multiple collections in one go easily via LangChain 
    without MultiVectorRetriever or similar complex setups, we will return a retriever 
    connected to a 'merged' logical view or we can create a custom retriever.
    
    For simplicity and robustness in this task, we will inspect which collection is most relevant 
    or just use one if we merged them. 
    
    WAIT: `ingest_data.py` created separate collections: 'restaurants', 'hotels', 'attractions'.
    We should probably query all of them or select based on intent.
    
    Let's create a custom retriever or a helper that queries all 3.
    """
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Connect to collections
    # Note: If collections don't exist, this might raise an error or just return empty.
    
    # Strategy: We will create a Composite Retriever later or just use a simple one for now.
    # To keep it simple for the "Start" phase, let's assume we want to retrieve from all.
    # But standard LangChain retrievers usually bind to one VS.
    
    # Better approach for this agent: The Agent can have tools `lookup_hotels`, `lookup_restaurants`.
    # BUT, the requirements say "Implement a RAG Retriever that searches ChromaDB".
    # I'll expose a function that queries all 3 and combines results.
    
    return CompositeRetriever(embeddings)


class CompositeRetriever:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.persist_dir = PERSIST_DIRECTORY
        
    def invoke(self, query: str, k: int = 3):
        # We manually query each collection
        results = []
        
        for col_name in ["restaurants", "hotels", "attractions"]:
            try:
                # We need to re-instantiate Chroma for each collection
                vectorstore = Chroma(
                    collection_name=col_name,
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_dir
                )
                
                # Check if collection is empty or doesn't exist? Chroma handles this gracefully usually.
                # similarity_search_with_score
                docs = vectorstore.similarity_search(query, k=k)
                for d in docs:
                    # Append source to metadata for clarity
                    d.metadata["source_collection"] = col_name
                results.extend(docs)
            except Exception as e:
                print(f"Error querying {col_name}: {e}")
                
        # Reranking could happen here, but we will just return top K from each mix
        # or just return them all (3*k documents).
        return results

    def get_relevant_documents(self, query: str):
        return self.invoke(query)
