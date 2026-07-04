import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

class VectorSearch:
    def __init__(self, data_path, text_column, id_column):
        self.data_path = data_path
        self.text_column = text_column
        self.id_column = id_column
        self.df = None
        self.vectorizer = None
        self.vectors = None
        
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.data_path):
            print(f"Dataset not found: {self.data_path}")
            return
            
        try:
            if self.data_path.endswith('.csv'):
                self.df = pd.read_csv(self.data_path)
            elif self.data_path.endswith('.json'):
                self.df = pd.read_json(self.data_path)
            
            # Fill NaN
            self.df[self.text_column] = self.df[self.text_column].fillna('')
            
            # Fit Vectorizer
            print(f"Fitting vectorizer for {os.path.basename(self.data_path)}...")
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
            self.vectors = self.vectorizer.fit_transform(self.df[self.text_column])
            print("Vectorizer fitted.")
            
        except Exception as e:
            print(f"Error loading data: {e}")

    def search(self, query, top_k=5):
        if self.vectors is None or self.vectorizer is None:
            return []
            
        try:
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.vectors).flatten()
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                score = similarities[idx]
                if score < 0.1: # Threshold
                    continue
                record = self.df.iloc[idx].to_dict()
                record['score'] = float(score)
                results.append(record)
                
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

if __name__ == "__main__":
    # Test
    pass
