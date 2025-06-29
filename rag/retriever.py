import faiss
import os
import pickle
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Cache variables (load once)
_index = None
_id_to_doc = None
_model = None

def load_resources():
    global _index, _id_to_doc, _model
    if _index is None or _id_to_doc is None or _model is None:
        load_dotenv()
        _index = faiss.read_index(os.getenv("INDEX_FILE"))
        with open(os.getenv("CHUNK_FILE"), "rb") as f:
            _id_to_doc = pickle.load(f)
        _model = SentenceTransformer("BAAI/bge-m3")

def get_detailed_instruct(task_description: str, query: str) -> str:
    return f'Instruct: {task_description}\nQuery: {query}'

def retrieve_docs(qry, k=3) :
    load_resources()

    task = "Given a user’s product-related query, retrieve the most relevant and informative product descriptions, specifications, or recommendations that directly address the query."

    embedding = _model.encode(
        get_detailed_instruct(task, qry),
        convert_to_numpy=True,
        normalize_embeddings=True
    ).reshape(1, -1)


    # Distance & Indices
    D, I = _index.search(embedding, k)

    return [{"text": _id_to_doc[i], "score": float(D[0][idx])} for idx, i in enumerate(I[0])]

def get_docs(index):
    load_resources()
    return _id_to_doc[index]


if __name__ == "__main__":
    query = input("Ask an Query: ")
    result = retrieve_docs(query)
    for i, item in enumerate(result, 1) : 
        print(f"[{i}] Score : {item['score']}")
        print(f"Data : {item['text']}")
        print("-" * 60)
