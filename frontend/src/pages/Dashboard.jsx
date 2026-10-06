import { useState, useEffect } from 'react'
import api from '../api/axios'
import Navbar from '../components/Navbar'

const TICKERS = ['SPY', 'AAPL', 'MSFT', 'GOOGL', 'NVDA']

export default function Dashboard() {
  const [ticker, setTicker] = useState('SPY')
  const [prediction, setPrediction] = useState(null)
  const [drift, setDrift] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function fetchPrediction() {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get(`/predict/${ticker}`)
      setPrediction(res.data)
      const driftRes = await api.get(`/monitoring/${ticker}`)
      setDrift(driftRes.data)
    } catch (err) {
      setError('Prédiction non disponible — pipeline non exécuté pour ce ticker')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPrediction()
  }, [ticker])

  return (
    <div style={styles.page}>
      <Navbar />

      <div style={styles.content}>
        <h2>Prédiction de marché</h2>

        <div style={styles.controls}>
          <select
            value={ticker}
            onChange={e => setTicker(e.target.value)}
            style={styles.select}
          >
            {TICKERS.map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <button onClick={fetchPrediction} style={styles.button} disabled={loading}>
            {loading ? 'Chargement...' : 'Analyser'}
          </button>
        </div>

        {error && <p style={styles.error}>{error}</p>}

        {prediction && (
          <div style={styles.card}>
            <h3>{prediction.ticker}</h3>
            <div style={{
              ...styles.direction,
              backgroundColor: prediction.direction === 'UP' ? '#e6f4ea' : '#fce8e6',
              color: prediction.direction === 'UP' ? '#137333' : '#c5221f',
            }}>
              {prediction.direction === 'UP' ? '▲ HAUSSE' : '▼ BAISSE'}
            </div>
            <p>Confiance : <strong>{(prediction.confidence * 100).toFixed(1)}%</strong></p>
            <p style={styles.date}>Prédiction pour demain · {new Date().toLocaleDateString('fr-FR')}</p>
          </div>
        )}

        {drift && (
          <div style={{ ...styles.card, marginTop: '16px' }}>
            <h3>Monitoring — Drift</h3>
            <p>Dataset drift : <strong>{drift.dataset_drift ? '⚠️ Détecté' : '✅ Stable'}</strong></p>
            <p>Features driftées : <strong>{drift.n_drifted} / {drift.n_features}</strong></p>
            <p>Part de drift : <strong>{(drift.drift_share * 100).toFixed(0)}%</strong></p>
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  },
  content: {
    maxWidth: '600px',
    margin: '40px auto',
    padding: '0 16px',
  },
  controls: {
    display: 'flex',
    gap: '8px',
    marginBottom: '24px',
  },
  select: {
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    width: '160px',
    cursor: 'pointer',
    backgroundColor: 'white',
  },
  button: {
    padding: '10px 20px',
    backgroundColor: '#1a73e8',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  direction: {
    fontSize: '32px',
    fontWeight: 'bold',
    textAlign: 'center',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '16px',
  },
  error: {
    color: '#c5221f',
  },
  date: {
    color: '#666',
    fontSize: '13px',
  },
}
