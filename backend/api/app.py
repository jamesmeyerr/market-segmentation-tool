# segmentation_tool/backend/api/app.py
from flask import Flask, request, jsonify
import os
from ..data_processor import DataProcessor
from ..cluster_engine import ClusterEngine

app = Flask(__name__)

# Define the path to the default data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "Mall_Customers.csv")

@app.route('/api/segment', methods=['GET'])
def segment_customers():
    """
    Run the segmentation pipeline and return the clustering results.
    For now, uses the default Mall_Customers.csv file.
    """
    try:
        # Initialize the data processor
        processor = DataProcessor()
        
        # Load the data
        if not processor.load_data(file_path=DATA_PATH):
            return jsonify({"error": "Failed to load data"}), 500
        
        # Clean and preprocess the data
        if not processor.clean_data():
            return jsonify({"error": "Failed to clean data"}), 500
        
        if not processor.feature_engineering():
            return jsonify({"error": "Failed to perform feature engineering"}), 500
        
        # Apply clustering
        clusterer = ClusterEngine()
        labels = clusterer.apply_clustering(processor.scaled_features)
        
        # Analyze clusters
        cluster_summary = clusterer.analyze_clusters(processor.df, processor.feature_columns)
        
        # Prepare the response
        response = {
            "cluster_labels": labels.tolist(),  # Convert numpy array to list for JSON serialization
            "cluster_summary": cluster_summary.to_dict(),  # Convert DataFrame to dict
            "message": "Segmentation completed successfully"
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "API is running"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)