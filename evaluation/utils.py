import json
import numpy as np
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import pandas as pd

@dataclass
class QueryEvaluation:
    """Data class to store evaluation results for a single query"""
    query_id: str
    query_text: str
    retrieved_docs: List[str] #
    relevant_docs: List[str] #
    precision_at_k: Dict[int, float]
    recall_at_k: Dict[int, float]
    mean_reciprocal_rank: float

class RAGRetrievalEvaluator:    
    def __init__(self, k_values: List[int] = [1, 3, 5, 10]):
        """
        Initialize evaluator with specified K values
        
        Args:
            k_values: List of K values to evaluate (e.g., [1, 3, 5, 10])
        """
        self.k_values = sorted(k_values)
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
                      retrieved_docs: List[str], relevant_docs: List[str]) -> QueryEvaluation:
        """
        Evaluate retrieval performance for a single query
        
        Args:
            query_id: Unique identifier for the query
            query_text: The actual query text
            retrieved_docs: List of retrieved document IDs in ranked order
            relevant_docs: List of relevant document IDs for the query
            
        Returns:
            QueryEvaluation object with all metrics
        """
        relevant_set = set(relevant_docs)
        
        # Calculate Precision@K and Recall@K for all K values
        precision_scores = {}
        recall_scores = {}
        
        for k in self.k_values:
            precision_scores[k] = self.precision_at_k(retrieved_docs, relevant_set, k)
            recall_scores[k] = self.recall_at_k(retrieved_docs, relevant_set, k)
        
        # Calculate MRR
        rr = self.mean_reciprocal_rank(retrieved_docs, relevant_set)
        
        evaluation = QueryEvaluation(
            query_id=query_id,
            query_text=query_text,
            retrieved_docs=retrieved_docs,
            relevant_docs=relevant_docs,
            precision_at_k=precision_scores,
            recall_at_k=recall_scores,
            mean_reciprocal_rank=rr
        )
        
        self.evaluations.append(evaluation)
        return evaluation
    
    def evaluate_dataset(self, evaluation_data: List[Dict]) -> Dict[str, float]:
        """
        Evaluate entire dataset and calculate aggregate metrics
        
        Args:
            evaluation_data: List of dictionaries with keys:
                - query_id: str
                - query_text: str  
                - retrieved_docs: List[str]
                - relevant_docs: List[str]
        
        Returns:
            Dictionary with aggregate metrics
        """
        self.evaluations = []  # Reset previous evaluations
        
        for data in evaluation_data:
            self.evaluate_query(
                query_id=data['query_id'],
                query_text=data['query_text'],
                retrieved_docs=data['retrieved_docs'],
                relevant_docs=data['relevant_docs']
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
        for k in self.k_values:
            precision_scores = [eval.precision_at_k[k] for eval in self.evaluations]
            recall_scores = [eval.recall_at_k[k] for eval in self.evaluations]
            
            metrics[f'Precision@{k}'] = np.mean(precision_scores)
            metrics[f'Recall@{k}'] = np.mean(recall_scores)
        
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
                'mean_reciprocal_rank': eval.mean_reciprocal_rank
            }
            
            # Add Precision@K and Recall@K columns
            for k in self.k_values:
                row[f'Precision@{k}'] = eval.precision_at_k[k]
                row[f'Recall@{k}'] = eval.recall_at_k[k]
            
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
        print(f"Total Queries Evaluated: {len(self.evaluations)}")
        print()
        
        print("PRECISION@K SCORES:")
        for k in self.k_values:
            print(f"  Precision@{k}: {metrics[f'Precision@{k}']:.4f}")
        
        print("\nRECALL@K SCORES:")
        for k in self.k_values:
            print(f"  Recall@{k}: {metrics[f'Recall@{k}']:.4f}")
        
        print(f"\nMEAN RECIPROCAL RANK (MRR): {metrics['MRR']:.4f}")
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

# Example usage and testing
def create_sample_data():
    """Create sample evaluation data for testing"""
    return [
        {
            'query_id': 'q1',
            'query_text': 'waterproof smartphone under $500',
            'retrieved_docs': ['doc1', 'doc2', 'doc3', 'doc4', 'doc5'],
            'relevant_docs': ['doc1', 'doc3', 'doc7']  # doc7 not retrieved
        },
        {
            'query_id': 'q2', 
            'query_text': 'gaming laptop with RTX 4060',
            'retrieved_docs': ['doc8', 'doc9', 'doc10', 'doc11'],
            'relevant_docs': ['doc8', 'doc9']
        },
        {
            'query_id': 'q3',
            'query_text': 'wireless headphones noise cancelling',
            'retrieved_docs': ['doc12', 'doc13', 'doc14', 'doc15', 'doc16'],
            'relevant_docs': ['doc13', 'doc14', 'doc17', 'doc18']  # some not retrieved
        }
    ]

def run_example():
    """Run example evaluation"""
    print("Running RAG Retrieval Evaluation Example...")
    print()
    
    # Initialize evaluator
    evaluator = RAGRetrievalEvaluator(k_values=[1, 3, 5])
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Evaluate dataset
    aggregate_metrics = evaluator.evaluate_dataset(sample_data)
    
    # Print summary
    evaluator.print_summary()
    
    # Show detailed results
    print("\nDETAILED RESULTS:")
    df = evaluator.get_detailed_results()
    print(df.to_string(index=False))
    
    return evaluator, aggregate_metrics

if __name__ == "__main__":
    # Run example
    evaluator, metrics = run_example()
    
    # Optionally save results
    # evaluator.save_results('rag_evaluation_results.csv')