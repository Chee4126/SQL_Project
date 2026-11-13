import { useEffect, useState } from 'react'
import App from './App.jsx'
import LoginPage from './pages/LoginPage.jsx'
import { API_URL, apiFetch, clearToken, getToken } from './api'

// Cổng đăng nhập: kiểm tra token, hiện trang đăng nhập hoặc giao diện chính.
export default function AuthGate() {
  const [user, setUser] = useState(null)
  const [checking, setChecking] = useState(Boolean(getToken()))

  useEffect(() => {
    if (!getToken()) return
    apiFetch(`${API_URL}/auth/me`)
      .then((response) => (response.ok ? response.json() : null))
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setChecking(false))
  }, [])

  useEffect(() => {
    const onLogout = () => setUser(null)
    window.addEventListener('auth:logout', onLogout)
    return () => window.removeEventListener('auth:logout', onLogout)
  }, [])

  async function logout() {
    try {
      await apiFetch(`${API_URL}/auth/logout`, { method: 'POST' })
    } finally {
      clearToken()
      setUser(null)
    }
  }

  if (checking) return <p style={{ textAlign: 'center', marginTop: 60 }}>Đang tải...</p>
  if (!user) return <LoginPage onLogin={setUser} />
  return <App user={user} onLogout={logout} onUserUpdated={setUser} />
}