import { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const API_BASE = 'http://127.0.0.1:8000/api';

const AUTH = {
  username: 'tanisha',     
  password: 'tanisha123',  
};


function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [recordId, setRecordId] = useState(null);
const [pdfLoading, setPdfLoading] = useState(false);

  // load history on first render
 useEffect(() => {
  axios
    .get(`${API_BASE}/history/`, { auth: AUTH })
    .then((res) => setHistory(res.data))
    .catch(() => {});
}, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file first.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await axios.post(`${API_BASE}/upload-csv/`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
  auth: AUTH,
});

      setSummary(res.data.summary);

      setRecordId(res.data.record_id);


      // refresh history after upload
      const histRes = await axios.get(`${API_BASE}/history/`, { auth: AUTH });
      setHistory(histRes.data);
    } catch (err) {
      setError(
        err.response?.data?.error || 'Upload failed. Check CSV and backend.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
  if (!recordId) {
    setError('No report available. Please upload a CSV first.');
    return;
  }

  setPdfLoading(true);
  setError('');

  try {
    const res = await axios.get(`${API_BASE}/report/${recordId}/`, {
      responseType: 'blob',
      auth: AUTH,
    });

    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `equipment_report_${recordId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (err) {
    setError('Failed to download PDF report.');
  } finally {
    setPdfLoading(false);
  }
};


  // data for bar chart
  const chartData =
    summary && summary.type_distribution
      ? {
          labels: Object.keys(summary.type_distribution),
          datasets: [
            {
              label: 'Equipment Count',
              data: Object.values(summary.type_distribution),
            },
          ],
        }
      : null;

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem' }}>
      <h1 style={{ marginBottom: '1rem' }}>Chemical Equipment Visualizer</h1>

      <div
        style={{
          border: '1px solid #ddd',
          padding: '1rem',
          borderRadius: 8,
          marginBottom: '1.5rem',
        }}
      >
        <h2 style={{ marginBottom: '0.5rem' }}>Upload CSV</h2>
        <input type="file" accept=".csv" onChange={handleFileChange} />
        <button
          onClick={handleUpload}
          disabled={loading}
          style={{ marginLeft: '1rem' }}
        >
          {loading ? 'Uploading...' : 'Upload & Analyze'}
        </button>

        {error && (
          <p style={{ color: 'red', marginTop: '0.5rem' }}>{error}</p>
        )}
      </div>

      {summary && (
        <div
          style={{
            border: '1px solid #ddd',
            padding: '1rem',
            borderRadius: 8,
            marginBottom: '1.5rem',
          }}
        >
          <h2>Summary</h2>
          <ul>
            <li>Total equipment: {summary.total_count}</li>
            <li>Average flowrate: {summary.avg_flowrate?.toFixed(2)}</li>
            <li>Average pressure: {summary.avg_pressure?.toFixed(2)}</li>
            <li>Average temperature: {summary.avg_temperature?.toFixed(2)}</li>
          </ul>

          {chartData && (
            <div style={{ marginTop: '1rem' }}>
              <h3>Equipment Type Distribution</h3>
              <Bar data={chartData} />
            </div>
          )}

          <button
  onClick={handleDownloadPdf}
  disabled={pdfLoading}
  style={{ marginTop: '1rem' }}
>
  {pdfLoading ? 'Generating PDF...' : 'Download PDF Report'}
</button>

        </div>
      )}

      <div
        style={{
          border: '1px solid #ddd',
          padding: '1rem',
          borderRadius: 8,
        }}
      >
        <h2>Last 5 Uploads</h2>
        {history.length === 0 ? (
          <p>No uploads yet.</p>
        ) : (
          <ul>
            {history.map((rec) => (
              <li key={rec.id}>
                {rec.filename} — {rec.total_count} items
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default App;
