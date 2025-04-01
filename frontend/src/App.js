// segmentation_tool/frontend/src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import { Container, Form, Button, Table, Alert, Spinner } from 'react-bootstrap';
import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';
import Plot from 'react-plotly.js';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

function App() {
  const [file, setFile] = useState(null);
  const [nClusters, setNClusters] = useState('');
  const [method, setMethod] = useState('kmeans');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    const params = {};
    if (nClusters) params.n_clusters = nClusters;
    params.method = method;

    try {
      const response = await axios.post('http://localhost:5000/api/upload-and-segment', formData, {
        params,
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log('API Response:', response.data);
      console.log('Cluster Summary:', response.data.cluster_summary);
      if (response.status !== 200) {
        throw new Error('Unexpected response status: ' + response.status);
      }
      if (!response.data || !response.data.cluster_summary || Object.keys(response.data.cluster_summary).length === 0) {
        throw new Error('Invalid response format: Missing or empty cluster_summary');
      }
      setResult(response.data);
    } catch (err) {
      console.error('API Error:', err);
      setError(
        err.response?.data?.error || 
        err.response?.statusText || 
        err.message || 
        'An unexpected error occurred'
      );
    } finally {
      setLoading(false);
    }
  };

  const radarData = result?.cluster_summary && Object.keys(result.cluster_summary).length > 0 ? {
    labels: Object.keys(result.cluster_summary[Object.keys(result.cluster_summary)[0]]),
    datasets: Object.entries(result.cluster_summary).map(([cluster, values], idx) => ({
      label: `Cluster ${cluster}`,
      data: Object.values(values).map(val => {
        if (typeof val === 'number' && !isNaN(val)) {
          return val;
        }
        console.warn(`Invalid value in cluster ${cluster}:`, val);
        return 0;
      }),
      backgroundColor: `rgba(${idx * 50}, ${idx * 100}, 255, 0.2)`,
      borderColor: `rgba(${idx * 50}, ${idx * 100}, 255, 1)`,
      borderWidth: 1,
    })),
  } : null;

  const scatter3DData = result?.raw_data && result.raw_data.length > 0 ? (() => {
    const clusters = [...new Set(result.raw_data.map(item => item.Cluster))];
    return clusters.map((cluster, idx) => ({
      x: result.raw_data.filter(item => item.Cluster === cluster).map(item => item['Age']),
      y: result.raw_data.filter(item => item.Cluster === cluster).map(item => item['Annual Income (k$)']),
      z: result.raw_data.filter(item => item.Cluster === cluster).map(item => item['Spending Score (1-100)']),
      type: 'scatter3d',
      mode: 'markers',
      name: `Cluster ${cluster}`,
      marker: {
        size: 5,
        color: `rgba(${idx * 50}, ${idx * 100}, 255, 0.8)`,
        opacity: 0.8,
      },
    }));
  })() : null;

  return (
    <Container className="mt-5">
      <h1>Market Segmentation Tool</h1>
      <div className="form-card">
        <Form onSubmit={handleSubmit}>
          <Form.Group controlId="formFile" className="mb-3">
            <Form.Label>Upload CSV File</Form.Label>
            <Form.Control type="file" accept=".csv" onChange={handleFileChange} />
          </Form.Group>
          <Form.Group controlId="formNClusters" className="mb-3">
            <Form.Label>Number of Clusters (optional)</Form.Label>
            <Form.Control
              type="number"
              value={nClusters}
              onChange={(e) => setNClusters(e.target.value)}
              placeholder="Leave blank for auto-detection"
            />
          </Form.Group>
          <Form.Group controlId="formMethod" className="mb-3">
            <Form.Label>Clustering Method</Form.Label>
            <Form.Select value={method} onChange={(e) => setMethod(e.target.value)}>
              <option value="kmeans">K-means</option>
              <option value="dbscan">DBSCAN</option>
            </Form.Select>
          </Form.Group>
          <Button variant="primary" type="submit" disabled={!file || loading}>
            {loading ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Processing...
              </>
            ) : (
              'Segment Customers'
            )}
          </Button>
        </Form>
      </div>

      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
        </Alert>
      )}

      {loading && (
        <div className="text-center mt-3">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p>Processing your request...</p>
        </div>
      )}

      {result && !loading && (
        <div className="results-card">
          <h2>Segmentation Results</h2>
          <h3>Cluster Summary</h3>
          {result.cluster_summary && Object.keys(result.cluster_summary).length > 0 ? (
            <Table striped bordered hover>
              <thead>
                <tr>
                  <th>Cluster</th>
                  {Object.keys(result.cluster_summary[Object.keys(result.cluster_summary)[0]]).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(result.cluster_summary).map(([cluster, values]) => (
                  <tr key={cluster}>
                    <td>{cluster}</td>
                    {Object.values(values).map((value, idx) => (
                      <td key={idx}>
                        {typeof value === 'number' && !isNaN(value) ? value.toFixed(2) : 'N/A'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </Table>
          ) : (
            <Alert variant="warning">No cluster summary available.</Alert>
          )}

          {radarData ? (
            <div className="chart-container">
              <div>
                <h3>Cluster Comparison (Radar Chart)</h3>
                <Radar
                  data={radarData}
                  options={{
                    scales: {
                      r: {
                        beginAtZero: true,
                      },
                    },
                    plugins: {
                      legend: {
                        position: 'top',
                      },
                    },
                  }}
                />
              </div>
            </div>
          ) : (
            <Alert variant="warning">No data available for radar chart.</Alert>
          )}

          {scatter3DData ? (
            <div className="chart-container">
              <div>
                <h3>3D Scatter Plot of Clusters</h3>
                <Plot
                  data={scatter3DData}
                  layout={{
                    width: 800,
                    height: 600,
                    title: '3D Scatter Plot of Customer Segments',
                    scene: {
                      xaxis: { title: 'Age' },
                      yaxis: { title: 'Annual Income (k$)' },
                      zaxis: { title: 'Spending Score (1-100)' },
                    },
                    margin: { l: 0, r: 0, b: 0, t: 50 },
                  }}
                />
              </div>
            </div>
          ) : (
            <Alert variant="warning">No data available for 3D scatter plot.</Alert>
          )}
        </div>
      )}
    </Container>
  );
}

export default App;