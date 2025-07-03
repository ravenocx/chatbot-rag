import faiss
import os
import pickle
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

def get_detailed_instruct(task_description: str, query: str) -> str:
    return f'Instruct: {task_description}\nQuery: {query}'

def retrieve_docs(qry, k=5) :
    load_dotenv()

    index = faiss.read_index(os.getenv("INDEX_FILE"))
    with open(os.getenv("CHUNK_FILE"), "rb") as f:
        id_to_doc = pickle.load(f)

    model = SentenceTransformer("BAAI/bge-m3")

    task = "Given a user’s product-related query, retrieve the most relevant and informative product descriptions, specifications, or recommendations that directly address the query."

    embedding = model.encode(
        get_detailed_instruct(task, qry),
        convert_to_numpy=True,
        normalize_embeddings=True
    ).reshape(1, -1)


    # Distance & Indices
    D, I = index.search(embedding, k)

    return [{"text": id_to_doc[i], "score": float(D[0][idx])} for idx, i in enumerate(I[0])]

def get_docs(indices):
    index = faiss.read_index(os.getenv("INDEX_FILE"))
    with open(os.getenv("CHUNK_FILE"), "rb") as f:
        id_to_doc = pickle.load(f)
    return [id_to_doc[i] for i in indices]

def truncate_string(s, max_length=100):
    return s[:max_length] + '...' if len(s) > max_length else s

if __name__ == "__main__":
    query = input("Ask an Query to retrieval : ")
    result = retrieve_docs(query, k=5)
    for i, item in enumerate(result, 1) : 
        print(f"[{i}] Score : {item['score']}")
        print(f"Data : {truncate_string(item['text'], max_length=1000)}")
        print("-" * 60)
