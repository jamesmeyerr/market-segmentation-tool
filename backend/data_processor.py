# segmentation_tool/backend/data_processor.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import os

class DataProcessor:
    def __init__(self):
        self.df = None
        self.scaled_features = None
        self.feature_columns = None
        
    def load_data(self, file_path=None, data=None):
        """Load data from various sources"""
        try:
            if file_path:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    self.df = pd.read_excel(file_path)
            elif data is not None:
                self.df = pd.DataFrame(data)
            else:
                raise ValueError("No data source provided")
            
            print(f"Data loaded successfully. Shape: {self.df.shape}")
            return True
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False

    def clean_data(self):
        """Clean the Mall_Customers dataset"""
        if self.df is None:
            return False
            
        # Remove duplicates based on CustomerID
        self.df.drop_duplicates(subset=['CustomerID'], inplace=True)
        
        # Handle missing values
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns
        self.df[numeric_columns] = self.df[numeric_columns].fillna(
            self.df[numeric_columns].mean()
        )
        
        # Drop columns with all NaN (if any)
        self.df.dropna(axis=1, how='all', inplace=True)
        
        # Encode categorical variables (Gender)
        if 'Gender' in self.df.columns:
            le = LabelEncoder()
            self.df['Gender'] = le.fit_transform(self.df['Gender'])  # Male/Female to 0/1
        
        return True

    def feature_engineering(self):
        """Create features specific to Mall_Customers dataset"""
        if self.df is None:
            return False
            
        # Create a new feature: Income-to-Spending Ratio
        self.df['Income_to_Spending_Ratio'] = (
            self.df['Annual Income (k$)'] / self.df['Spending Score (1-100)']
        )
        
        # Log transform for skewed data
        self.df['Log_Annual_Income'] = np.log1p(self.df['Annual Income (k$)'])
        
        # Select features for clustering (excluding CustomerID)
        self.feature_columns = [
            'Gender', 'Age', 'Annual Income (k$)', 'Spending Score (1-100)',
            'Income_to_Spending_Ratio', 'Log_Annual_Income'
        ]
        
        # Standardize numerical features
        scaler = StandardScaler()
        self.scaled_features = scaler.fit_transform(self.df[self.feature_columns])
        
        return True