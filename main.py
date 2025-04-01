# segmentation_tool/main.py
import os
import numpy as np
from backend.data_processor import DataProcessor
from backend.cluster_engine import ClusterEngine
from backend.visualizations import plot_3d_clusters

def main():
    # Define the path to the data
    data_path = os.path.join("data", "Mall_Customers.csv")
    
    # Initialize the data processor
    processor = DataProcessor()
    
    # Load the data
    if not processor.load_data(file_path=data_path):
        print("Failed to load data. Exiting...")
        return
    
    # Clean and preprocess the data
    if not processor.clean_data():
        print("Failed to clean data. Exiting...")
        return
    
    if not processor.feature_engineering():
        print("Failed to perform feature engineering. Exiting...")
        return
    
    # Apply clustering
    clusterer = ClusterEngine()
    labels = clusterer.apply_clustering(processor.scaled_features)
    print(f"Cluster labels generated: {np.unique(labels)}")
    
    # Analyze clusters
    cluster_summary = clusterer.analyze_clusters(processor.df, processor.feature_columns)
    print("\nCluster Summary (Mean Values for Each Feature):")
    print(cluster_summary)
    
    # Visualize the clusters
    plot_3d_clusters(processor.df, labels)

if __name__ == "__main__":
    main()