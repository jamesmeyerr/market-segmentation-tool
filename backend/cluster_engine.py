# segmentation_tool/backend/cluster_engine.py
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
import numpy as np

class ClusterEngine:
    def __init__(self):
        self.clusters = None
        self.labels = None
        
    def find_optimal_kmeans(self, data, max_k=10):
        """Find optimal number of clusters using silhouette score"""
        silhouette_scores = []
        
        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(data)
            silhouette_scores.append(silhouette_score(data, kmeans.labels_))
        
        # Choose k with max silhouette score
        optimal_k = np.argmax(silhouette_scores) + 2  # +2 because we start at k=2
        return optimal_k

    def apply_clustering(self, data, method='kmeans', n_clusters=None, weights=None):
        """Apply clustering with optional attribute weights"""
        if weights is not None:
            data = data * weights
            
        if method == 'kmeans':
            if n_clusters is None:
                n_clusters = self.find_optimal_kmeans(data)
            self.clusters = KMeans(n_clusters=n_clusters, random_state=42)
            
        elif method == 'dbscan':
            self.clusters = DBSCAN(eps=0.5, min_samples=5)
            
        self.labels = self.clusters.fit_predict(data)
        return self.labels

    def analyze_clusters(self, df, feature_columns):
        """Analyze the characteristics of each cluster"""
        df['Cluster'] = self.labels
        cluster_summary = df.groupby('Cluster')[feature_columns].mean()
        return cluster_summary