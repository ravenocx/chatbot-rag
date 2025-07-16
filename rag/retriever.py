import faiss
import os
import pickle
from sentence_transformers import SentenceTransformer
from api.db.database import get_rag_configuration

def get_detailed_instruct(task_description: str, query: str) -> str:
    return f'Instruct: {task_description}\nQuery: {query}'

def retrieve_docs(db_conn, qry) :
    index = faiss.read_index(os.getenv("INDEX_FILE"))
    with open(os.getenv("CHUNK_FILE"), "rb") as f:
        id_to_doc = pickle.load(f)

    model = SentenceTransformer("BAAI/bge-m3")

    # Build instruction for embedding model
    rag_config = get_rag_configuration(db_conn)
    task = rag_config['retriever_instruction']
    print("[DEBUG] Retriever Instruction :", task)
    print("[DEBUG] Top-K Retrieval value :", rag_config['top_k_retrieval'])

    embedding = model.encode(
        get_detailed_instruct(task, qry),
        convert_to_numpy=True,
        normalize_embeddings=True
    ).reshape(1, -1)


    # Distance & Indices
    print("🔍 Searching FAISS index...")
    D, I = index.search(embedding, rag_config['top_k_retrieval'])
    print(f"✅ Found {len(I[0])} results")

    return [{"text": id_to_doc[i], "score": float(D[0][idx])} for idx, i in enumerate(I[0])]

def get_docs(indices):
    index = faiss.read_index(os.getenv("INDEX_FILE"))
    with open(os.getenv("CHUNK_FILE"), "rb") as f:
        id_to_doc = pickle.load(f)
    return [id_to_doc[i] for i in indices]

def truncate_string(s, max_length=100):
    return s[:max_length] + '...' if len(s) > max_length else s

if __name__ == "__main__":
    import db.database as db
    conn = db.db_connection()

    query = input("Ask an Query to retrieval : ")
    result = retrieve_docs(conn, query)
    for i, item in enumerate(result, 1) : 
        print(f"[{i}] Score : {item['score']}")
        print(f"Data : {truncate_string(item['text'], max_length=1000)}")
        print("-" * 60)
