import { useCallback, useEffect, useState } from 'react'
import { apiJson } from '../api'
import './pages.css'

const EMPTY = { student_id: '', name: '', identity_number: '', birth_date: '', class_name: '', hometown: '' }

// Quản lý hồ sơ sinh viên: tìm kiếm, thêm mới, cập nhật.
export default function StudentsPage() {
  const [students, setStudents] = useState([])
  const [keyword, setKeyword] = useState('')
  const [form, setForm] = useState(EMPTY)
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const load = useCallback(async (q) => {
    setLoading(true)
    setError('')
    try {
      setStudents(await apiJson('/students', { params: { q } }))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load('') }, [load])

  async function save(event) {
    event.preventDefault()
    if (!form.student_id.trim() || !form.name.trim()) {
      setError('Vui lòng nhập mã sinh viên và họ tên.')
      return
    }

    setSubmitting(true)
    setError('')
    setMessage('')
    const body = {
      ...form,
      student_id: form.student_id.trim(),
      identity_number: form.identity_number.trim() || null,
      birth_date: form.birth_date || null,
    }
    try {
      if (editing) {
        await apiJson(`/students/${form.student_id}`, { method: 'PUT', body })
      } else {
        await apiJson('/students', { method: 'POST', body })
      }
      setMessage(editing ? 'Đã cập nhật sinh viên.' : 'Đã thêm sinh viên.')
      resetForm()
      await load(keyword)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  function startEdit(student) {
    setEditing(true)
    setMessage('')
    setError('')
    setForm({
      ...EMPTY,
      ...student,
      identity_number: student.identity_number ?? '',
      birth_date: student.birth_date ?? '',
    })
  }

  function resetForm() {
    setEditing(false)
    setForm(EMPTY)
  }

  async function remove(student) {
    if (!window.confirm(`Xóa hồ sơ sinh viên ${student.student_id} - ${student.name}? Dữ liệu có lịch sử phát sinh sẽ không thể xóa.`)) return

    setSubmitting(true)
    setError('')
    setMessage('')
    try {
      await apiJson(`/students/${student.student_id}`, { method: 'DELETE' })
      setMessage(`Đã xóa sinh viên ${student.student_id}.`)
      if (editing && form.student_id === student.student_id) resetForm()
      await load(keyword)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const set = (field) => (event) => {
    setError('')
    setForm({ ...form, [field]: event.target.value })
  }

  return (
    <section className="management-page">
      {message && <div className="notice success" role="status">{message}</div>}
      {error && <div className="notice error" role="alert">{error}</div>}

      <div className="management-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <h2>{editing ? 'Cập nhật sinh viên' : 'Thêm sinh viên'}</h2>
              <p>Mã sinh viên và số CMT/CCCD không được trùng.</p>
            </div>
            <span className="heading-icon">☰</span>
          </div>
          <form onSubmit={save} noValidate>
            <label>Mã sinh viên
              <input required maxLength="15" value={form.student_id} onChange={set('student_id')} disabled={editing} placeholder="Ví dụ: SV001" />
              <small className="field-hint">Bắt buộc</small>
            </label>
            <label>Họ tên
              <input required maxLength="100" value={form.name} onChange={set('name')} />
              <small className="field-hint">Bắt buộc</small>
            </label>
            <label>Số CMT/CCCD
              <input maxLength="20" value={form.identity_number} onChange={set('identity_number')} />
            </label>
            <div className="form-row">
              <label>Ngày sinh
                <input type="date" value={form.birth_date} onChange={set('birth_date')} />
              </label>
              <label>Lớp
                <input maxLength="30" value={form.class_name} onChange={set('class_name')} />
              </label>
            </div>
            <label>Quê quán
              <input maxLength="150" value={form.hometown} onChange={set('hometown')} />
            </label>
            <div className="form-actions">
              <button className="primary-button" type="submit" disabled={submitting}>
                {submitting ? 'Đang lưu...' : editing ? 'Lưu thay đổi' : 'Thêm sinh viên'}
              </button>
              {editing && <button className="secondary-button" type="button" onClick={resetForm}>Hủy</button>}
            </div>
          </form>
        </article>

        <article className="panel">
          <div className="panel-heading list-heading">
            <div>
              <h2>Danh sách sinh viên</h2>
              <p>{students.length} sinh viên</p>
            </div>
            <button className="refresh-button" onClick={() => load(keyword)} disabled={loading}>
              ↻ <span>Làm mới</span>
            </button>
          </div>
          <form className="search-row" onSubmit={(e) => { e.preventDefault(); load(keyword) }}>
            <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="Tìm theo mã, họ tên hoặc CMT/CCCD" />
            <button className="secondary-button" type="submit">Tìm</button>
          </form>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Mã SV</th><th>Họ tên</th><th>CMT/CCCD</th><th>Ngày sinh</th><th>Lớp</th><th>Quê quán</th><th></th></tr>
              </thead>
              <tbody>
                {loading && students.length === 0 ? (
                  <tr><td className="empty-state" colSpan="7">Đang tải...</td></tr>
                ) : students.length === 0 ? (
                  <tr><td className="empty-state" colSpan="7">Chưa có sinh viên phù hợp.</td></tr>
                ) : students.map((s) => (
                  <tr key={s.student_id}>
                    <td>{s.student_id}</td>
                    <td><strong>{s.name}</strong></td>
                    <td>{s.identity_number || '—'}</td>
                    <td>{s.birth_date || '—'}</td>
                    <td>{s.class_name || '—'}</td>
                    <td>{s.hometown || '—'}</td>
                    <td>
                      <button className="table-action" onClick={() => startEdit(s)}>Sửa</button>
                      {' · '}
                      <button className="table-action danger" onClick={() => remove(s)} disabled={submitting}>Xóa</button>
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