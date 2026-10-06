import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Navbar() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <nav style={styles.nav}>
      <span style={styles.logo}>📈 Financial Market Analyzer</span>
      <button onClick={handleLogout} style={styles.button}>
        Déconnexion
      </button>
    </nav>
  )
}

const styles = {
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '0 24px',
    height: '56px',
    backgroundColor: '#1a73e8',
    color: 'white',
  },
  logo: {
    fontSize: '18px',
    fontWeight: 'bold',
  },
  button: {
    padding: '8px 16px',
    backgroundColor: 'white',
    color: '#1a73e8',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold',
  },
}