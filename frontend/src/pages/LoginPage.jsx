import { useState } from 'react'
import { setToken } from '../api'
import { apiJson } from '../api'
import './pages.css'

// Trang đăng nhập và đăng ký tài khoản Staff.
export default function LoginPage({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({
    email: '',
    full_name: '',
    phone_number: '',
    password: '',
    password_confirm: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const registering = mode === 'register'
      const data = await apiJson(registering ? '/auth/register' : '/auth/login', {
        method: 'POST',
        body: registering
          ? {
              email: form.email.trim(),
              full_name: form.full_name.trim(),
              phone_number: form.phone_number.trim(),
              password: form.password,
              password_confirm: form.password_confirm,
            }
          : { email: form.email.trim(), password: form.password },
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
            <p>{mode === 'login' ? 'Đăng nhập để quản lý ký túc xá' : 'Tạo tài khoản Staff mới'}</p>
          </div>
          <span className="heading-icon">K</span>
        </div>
        <form onSubmit={submit}>
          {mode === 'register' && (
            <label>
              Họ và tên
              <input required maxLength="150" value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
            </label>
          )}
          <label>
            Email
            <input required autoFocus type="email" maxLength="254" autoComplete="email" value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </label>
          {mode === 'register' && (
            <label>
                Số điện thoại
                <input required type="tel" maxLength="20" autoComplete="tel"
                  value={form.phone_number}
                  onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
            </label>
          )}
          <label>
            Mật khẩu
            <input required minLength="6" type="password"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </label>
          {mode === 'register' && (
            <label>
              Xác nhận mật khẩu
              <input required minLength="6" type="password" autoComplete="new-password"
                value={form.password_confirm}
                onChange={(e) => setForm({ ...form, password_confirm: e.target.value })} />
            </label>
          )}
          {error && <div className="notice error" role="alert">{error}</div>}
          <button className="primary-button" type="submit" disabled={loading}>
            {loading
              ? (mode === 'login' ? 'Đang đăng nhập...' : 'Đang đăng ký...')
              : (mode === 'login' ? 'Đăng nhập' : 'Đăng ký')}
          </button>
        </form>
        <button
          className="table-action"
          type="button"
          onClick={() => {
            setMode(mode === 'login' ? 'register' : 'login')
            setError('')
          }}
        >
          {mode === 'login' ? 'Chưa có tài khoản? Đăng ký' : 'Đã có tài khoản? Đăng nhập'}
        </button>
      </article>
    </div>
  )
}