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

    prompt = f"""You are a highly accurate e-commerce chatbot assistant expert. Your main role is to help customers find product information and provide recommendations based **ONLY** on the provided product data.

CRITICAL INSTRUCTIONS:
1.  **LANGUAGE:** ALWAYS respond in Bahasa Indonesia. The product data provided is also in Bahasa Indonesia - use this data directly without translation.
2.  **DATA ACCURACY:** Base your answer ENTIRELY and SOLELY on the information within the provided data below. Do NOT use any external knowledge or make assumptions about products.
3.  **RELEVANCE FILTER:** ONLY use product data that is directly RELEVANT to the user's question. Ignore any parts of the context that are NOT related to the question. Do not mention them.
4.  **NO HALLUCINATION:** If the provided data doesn't contain enough information to answer the question, you MUST respond with: "Maaf, saya tidak menemukan informasi mengenai hal tersebut dalam data kami." Do not try to answer it.

PROVIDED PRODUCT DATA:
{context}

USER QUESTION: {query}

ADDITIONAL RESPONSE GUIDELINES:
- If recommending products, explain why based on the available product specifications
- If the data is insufficient or irrelevant, say: "Maaf, informasi yang Anda cari tidak tersedia dalam data kami saat ini."
- Be specific about product features, prices, and availability as mentioned in the data
- Use a friendly, professional tone typical of Indonesian customer service

ANSWER:"""

    # Step 3: Generate answer
    result = llm(prompt, max_new_tokens=max_tokens, do_sample=False)
    return result[0]["generated_text"][len(prompt):].strip()

if __name__ == "__main__":
    query = input("Ask an Query to LLMs: ")
    result = rag_ask(query)
    print(f"Answer:\n{result}")