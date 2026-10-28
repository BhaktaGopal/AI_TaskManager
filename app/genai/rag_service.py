from sqlalchemy.orm import Session
from app.models.task import Task
from app.core.redis_client import redis_client  
# Import Redis client to use caching
from langchain_huggingface import HuggingFaceEmbeddings
# Free embedding model
from transformers import pipeline
from langchain_community.vectorstores import FAISS

# Initialize FREE embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
# Runs locally, no API key required


def build_index(db: Session, user_id: int):
    tasks = db.query(Task).filter(Task.owner_id == user_id).all()

    if not tasks:
        return None

    texts = []

    for task in tasks:
        text = f"""
        Task: {task.title}
        Description: {task.description}
        Status: {task.status}
        Priority: {task.priority}
        """
        # Convert structured data → text for embeddings

        texts.append(text)

    vector_store = FAISS.from_texts(texts, embeddings)
    # Create vector DB locally

    return vector_store


def query_tasks(db: Session, user_id: int, query: str):
    
    # Create unique cache key per user + query
    cache_key = f"rag:{user_id}:{query}"
    # Example: rag:1:pending tasks

    # 🔴 Step 1: Check cache
    cached_result = redis_client.get(cache_key)

    if cached_result:
        return cached_result  
        # Return instantly if found (cache hit)

    # 🔴 Step 2: Run RAG pipeline (cache miss)
    vector_store = build_index(db, user_id)

    if vector_store is None:
        return "No tasks available"

    docs = vector_store.similarity_search(query, k=3)

    texts = [doc.page_content for doc in docs]

    result = generate_answer(query, texts)  
    # This is the expensive part (LLM call)

    # 🔴 Step 3: Store result in Redis
    redis_client.setex(
        cache_key,
        300,  
        result
    )
    # setex → set with expiry
    # 300 seconds = 5 minutes TTL

    return result


# Load free text generation model
generator = pipeline("text-generation", model="google/flan-t5-base")

def generate_answer(query, docs):
    context = "\n".join(docs)

    prompt = f"""
    Answer the question based on the tasks below:

    {context}

    Question: {query}
    """

    result = generator(prompt, max_length=200)

    return result[0]["generated_text"]