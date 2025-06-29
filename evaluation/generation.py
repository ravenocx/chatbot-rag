from typing import List, Dict
import evaluate
from rag.inference import generate_response
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
            'query_text': 'waterproof smartphone under $500',
            'reference': 'reference'  
        },
        {
            'query_id': 'Q2', 
            'query_text': 'gaming laptop with RTX 4060',
            'reference': 'reference'  
        },
        {
            'query_id': 'Q3',
            'query_text': 'wireless headphones noise cancelling',
            'reference': 'reference' 
        },
        {
            'query_id': 'Q4',
            'query_text': 'wireless headphones noise cancelling',
            'reference': 'reference' 
        },
        {
            'query_id': 'Q5',
            'query_text': 'wireless headphones noise cancelling',
            'reference': 'reference' 
        }
    ]

    evaluator = RAGGenerationEvaluator(unit_tests=test_cases)

    metrics, tc = evaluator.evaluate_generation(top_k=3, lang="id")

    print_summary(metrics=metrics, tc=tc)

    save_result(metrics=metrics, filepath='./evaluation/generation_evaluation.csv')
