import json
import numpy as np
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import pandas as pd
from retriever import retrieve_docs, get_docs

@dataclass
class QueryEvaluation:
    """Data class to store evaluation results for a single query"""
    query_id: str
    query_text: str
    retrieved_docs: List[str] #
    relevant_docs: List[str] #
    precision_at_k: float
    recall_at_k: float
    mean_reciprocal_rank: float

class RAGRetrievalEvaluator:    
    def __init__(self):
        """
        Initialize evaluator with specified K values
        
        """
        # self.k_values = sorted(k_values)
        self.evaluations = []
    
    def precision_at_k(self, retrieved_docs: List[str], relevant_docs: Set[str], k: int) -> float:
        """
        Calculate Precision@K
        
        Args:
            retrieved_docs: List of retrieved document IDs in ranked order
            relevant_docs: Set of relevant document IDs for the query
            k: Number of top documents to consider
            
        Returns:
            Precision@K score (0.0 to 1.0)
        """
        if k == 0 or len(retrieved_docs) == 0:
            return 0.0
            
        top_k = retrieved_docs[:k]
        relevant_in_top_k = [doc for doc in top_k if doc in relevant_docs]
        
        return len(relevant_in_top_k) / k
    
    def recall_at_k(self, retrieved_docs: List[str], relevant_docs: Set[str], k: int) -> float:
        """
        Calculate Recall@K
        
        Args:
            retrieved_docs: List of retrieved document IDs in ranked order
            relevant_docs: Set of relevant document IDs for the query
            k: Number of top documents to consider
            
        Returns:
            Recall@K score (0.0 to 1.0)
        """
            
        if k == 0 or len(retrieved_docs) == 0:
            return 0.0
            
        top_k = retrieved_docs[:k]
        relevant_in_top_k = [doc for doc in top_k if doc in relevant_docs]
        
        return len(relevant_in_top_k)/ len(relevant_docs)
    
    def mean_reciprocal_rank(self, retrieved_docs: List[str], relevant_docs: Set[str]) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR) for a single query
        
        Args:
            retrieved_docs: List of retrieved document IDs in ranked order
            relevant_docs: Set of relevant document IDs for the query
            
        Returns:
            Reciprocal rank (0.0 to 1.0)
        """
        for i, doc in enumerate(retrieved_docs):
            if doc in relevant_docs:
                return 1.0 / (i + 1)  # +1 because ranking starts from 1
        return 0.0
    
    def evaluate_query(self, query_id: str, query_text: str, 
                      retrieved_docs: List[str], relevant_docs: List[str], k: int) -> QueryEvaluation:
        """
        Evaluate retrieval performance for a single query
        
        Args:
            query_id: Unique identifier for the query
            query_text: The actual query text
            retrieved_docs: List of retrieved document IDs in ranked order
            relevant_docs: List of relevant document IDs for the query
            k: Number of top documents to consider
        Returns:
            QueryEvaluation object with all metrics
        """
        relevant_set = set(relevant_docs)
        
        # Calculate Precision@K and Recall@K for all K values
        precision = self.precision_at_k(retrieved_docs, relevant_set, k)
        recall = self.recall_at_k(retrieved_docs, relevant_set, k)
        
        # Calculate MRR
        rr = self.mean_reciprocal_rank(retrieved_docs, relevant_set)
        
        evaluation = QueryEvaluation(
            query_id=query_id,
            query_text=query_text,
            retrieved_docs=retrieved_docs,
            relevant_docs=relevant_docs,
            precision_at_k=precision,
            recall_at_k=recall,
            mean_reciprocal_rank=rr
        )
        
        self.evaluations.append(evaluation)
        return evaluation
    
    def evaluate_dataset(self, evaluation_data: List[Dict], k: int) -> Dict[str, float]:
        """
        Evaluate entire dataset and calculate aggregate metrics
        
        Args:
            evaluation_data: List of dictionaries with keys:
                - query_id: str
                - query_text: str  
                - retrieved_docs: List[str]
                - relevant_docs: List[str]
            k: Number of top documents to consider
        
        Returns:
            Dictionary with aggregate metrics
        """
        self.evaluations = []  # Reset previous evaluations
        
        enrich_data = enrich_docs(evaluation_data, k)
        for data in enrich_data:
            self.evaluate_query(
                query_id=data['query_id'],
                query_text=data['query_text'],
                retrieved_docs=data['retrieved_docs'],
                relevant_docs=data['relevant_docs'],
                k=k
            )
        
        return self.get_aggregate_metrics()
    
    def get_aggregate_metrics(self) -> Dict[str, float]:
        """
        Calculate aggregate metrics across all evaluated queries
        
        Returns:
            Dictionary with mean metrics across all queries
        """
        if not self.evaluations:
            return {}
        
        metrics = {}
        
        # Aggregate Precision@K and Recall@K
        precision_scores = [eval.precision_at_k for eval in self.evaluations]
        recall_scores = [eval.recall_at_k for eval in self.evaluations]
        
        metrics[f'Precision@k'] = np.mean(precision_scores)
        metrics[f'Recall@k'] = np.mean(recall_scores)

        
        # Aggregate MRR
        mrr_scores = [eval.mean_reciprocal_rank for eval in self.evaluations]
        metrics['MRR'] = np.mean(mrr_scores)
        
        return metrics
    
    def get_detailed_results(self) -> pd.DataFrame:
        """
        Get detailed results for all queries in a pandas DataFrame
        
        Returns:
            DataFrame with detailed metrics for each query
        """
        if not self.evaluations:
            return pd.DataFrame()
        
        rows = []
        for eval in self.evaluations:
            row = {
                'query_id': eval.query_id,
                'query_text': eval.query_text,
                'num_retrieved': len(eval.retrieved_docs),
                'num_relevant': len(eval.relevant_docs),
                'mean_reciprocal_rank': eval.mean_reciprocal_rank,
                'precision@k': eval.precision_at_k,
                'recall@k' : eval.recall_at_k
            }
            
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def print_summary(self):
        """Print a formatted summary of evaluation results"""
        if not self.evaluations:
            print("No evaluations performed yet.")
            return
        
        metrics = self.get_aggregate_metrics()
        
        print("=" * 60)
        print("RAG RETRIEVAL EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Queries Evaluated: {len(self.evaluations)}\n")
        
        print(f"PRECISION@K SCORES: {metrics['Precision@k']:.4f}\n")
        print(f"RECALL@K SCORES: {metrics['Recall@k']:.4f}\n")
        print(f"MEAN RECIPROCAL RANK (MRR): {metrics['MRR']:.4f}")
        print("=" * 60)
    
    def save_results(self, filepath: str):
        """
        Save detailed results to CSV file
        
        Args:
            filepath: Path to save the CSV file
        """
        df = self.get_detailed_results()
        df.to_csv(filepath, index=False)
        print(f"Results saved to {filepath}")


def enrich_docs(unit_tests, top_k):
    enriched_unit_test = []

    for ut in unit_tests:
        retrieved = retrieve_docs(ut['query_text'], k=top_k)
        retrieved_texts = [item['text'] for item in retrieved]

        enriched_unit_test.append({
            'query_id': ut['query_id'],
            'query_text': ut['query_text'],
            'retrieved_docs': retrieved_texts,
            'relevant_docs_idx': ut['relevant_docs_idx'],
            'relevant_docs' : get_docs(ut['relevant_docs_idx'])
        })

    return enriched_unit_test


def run_unit_tests(unit_tests, top_k):
    """Run example evaluation"""
    print("Running RAG Retrieval Evaluation...")
    print()
    
    # Initialize evaluator
    evaluator = RAGRetrievalEvaluator()
    
    # Evaluate dataset
    aggregate_metrics = evaluator.evaluate_dataset(unit_tests, k=top_k)
    
    # Print summary
    evaluator.print_summary()
    
    # Show detailed results
    print("\nDETAILED RESULTS:")
    df = evaluator.get_detailed_results()
    print(df.to_string(index=False))

    # Optionally save results
    evaluator.save_results('./evaluation/retrieval_evaluation.csv')
    print("[v] Retrieval Evaluation saved to csv file")
    
    return evaluator, aggregate_metrics

if __name__ == "__main__":
    test_cases = [
        {
            'query_id': 'Q1',
            'query_text': 'Berikan saya rekomendasi handphone dengan brand xiaomi',
            'relevant_docs_idx': [8, 14]  
        },
        {
            'query_id': 'Q2', 
            'query_text': 'Berikan saya rekomendasi serum dengan diskon terbesar',
            'relevant_docs_idx': [31, 28, 32]  
        },
        {
            'query_id': 'Q3',
            'query_text': 'Popok bayi dengan harga paling termurah',
            'relevant_docs_idx': [61, 53, 52, 54, 58] 
        },
        {
            'query_id': 'Q4',
            'query_text': 'Berapa saja kapasitas penyimpanan yang tersedia untuk Iphone 15?',
            'relevant_docs_idx': [9] 
        },
        {
            'query_id': 'Q5',
            'query_text': 'Apakah produk infinix smart 8 merupakan barang baru?',
            'relevant_docs_idx': [12] 
        }
    ]
    # Run Unit Test
    evaluator, metrics = run_unit_tests(unit_tests=test_cases, top_k=5)
