# segmentation_tool/backend/api/app.py
from flask import Flask, request, jsonify
import os
import pandas as pd
from ..data_processor import DataProcessor
from ..cluster_engine import ClusterEngine

app = Flask(__name__)

# Define the path to the default data
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "Mall_Customers.csv")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create uploads directory if it doesn't exist

def run_segmentation(file_path, n_clusters=None, method='kmeans'):
    """Helper function to run the segmentation pipeline"""
    try:
        # Initialize the data processor
        processor = DataProcessor()
        
        # Load the data
        if not processor.load_data(file_path=file_path):
            return None, "Failed to load data"
        
        # Clean and preprocess the data
        if not processor.clean_data():
            return None, "Failed to clean data"
        
        if not processor.feature_engineering():
            return None, "Failed to perform feature engineering"
        
        # Apply clustering
        clusterer = ClusterEngine()
        labels = clusterer.apply_clustering(processor.scaled_features, method=method, n_clusters=n_clusters)
        
        # Analyze clusters
        cluster_summary = clusterer.analyze_clusters(processor.df, processor.feature_columns)
        
        return {
            "cluster_labels": labels.tolist(),
            "cluster_summary": cluster_summary.to_dict(),
            "message": "Segmentation completed successfully"
        }, None
    except Exception as e:
        return None, str(e)

@app.route('/api/segment', methods=['GET'])
def segment_customers():
    """
    Run the segmentation pipeline on the default dataset with optional query parameters.
    Query Parameters:
    - n_clusters: Number of clusters (optional, default: auto-determined)
    - method: Clustering method (optional, default: 'kmeans', options: 'kmeans', 'dbscan')
    """
    n_clusters = request.args.get('n_clusters', type=int)
    method = request.args.get('method', default='kmeans', type=str)
    
    if method not in ['kmeans', 'dbscan']:
        return jsonify({"error": "Invalid clustering method. Use 'kmeans' or 'dbscan'."}), 400
    
    result, error = run_segmentation(DEFAULT_DATA_PATH, n_clusters, method)
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result), 200

@app.route('/api/upload-and-segment', methods=['POST'])
def upload_and_segment():
    """
    Upload a CSV file and run the segmentation pipeline.
    Query Parameters:
    - n_clusters: Number of clusters (optional, default: auto-determined)
    - method: Clustering method (optional, default: 'kmeans', options: 'kmeans', 'dbscan')
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.csv'):
        # Save the uploaded file temporarily
        file_path = os.path.join(UPLOAD_FOLDER, "uploaded.csv")
        file.save(file_path)
        
        # Get query parameters
        n_clusters = request.args.get('n_clusters', type=int)
        method = request.args.get('method', default='kmeans', type=str)
        
        if method not in ['kmeans', 'dbscan']:
            return jsonify({"error": "Invalid clustering method. Use 'kmeans' or 'dbscan'."}), 400
        
        # Run segmentation
        result, error = run_segmentation(file_path, n_clusters, method)
        
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if error:
            return jsonify({"error": error}), 500
        return jsonify(result), 200
    
    return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "API is running"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)