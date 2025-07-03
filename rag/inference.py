import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
from huggingface_hub import login
from rag.retriever import retrieve_docs

login(token=os.getenv("HUGGINGFACE_TOKEN"))

model_id = "meta-llama/Llama-3.3-70B-Instruct"

bnb_config= BitsAndBytesConfig(
    load_in_4bit=True,
    llm_int8_threshold=6.0,
    llm_int8_has_fp16_weight=False, 
    # bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, 
                                             device_map="auto", 
                                             torch_dtype=torch.bfloat16, 
                                             quantization_config=bnb_config)

print("Model device:", next(model.parameters()).device)

llm = pipeline("text-generation", model=model, tokenizer=tokenizer)

print("CUDA available:", torch.cuda.is_available())
print("CUDA device count:", torch.cuda.device_count())

def generate_response(query: str, k=5, max_tokens=4096):
    # Get relevant passages
    docs = retrieve_docs(query, k=k)
    context = "\n\n".join([f"{i+1}. {doc['text']}" for i, doc in enumerate(docs)])

    prompt = f"""You are a highly accurate e-commerce chatbot assistant expert. Your main role is to help customers find product information and provide recommendations based **ONLY** on the provided product data.

CRITICAL INSTRUCTIONS:
1.  **LANGUAGE:** ALWAYS respond in Bahasa Indonesia. The product data provided is also in Bahasa Indonesia - use this data directly without translation.
2.  **DATA ACCURACY:** Base your answer ENTIRELY and SOLELY on the information within the provided data below. Do NOT use any external knowledge or make assumptions about products.
3.  **RELEVANCE FILTER:** ONLY extract and use the specific parts of the product data that are directly relevant to the user's question. If there is clearly no relevant information AT ALL within the data, respond with: "Maaf, informasi yang Anda cari tidak tersedia dalam data kami saat ini." Otherwise, answer based ONLY on the RELEVANT parts.

PROVIDED PRODUCT DATA:
{context}

USER QUESTION: {query}

ADDITIONAL RESPONSE GUIDELINES:
- If recommending products, explain why based on the available product specifications
- Be specific about product features, prices, and availability as mentioned in the data
- Use a friendly, professional tone typical of Indonesian customer service

ANSWER:"""

    result = llm(prompt, max_new_tokens=max_tokens, do_sample=False)
    return result[0]["generated_text"][len(prompt):].strip()

if __name__ == "__main__":
    query = input("Ask an Query to generate answer from LLMs: ")
    result = generate_response(query)
    print(f"Answer:\n{result}")