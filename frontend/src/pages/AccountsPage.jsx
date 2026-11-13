import { useCallback, useEffect, useState } from 'react'
import { apiJson } from '../api'
import './pages.css'

// Quản lý danh sách tài khoản Staff.
export default function AccountsPage({ user }) {
  const [users, setUsers] = useState([])
  const [form, setForm] = useState({
    email: '',
    phone_number: '',
    password: '',
    full_name: '',
  })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    setError('')
    try {
      setUsers(await apiJson('/accounts'))
    } catch (err) {
      setError(err.message)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function run(action, successText, reset) {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      await action()
      setMessage(successText)
      if (reset) reset()
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const createUser = (event) => {
    event.preventDefault()
    run(
      () => apiJson('/accounts', {
        method: 'POST',
        body: {
          email: form.email.trim(),
          phone_number: form.phone_number.trim(),
          password: form.password,
          full_name: form.full_name.trim(),
        },
      }),
      `Đã tạo tài khoản ${form.email.trim()}.`,
      () => setForm({
        email: '',
        phone_number: '',
        password: '',
        full_name: '',
      }),
    )
  }

  const removeUser = (account) => {
    if (!window.confirm(`Xóa tài khoản ${account.email}?`)) return
    run(
      () => apiJson(`/accounts/${account.id}`, { method: 'DELETE' }),
      `Đã xóa tài khoản ${account.email}.`,
    )
  }

  const set = (field) => (event) => setForm({ ...form, [field]: event.target.value })

  return (
    <section className="management-page">
      {message && <div className="notice success" role="status">{message}</div>}
      {error && <div className="notice error" role="alert">{error}</div>}

      <div className="management-grid">
        <article className="panel">
          <div className="panel-heading">
            <div><h2>Tạo tài khoản</h2><p>Mật khẩu tối thiểu 6 ký tự.</p></div>
            <span className="heading-icon">＋</span>
          </div>
          <form onSubmit={createUser}>
            <label>Email
              <input required type="email" maxLength="254" value={form.email} onChange={set('email')} />
            </label>
            <label>Họ tên
              <input required maxLength="150" value={form.full_name} onChange={set('full_name')} />
            </label>
            <label>Số điện thoại
              <input required type="tel" maxLength="20" value={form.phone_number} onChange={set('phone_number')} />
            </label>
            <label>Mật khẩu
              <input required type="password" minLength="6" value={form.password} onChange={set('password')} />
            </label>
            <button className="primary-button" type="submit" disabled={busy}>Tạo tài khoản</button>
          </form>
        </article>

        <article className="panel">
          <div className="panel-heading list-heading">
            <div><h2>Danh sách tài khoản</h2><p>{users.length} tài khoản</p></div>
            <button className="refresh-button" onClick={load}>↻ <span>Làm mới</span></button>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Email</th><th>Họ tên</th><th>Số điện thoại</th><th>Vai trò</th><th></th></tr></thead>
              <tbody>
                {users.length === 0 ? (
                  <tr><td className="empty-state" colSpan="5">Chưa có tài khoản.</td></tr>
                ) : users.map((u) => (
                  <tr key={u.id}>
                    <td><strong>{u.email || '—'}</strong></td>
                    <td>{u.full_name || '—'}</td>
                    <td>{u.phone_number || '—'}</td>
                    <td>
                      <span className="status-pill paid">Staff</span>
                    </td>
                    <td>
                      {u.id === user.id ? (
                        <small className="cell-subtitle">Tài khoản của bạn</small>
                      ) : (
                        <button className="table-action danger" onClick={() => removeUser(u)} disabled={busy}>
                          Xóa
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </div>
    </section>
  )
}