// segmentation_tool/frontend/src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import { Container, Form, Button, Table, Alert } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [nClusters, setNClusters] = useState('');
  const [method, setMethod] = useState('kmeans');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);

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
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    }
  };

  return (
    <Container className="mt-5">
      <h1>Market Segmentation Tool</h1>
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
        <Button variant="primary" type="submit" disabled={!file}>
          Segment Customers
        </Button>
      </Form>

      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
        </Alert>
      )}

      {result && (
        <div className="mt-5">
          <h2>Segmentation Results</h2>
          <h3>Cluster Summary</h3>
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>Cluster</th>
                {result.cluster_summary && Object.keys(result.cluster_summary[Object.keys(result.cluster_summary)[0]]).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.cluster_summary && Object.entries(result.cluster_summary).map(([cluster, values]) => (
                <tr key={cluster}>
                  <td>{cluster}</td>
                  {Object.values(values).map((value, idx) => (
                    <td key={idx}>{typeof value === 'number' ? value.toFixed(2) : value}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </Container>
  );
}

export default App;