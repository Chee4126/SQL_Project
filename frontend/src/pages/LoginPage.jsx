import { useState } from 'react'
import { setToken } from '../api'
import { apiJson } from '../api'
import './pages.css'

// Trang đăng nhập cho Admin và nhân viên.
export default function LoginPage({ onLogin }) {
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const data = await apiJson('/auth/login', {
        method: 'POST',
        body: { username: form.username.trim(), password: form.password },
      })
      setToken(data.token)
      onLogin(data.user)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-wrap">
      <article className="panel login-card">
        <div className="panel-heading">
          <div>
            <h2>KTX Manager</h2>
            <p>Đăng nhập để quản lý ký túc xá</p>
          </div>
          <span className="heading-icon">K</span>
        </div>
        <form onSubmit={submit}>
          <label>
            Tên đăng nhập
            <input required autoFocus value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })} />
          </label>
          <label>
            Mật khẩu
            <input required type="password" value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </label>
          {error && <div className="notice error" role="alert">{error}</div>}
          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>
      </article>
    </div>
  )
}