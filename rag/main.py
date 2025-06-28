import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
from retriever import retrieve

model_id = "meta-llama/Llama-3.3-70B-Instruct"

bnb_config= BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,
    llm_int8_has_fp16_weight=False
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, 
                                             device_map="auto", 
                                             torch_dtype=torch.bfloat16, 
                                             quantization_config=bnb_config)

llm = pipeline("text-generation", model=model, tokenizer=tokenizer)

# prompt to LLM
def rag_ask(query: str, k=3, max_tokens=1024):
    # Step 1: Get relevant passages
    retrieved_docs = retrieve(query, k=k)
    context = "\n\n".join([f"{i+1}. {doc['text']}" for i, doc in enumerate(retrieved_docs)])

    # Step 2: Build the prompt
    prompt = f"""You are a helpful assistant for an e-commerce platform.
Answer the user's question based on the context below.

Context:
{context}

Question:
{query}

Answer:"""

    # Step 3: Generate answer
    result = llm(prompt, max_new_tokens=max_tokens, do_sample=False)
    return result[0]["generated_text"][len(prompt):].strip()

if __name__ == "__main__":
    query = input("Query: ")
    result = rag_ask(query)
    print(result)