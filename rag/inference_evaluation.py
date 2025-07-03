from typing import List, Dict
import evaluate
from inference import generate_response, model, tokenizer
import pandas as pd
import torch
import math

class RAGGenerationEvaluator:    
    def __init__(self, unit_tests: List[Dict], model, tokenizer):
        """
        Load the evaluator from huggingface
        
        """
        self.unit_tests = unit_tests
        self.model = model
        self.tokenizer = tokenizer
        self.rouge = evaluate.load("rouge")
        self.bertscore = evaluate.load("bertscore")

    def compute_perplexity(self, texts: List[str]) -> float:
        self.model.eval()

        ppl_scores = []
        for text in texts:
            inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                outputs = self.model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
            ppl_scores.append(math.exp(loss.item()))
        return round(sum(ppl_scores) / len(ppl_scores), 4)

    def compute_rouge(self, predictions: List[str], references: List[str]) -> dict:
        result = self.rouge.compute(predictions=predictions, references=references)
        return {k: round(v, 4) for k, v in result.items()}

    def compute_bertscore(self, predictions: List[str], references: List[str], lang="id") -> float:
        result = self.bertscore.compute(predictions=predictions, references=references, lang=lang)
        return round(sum(result["f1"]) / len(result["f1"]), 4)

    def enrich_predictions(self, top_k):
        enriched_unit_test = []

        for ut in self.unit_tests:
            prediction = generate_response(ut['query_text'], k=top_k)

            enriched_unit_test.append({
                'query_id': ut['query_id'],
                'query_text': ut['query_text'],
                'reference': ut['reference'],
                'prediction' : prediction
            })

        return enriched_unit_test
    
    def evaluate_generation(self, top_k=5, lang="id"):
        enriched_test_cases = self.enrich_predictions(top_k=top_k)

        predictions =[tc['prediction'] for tc in enriched_test_cases]
        references = [tc['reference'] for tc in enriched_test_cases]
        metrics = {
            "Perplexity": self.compute_perplexity(predictions),
            "ROUGE": self.compute_rouge(predictions, references),
            "BERTScore": self.compute_bertscore(predictions, references, lang=lang)
        }
        return metrics, enriched_test_cases


def print_summary(metrics: dict, tc: list):
    print("=" * 60)
    print("RAG GENERATION EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total Queries Evaluated: {len(tc)}\n")
    
    print(f"Perplexity: {metrics['Perplexity']:.4f}\n")
    print(f"ROUGE: {metrics['ROUGE']}\n")
    print(f"BERT Score: {metrics['BERTScore']:.4f}")
    print("=" * 60)

    print("\n--- Enriched Unit Tests ---")
    for t in tc:
        print(f"Query ID   : {t['query_id']}")
        print(f"Query Text : {t['query_text']}")
        print(f"Reference  : {t['reference']}")
        print("-" * 10)
        print(f"Prediction : {t['prediction']}")
        print("=" * 60)

def save_result(metrics:dict ,filepath: str):
    flat_metrics = metrics.copy()
    rouge = flat_metrics.pop("ROUGE", {})
    for key, value in rouge.items():
        flat_metrics[f"ROUGE_{key}"] = value
    df = pd.DataFrame([flat_metrics])
    df.to_csv(filepath, index=False)
    print(f"[v] Generation Evaluation saved to {filepath}")
    

