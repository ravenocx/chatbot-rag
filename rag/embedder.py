import rag.db.database as db
import rag.helpers.document_utils as utils
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
import faiss

def embedd_product_data(db_conn): 
    products = db.get_all_products(db_conn)
    attributes = db.get_all_attributes(db_conn)

    print("📝 Generating product documents...")
    documents = utils.generate_product_documents(products, attributes)
    print(f"✅ Success Generated {len(documents)} documents")

    # Check if the document exceed token limit
    tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
    texts = [f"Passage: {doc.page_content}" for doc in documents]

    for i, text in enumerate(texts):
        tokens = tokenizer.encode(text, truncation=False)
        # print(f"Doc {i} → {len(tokens)} tokens")

        if len(tokens) > 8194:
            print(f"⚠️ Doc {i} Exceeds token limit! Token: ", len(tokens))
    
    # Embedd product data
    model = SentenceTransformer('BAAI/bge-m3')

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True  # for cosine similarity
    )
    print(f"✅ Embeddings created with shape: {embeddings.shape}")

    # Store embedding data
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)
    print(f"✅ Added {embeddings.shape[0]} vectors to FAISS index")

    # Export FAISS Index
    faiss.write_index(index, "data/tokopoin_product.index")
    print("💾 Successfully export index data")
    

if __name__ == "__main__":
    import db.database as db
    conn = db.db_connection()

    embedd_product_data(conn)
    