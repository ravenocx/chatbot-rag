import faiss
import os
import pickle
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

def get_detailed_instruct(task_description: str, query: str) -> str:
    return f'Instruct: {task_description}\nQuery: {query}'

def retrieve_docs(qry, k=3) :
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

def get_docs(index):
    index = faiss.read_index(os.getenv("INDEX_FILE"))
    with open(os.getenv("CHUNK_FILE"), "rb") as f:
        id_to_doc = pickle.load(f)
    return id_to_doc[index]

if __name__ == "__main__":
    query = input("Ask an Query to retrieval : ")
    result = retrieve_docs(query)
    for i, item in enumerate(result, 1) : 
        print(f"[{i}] Score : {item['score']}")
        print(f"Data : {item['text']}")
        print("-" * 60)
