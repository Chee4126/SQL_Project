import { useCallback, useEffect, useState } from 'react'
import { apiJson } from '../api'
import './pages.css'

const ROLE_LABEL = { ADMIN: 'Admin', STAFF: 'Nhân viên' }

// Quản lý tài khoản: Admin xem danh sách, tạo nhân viên và đổi vai trò.
export default function AccountsPage({ user }) {
  const [users, setUsers] = useState([])
  const [form, setForm] = useState({ username: '', password: '', full_name: '', role: 'STAFF' })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    setError('')
    try {
      setUsers(await apiJson('/admin/users'))
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
      () => apiJson('/admin/users', {
        method: 'POST',
        body: {
          username: form.username.trim(),
          password: form.password,
          full_name: form.full_name.trim(),
          role: form.role,
        },
      }),
      `Đã tạo tài khoản ${form.username.trim()}.`,
      () => setForm({ username: '', password: '', full_name: '', role: 'STAFF' }),
    )
  }

  const changeRole = (target) => {
    const role = target.role === 'ADMIN' ? 'STAFF' : 'ADMIN'
    run(
      () => apiJson(`/admin/users/${target.id}/role`, { method: 'PATCH', body: { role } }),
      `Đã đổi ${target.username} thành ${ROLE_LABEL[role]}.`,
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
            <label>Tên đăng nhập
              <input required maxLength="150" value={form.username} onChange={set('username')} />
            </label>
            <label>Họ tên
              <input maxLength="150" value={form.full_name} onChange={set('full_name')} />
            </label>
            <label>Mật khẩu
              <input required type="password" minLength="6" value={form.password} onChange={set('password')} />
            </label>
            <label>Vai trò
              <select value={form.role} onChange={set('role')}>
                <option value="STAFF">Nhân viên</option>
                <option value="ADMIN">Admin</option>
              </select>
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
              <thead><tr><th>Tên đăng nhập</th><th>Họ tên</th><th>Vai trò</th><th></th></tr></thead>
              <tbody>
                {users.length === 0 ? (
                  <tr><td className="empty-state" colSpan="4">Chưa có tài khoản.</td></tr>
                ) : users.map((u) => (
                  <tr key={u.id}>
                    <td><strong>{u.username}</strong></td>
                    <td>{u.full_name || '—'}</td>
                    <td>
                      <span className={`status-pill ${u.role === 'ADMIN' ? 'paid' : 'unpaid'}`}>
                        {ROLE_LABEL[u.role]}
                      </span>
                    </td>
                    <td>
                      {u.username === user.username ? (
                        <small className="cell-subtitle">Tài khoản của bạn</small>
                      ) : (
                        <button className="table-action" onClick={() => changeRole(u)} disabled={busy}>
                          {u.role === 'ADMIN' ? 'Hạ xuống nhân viên' : 'Nâng lên Admin'}
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