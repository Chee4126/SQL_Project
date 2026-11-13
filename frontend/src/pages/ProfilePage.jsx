import { useState } from 'react'
import { apiJson, setToken } from '../api'
import './pages.css'

export default function ProfilePage({ user, onUserUpdated }) {
  const [form, setForm] = useState({
    full_name: user.full_name || '',
    email: user.email || '',
    phone_number: user.phone_number || '',
    current_password: '',
    new_password: '',
    password_confirm: '',
  })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const set = (field) => (event) => {
    setForm((previous) => ({ ...previous, [field]: event.target.value }))
  }

  async function submit(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    setMessage('')
    try {
      const response = await apiJson('/auth/me', {
        method: 'PATCH',
        body: {
          full_name: form.full_name.trim(),
          email: form.email.trim(),
          phone_number: form.phone_number.trim(),
          current_password: form.current_password,
          new_password: form.new_password,
          password_confirm: form.password_confirm,
        },
      })
      const { token, ...updatedUser } = response
      if (token) setToken(token)
      onUserUpdated(updatedUser)
      setForm((previous) => ({
        ...previous,
        full_name: updatedUser.full_name || '',
        email: updatedUser.email || '',
        phone_number: updatedUser.phone_number || '',
        current_password: '',
        new_password: '',
        password_confirm: '',
      }))
      setMessage('Đã cập nhật hồ sơ tài khoản.')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="management-page profile-page">
      {message && <div className="notice success" role="status">{message}</div>}
      {error && <div className="notice error" role="alert">{error}</div>}

      <article className="panel">
        <div className="panel-heading">
          <div>
            <h2>Thông tin cá nhân</h2>
            <p>Tên đăng nhập: <strong>{user.username}</strong></p>
          </div>
          <span className="heading-icon">◎</span>
        </div>
        <form className="profile-form" onSubmit={submit}>
          <label>
            Họ và tên
            <input required maxLength="150" value={form.full_name} onChange={set('full_name')} />
          </label>
          <label>
            Email đăng nhập
            <input required type="email" maxLength="254" autoComplete="email"
              value={form.email} onChange={set('email')} />
          </label>
          <label>
            Số điện thoại
            <input required type="tel" maxLength="20" autoComplete="tel"
              value={form.phone_number} onChange={set('phone_number')} />
          </label>

          <div className="profile-password-heading">
            <h3>Đổi mật khẩu</h3>
            <p>Để trống các trường bên dưới nếu không muốn đổi mật khẩu.</p>
          </div>
          <label>
            Mật khẩu hiện tại
            <input type="password" autoComplete="current-password"
              value={form.current_password} onChange={set('current_password')} />
          </label>
          <label>
            Mật khẩu mới
            <input type="password" minLength="6" autoComplete="new-password"
              value={form.new_password} onChange={set('new_password')} />
          </label>
          <label>
            Xác nhận mật khẩu mới
            <input type="password" minLength="6" autoComplete="new-password"
              value={form.password_confirm} onChange={set('password_confirm')} />
          </label>
          <div className="form-actions">
            <button className="primary-button" type="submit" disabled={saving}>
              {saving ? 'Đang lưu...' : 'Lưu thay đổi'}
            </button>
          </div>
        </form>
      </article>
    </section>
  )
}
