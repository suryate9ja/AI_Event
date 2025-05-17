import numpy as np
from typing import List, Dict, Any
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
import spacy
import pandas as pd

class GuestAnalyzer:
    def __init__(self):
        """
        Initialize the guest analyzer with NLP models.
        """
        self.nlp = spacy.load("en_core_web_sm")
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.vectorizer = TfidfVectorizer(max_features=1000)
        
    def analyze_guest_data(self, guest_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Analyze guest data and extract features.
        
        Args:
            guest_data (List[Dict[str, Any]]): List of guest information
            
        Returns:
            pd.DataFrame: Processed guest data with features
        """
        processed_data = []
        
        for guest in guest_data:
            # Extract text features
            text = f"{guest.get('name', '')} {guest.get('title', '')} {guest.get('company', '')}"
            doc = self.nlp(text)
            
            # Extract named entities
            entities = [ent.text for ent in doc.ents]
            
            # Analyze sentiment if description is available
            sentiment = None
            if 'description' in guest:
                sentiment = self.sentiment_analyzer(guest['description'])[0]
            
            processed_data.append({
                'name': guest.get('name', ''),
                'title': guest.get('title', ''),
                'company': guest.get('company', ''),
                'entities': entities,
                'sentiment': sentiment['label'] if sentiment else None,
                'sentiment_score': sentiment['score'] if sentiment else None
            })
            
        return pd.DataFrame(processed_data)
    
    def cluster_guests(self, guest_df: pd.DataFrame, 
                      eps: float = 0.5, 
                      min_samples: int = 2) -> Dict[int, List[str]]:
        """
        Cluster guests based on their features.
        
        Args:
            guest_df (pd.DataFrame): Processed guest data
            eps (float): Maximum distance between samples for DBSCAN
            min_samples (int): Minimum number of samples in a cluster
            
        Returns:
            Dict[int, List[str]]: Clusters of guest names
        """
        # Prepare text data for clustering
        text_data = guest_df.apply(
            lambda x: f"{x['title']} {x['company']} {' '.join(x['entities'])}", 
            axis=1
        )
        
        # Convert text to TF-IDF features
        features = self.vectorizer.fit_transform(text_data)
        
        # Perform clustering
        clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        clusters = clustering.fit_predict(features)
        
        # Group guests by cluster
        cluster_groups = {}
        for i, cluster_id in enumerate(clusters):
            if cluster_id not in cluster_groups:
                cluster_groups[cluster_id] = []
            cluster_groups[cluster_id].append(guest_df.iloc[i]['name'])
            
        return cluster_groups
    
    def get_guest_insights(self, guest_df: pd.DataFrame, 
                          clusters: Dict[int, List[str]]) -> Dict[str, Any]:
        """
        Generate insights about guests and their clusters.
        
        Args:
            guest_df (pd.DataFrame): Processed guest data
            clusters (Dict[int, List[str]]): Clusters of guest names
            
        Returns:
            Dict[str, Any]: Insights about guests and clusters
        """
        insights = {
            'total_guests': len(guest_df),
            'cluster_count': len(clusters),
            'cluster_sizes': {k: len(v) for k, v in clusters.items()},
            'company_distribution': guest_df['company'].value_counts().to_dict(),
            'title_distribution': guest_df['title'].value_counts().to_dict(),
            'sentiment_distribution': guest_df['sentiment'].value_counts().to_dict()
        }
        
        # Calculate average sentiment score per cluster
        cluster_sentiments = {}
        for cluster_id, names in clusters.items():
            cluster_guests = guest_df[guest_df['name'].isin(names)]
            cluster_sentiments[cluster_id] = {
                'avg_sentiment_score': cluster_guests['sentiment_score'].mean(),
                'size': len(names)
            }
            
        insights['cluster_sentiments'] = cluster_sentiments
        
        return insights 