# Example usage
if __name__ == "__main__":
    test_cases = [
        {
            'query_id': 'Q1',
            'query_text': 'Apakah produk Xiaomi Redmi A2 merupakan barang baru?',
            'reference': 'Produk Xiaomi Redmi A2 3/32 GB dengan kondisi Grade C bukan barang baru, melainkan handphone bekas yang memiliki lecet sekitar 85%. Jika Anda menginginkan produk baru, pertimbangkan Xiaomi 14T 12/512GB yang dijual dalam kondisi baru 100% dengan garansi resmi dari Xiaomi Indonesia selama 2 tahun dan harga sekitar Rp6.299.000.'  
        },
        {
            'query_id': 'Q2', 
            'query_text': 'Apakah produk Lenovo Yoga Slim 7i cocok untuk kuliah informatika?',
            'reference': 'Produk Lenovo Yoga Slim 7i sangat sesuai untuk kebutuhan kuliah di jurusan informatika. Laptop ini ditenagai prosesor Intel Core Ultra 7 155H dan RAM 16GB, sehingga mampu menangani aktivitas seperti coding, desain grafis, hingga analisis data. Layarnya yang berukuran 14 inci berjenis OLED dengan resolusi 1920x1200 dan refresh rate 60Hz memberikan tampilan visual yang tajam. Dengan harga sekitar Rp18.859.080 setelah diskon, perangkat ini menjadi pilihan ideal bagi mahasiswa yang memerlukan laptop berkinerja tinggi.'  
        },
        {
            'query_id': 'Q3',
            'query_text': 'Fitur apa saja yang dimiliki produk Iphone 15?',
            'reference': 'Produk iPhone 15 hadir dengan layar Super Retina XDR 6,1 inci berteknologi OLED dan resolusi tinggi 2556 x 1179 piksel. Smartphone ini ditenagai oleh chip A16 Bionic dengan CPU 6-core, GPU 5-core, dan Neural Engine 16-core, yang menawarkan performa tinggi. Sistem kameranya mencakup kamera utama 48MP, ultra-wide 12MP, dan telephoto 12MP 2x zoom, serta mendukung perekaman video hingga resolusi 4K. Tersedia dalam varian 128GB dan 256GB, produk ini juga bergaransi resmi iBox selama 1 tahun. Dengan fitur-fitur lengkap dan desain premium, iPhone 15 cocok untuk pengguna yang menginginkan performa maksimal dalam aktivitas sehari-hari.' 
        },
        {
            'query_id': 'Q4',
            'query_text': 'Bagaimana cara penggunaan skincare Moisturizer SKINTIFIC?',
            'reference': 'Moisturizer SKINTIFIC digunakan setelah mencuci wajah dan mengaplikasikan toner atau serum. Ambil produk secukupnya lalu usapkan merata ke wajah dan leher. Pada pagi hari, lanjutkan dengan penggunaan sunscreen untuk perlindungan ekstra. Moisturizer ini membantu menjaga kelembaban kulit, memperkuat skin barrier, dan membuat kulit terasa lebih lembut. Produk tersedia dalam ukuran 30 ml dengan harga Rp135.000 dan ongkos kirim sebesar Rp15.000. Nomor BPOM-nya adalah NA11230100349 dan dapat dibeli mulai dari 1 hingga 100 unit.' 
        },
        {
            'query_id': 'Q5',
            'query_text': 'Berikan saya rekomendasi produk handphone dengan brand xiaomi',
            'reference': 'Untuk Anda yang mencari handphone dari brand Xiaomi, tersedia beberapa pilihan menarik. Salah satunya adalah Xiaomi 14T 12/512GB, produk baru dengan segel asli dan garansi resmi dari Xiaomi Indonesia selama 2 tahun. Memiliki spesifikasi tinggi dengan RAM 12GB dan penyimpanan 512GB, cocok untuk pengguna yang menginginkan performa optimal. Harganya Rp6.299.000 dan biaya pengiriman Rp11.199. Jika Anda memiliki anggaran terbatas, tersedia juga opsi Xiaomi Redmi A2 bekas (Grade C) dengan RAM 3GB dan penyimpanan 32GB, dijual seharga Rp575.000. Namun karena kondisinya second dan terdapat lecet 85%, sesuaikan dengan kebutuhan Anda. Kami siap membantu jika Anda membutuhkan saran lebih lanjut.' 
        }
    ]

    print("Running RAG Generation Evaluation...")
    print()
    evaluator = RAGGenerationEvaluator(unit_tests=test_cases, model=model, tokenizer=tokenizer)

    metrics, tc = evaluator.evaluate_generation(top_k=5, lang="id")

    print_summary(metrics=metrics, tc=tc)

    save_result(metrics=metrics, filepath='./evaluation/generation_evaluation.csv')
