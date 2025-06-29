from typing import List, Dict
import evaluate
from inference import generate_response
import pandas as pd


class RAGGenerationEvaluator:    
    def __init__(self, unit_tests: List[Dict]):
        """
        Load the evaluator from huggingface
        
        """
        self.unit_tests = unit_tests
        self.rouge = evaluate.load("rouge")
        self.bertscore = evaluate.load("bertscore")
        self.f1_metric = evaluate.load("f1")

    def compute_f1(self, predictions: List[str], references: List[str]) -> float:
        scores = []
        for pred, ref in zip(predictions, references):
            score = self.f1_metric.compute(predictions=[pred], references=[ref])["f1"]
            scores.append(score)
        return sum(scores) / len(scores)

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
    
    def evaluate_generation(self, top_k=3, lang="id"):
        enriched_test_cases = self.enrich_predictions(top_k=top_k)

        predictions =[tc['prediction'] for tc in enriched_test_cases]
        references = [tc['reference'] for tc in enriched_test_cases]
        metrics = {
            "F1 Score": round(self.compute_f1(predictions, references), 4),
            "ROUGE": self.compute_rouge(predictions, references),
            "BERTScore": self.compute_bertscore(predictions, references, lang=lang)
        }
        return metrics, enriched_test_cases


def print_summary(metrics: dict, tc: list):
    print("=" * 60)
    print("RAG GENERATION EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total Queries Evaluated: {len(tc)}\n")
    
    print(f"F1 Score: {metrics['F1 Score']:.4f}\n")
    print(f"ROUGE: {metrics['ROUGE']}\n")
    print(f"BERT Score: {metrics['BERTScore']:.4f}")
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
            'reference': 'Produk ini merupakan HP Xiaomi Redmi A2 yang dijual dalam kondisi tidak baru, atau second, dan tersedia dalam beberapa grade kualitas seperti Grade A, B, C, dan X. Meskipun bekas, penjual memberikan garansi toko selama 7 hari dan menyertakan kelengkapan seperti dus original dan charger OEM.'  
        },
        {
            'query_id': 'Q2', 
            'query_text': 'Apakah produk Lenovo Yoga Slim 7i cocok untuk kuliah informatika?',
            'reference': 'Laptop Lenovo Yoga Slim 7i ini sudah cukup cocok untuk menunjang kebutuhan kuliah di jurusan informatika. Performanya sangat mumpuni berkat prosesor terbaru Intel Core Ultra 7 155H yang memiliki 16 core, kapasitas RAM 16GB LPDDR5x yang sangat cepat dan 1TB SSD PCIe 4.0 memastikan aktivitas multitasking berjalan tanpa hambatan serta menyediakan ruang penyimpanan yang lebih dari cukup untuk proyek-proyek besar.'  
        },
        {
            'query_id': 'Q3',
            'query_text': 'Jelaskan fitur lengkap dari produk Iphone 15',
            'reference': 'Produk iPhone 15 menawarkan serangkaian fitur lengkap yang berpusat pada performa dan kualitas kamera. Produk ini hadir dengan layar OLED berukuran 6.1 inci dan menggunakan chip A16 Bionic. Kamera utamanya 48MP dengan dukungan pengambilan gambar resolusi tinggi, serta memiliki fitur video 4K. Tersedia dalam beberapa varian penyimpanan dan menggunakan konektor USB-C. Semua fitur ini berjalan pada sistem operasi iOS 17 dan produk ini disertai dengan garansi resmi iBox selama satu tahun.' 
        },
        {
            'query_id': 'Q4',
            'query_text': 'Bagaimana cara penggunaan skincare Moisturizer SKINTIFIC?',
            'reference': 'Gunakan moisturizer ini setelah membersihkan wajah dan memakai toner. Setelah wajah dibersihkan, aplikasikan moisturizer secara merata pada wajah dan leher. Oleskan secara merata ke wajah untuk menjaga kelembaban dan kesehatan kulit, serta gunakan pada pagi dan malam hari untuk hasil maksimal.' 
        },
        {
            'query_id': 'Q5',
            'query_text': 'Berikan saya rekomendasi produk handphone dengan brand xiaomi',
            'reference': 'Terdapat dua rekomendasi produk Xiaomi yang sangat berbeda yang dapat disesuaikan dengan kebutuhan Anda. Jika Anda mencari ponsel baru dengan performa tinggi, ruang penyimpanan sangat besar, dan jaminan jangka panjang, maka Xiaomi 14T adalah pilihan yang sangat direkomendasikan. Ponsel ini datang dalam kondisi baru (BNIB) dengan spesifikasi RAM 12 GB dan penyimpanan 512 GB. Sebaliknya, jika Anda memiliki anggaran yang sangat terbatas dan mencari ponsel untuk kebutuhan dasar, anda bisa mempertimbangkan Xiaomi Redmi A2 second. Produk ini adalah ponsel bekas dengan spesifikasi 3 GB RAM dan 32 GB penyimpanan yang dijual dalam kondisi Grade C atau memiliki lecet.' 
        }
    ]

    evaluator = RAGGenerationEvaluator(unit_tests=test_cases)

    metrics, tc = evaluator.evaluate_generation(top_k=3, lang="id")

    print_summary(metrics=metrics, tc=tc)

    save_result(metrics=metrics, filepath='./evaluation/generation_evaluation.csv')
