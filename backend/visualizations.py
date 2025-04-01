# segmentation_tool/backend/visualizations.py
import plotly.express as px

def plot_3d_clusters(df, labels):
    df['Cluster'] = labels
    fig = px.scatter_3d(
        df,
        x='Age',
        y='Annual Income (k$)',
        z='Spending Score (1-100)',
        color='Cluster',
        title='Customer Segments in 3D',
        labels={'Cluster': 'Customer Segment'}
    )
    fig.show()