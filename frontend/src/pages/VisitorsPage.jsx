import { useCallback, useEffect, useState } from 'react'
import { apiJson } from '../api'
import './pages.css'

const nowLocal = () =>
  new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16)
const fmt = (value) => (value ? new Date(value).toLocaleString('vi-VN') : '')

// Quản lý khách, lượt thăm và thống kê số lần thăm theo tuần/tháng.
export default function VisitorsPage() {
  const [visitors, setVisitors] = useState([])
  const [visits, setVisits] = useState([])
  const [report, setReport] = useState({ results: [] })
  const [period, setPeriod] = useState('month')
  const [refDate, setRefDate] = useState(nowLocal().slice(0, 10))
  const [visitorForm, setVisitorForm] = useState({ name: '', identity_number: '', birth_date: '' })
  const [visitForm, setVisitForm] = useState({ visitor_id: '', student_id: '', arrived_at: nowLocal() })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const loadAll = useCallback(async () => {
    setError('')
    try {
      const [v, vs, rep] = await Promise.all([
        apiJson('/visitors'),
        apiJson('/visits'),
        apiJson('/reports/visits', { params: { period, date: refDate } }),
      ])
      setVisitors(v)
      setVisits(vs)
      setReport(rep)
    } catch (err) {
      setError(err.message)
    }
  }, [period, refDate])

  useEffect(() => { loadAll() }, [loadAll])

  async function run(action, successText, reset) {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      await action()
      setMessage(successText)
      if (reset) reset()
      await loadAll()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const saveVisitor = (e) => {
    e.preventDefault()
    run(
      () => apiJson('/visitors', {
        method: 'POST',
        body: {
          name: visitorForm.name.trim(),
          identity_number: visitorForm.identity_number.trim() || null,
          birth_date: visitorForm.birth_date || null,
        },
      }),
      'Đã thêm hồ sơ khách.',
      () => setVisitorForm({ name: '', identity_number: '', birth_date: '' }),
    )
  }

  const saveVisit = (e) => {
    e.preventDefault()
    run(
      () => apiJson('/visits', {
        method: 'POST',
        body: {
          visitor_id: Number(visitForm.visitor_id),
          student_id: visitForm.student_id.trim(),
          arrived_at: visitForm.arrived_at,
        },
      }),
      'Đã ghi nhận lượt thăm.',
      () => setVisitForm({ ...visitForm, student_id: '', arrived_at: nowLocal() }),
    )
  }

  const depart = (visit) =>
    run(
      () => apiJson(`/visits/${visit.id}/departure`, { method: 'PATCH', body: {} }),
      `Đã ghi nhận ${visit.visitor_name} rời đi.`,
    )

  return (
    <section className="management-page">
      {message && <div className="notice success" role="status">{message}</div>}
      {error && <div className="notice error" role="alert">{error}</div>}

      <div className="management-grid">
        <article className="panel">
          <div className="panel-heading">
            <div><h2>Thêm hồ sơ khách</h2><p>Số CMT/CCCD không được trùng.</p></div>
            <span className="heading-icon">＋</span>
          </div>
          <form onSubmit={saveVisitor}>
            <label>Họ tên
              <input required maxLength="100" value={visitorForm.name} onChange={(e) => setVisitorForm({ ...visitorForm, name: e.target.value })} />
            </label>
            <label>Số CMT/CCCD
              <input maxLength="20" value={visitorForm.identity_number} onChange={(e) => setVisitorForm({ ...visitorForm, identity_number: e.target.value })} />
            </label>
            <label>Ngày sinh
              <input type="date" value={visitorForm.birth_date} onChange={(e) => setVisitorForm({ ...visitorForm, birth_date: e.target.value })} />
            </label>
            <button className="primary-button" type="submit" disabled={busy}>Thêm khách</button>
          </form>
        </article>

        <article className="panel">
          <div className="panel-heading list-heading">
            <div><h2>Danh sách khách</h2><p>{visitors.length} khách</p></div>
            <button className="refresh-button" onClick={loadAll}>↻ <span>Làm mới</span></button>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Mã</th><th>Họ tên</th><th>CMT/CCCD</th><th>Ngày sinh</th></tr></thead>
              <tbody>
                {visitors.length === 0 ? (
                  <tr><td className="empty-state" colSpan="4">Chưa có khách.</td></tr>
                ) : visitors.map((v) => (
                  <tr key={v.id}>
                    <td>{v.id}</td><td><strong>{v.name}</strong></td>
                    <td>{v.identity_number || '—'}</td><td>{v.birth_date || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <article className="panel">
        <div className="panel-heading">
          <div><h2>Ghi nhận khách đến thăm</h2><p>Một khách chỉ có một lượt thăm đang mở tại một thời điểm.</p></div>
          <span className="heading-icon">＋</span>
        </div>
        <form className="record-form" onSubmit={saveVisit}>
          <label>Khách
            <select required value={visitForm.visitor_id} onChange={(e) => setVisitForm({ ...visitForm, visitor_id: e.target.value })}>
              <option value="">Chọn khách</option>
              {visitors.map((v) => <option key={v.id} value={v.id}>{v.name}</option>)}
            </select>
          </label>
          <label>Mã sinh viên được thăm
            <input required value={visitForm.student_id} onChange={(e) => setVisitForm({ ...visitForm, student_id: e.target.value })} placeholder="Ví dụ: SV001" />
          </label>
          <label>Thời gian đến
            <input required type="datetime-local" value={visitForm.arrived_at} onChange={(e) => setVisitForm({ ...visitForm, arrived_at: e.target.value })} />
          </label>
          <button className="primary-button" type="submit" disabled={busy}>Ghi nhận lượt thăm</button>
        </form>
      </article>

      <article className="panel">
        <div className="panel-heading list-heading">
          <div><h2>Lượt thăm</h2><p>{visits.length} lượt, mới nhất ở trên</p></div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Khách</th><th>Sinh viên</th><th>Đến</th><th>Rời đi</th><th></th></tr></thead>
            <tbody>
              {visits.length === 0 ? (
                <tr><td className="empty-state" colSpan="5">Chưa có lượt thăm.</td></tr>
              ) : visits.map((v) => (
                <tr key={v.id}>
                  <td><strong>{v.visitor_name}</strong></td>
                  <td>{v.student_name}<small className="cell-subtitle">{v.student_id}</small></td>
                  <td>{fmt(v.arrived_at)}</td>
                  <td>{v.left_at ? fmt(v.left_at) : <span className="status-pill unpaid">Đang ở</span>}</td>
                  <td>{!v.left_at && <button className="table-action" onClick={() => depart(v)} disabled={busy}>Ghi nhận rời đi</button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      <article className="panel report-panel">
        <div className="panel-heading list-heading">
          <div>
            <h2>Thống kê khách thăm</h2>
            <p>{report.from ? `Từ ${report.from} đến ${report.to}` : 'Số lần mỗi khách đến thăm từng sinh viên.'}</p>
          </div>
          <div className="date-range-controls">
            <label>Theo
              <select value={period} onChange={(e) => setPeriod(e.target.value)}>
                <option value="week">Tuần</option>
                <option value="month">Tháng</option>
              </select>
            </label>
            <label>Ngày trong kỳ
              <input type="date" value={refDate} onChange={(e) => setRefDate(e.target.value)} />
            </label>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Sinh viên</th><th>Khách</th><th>CMT/CCCD</th><th>Số lần đến</th></tr></thead>
            <tbody>
              {report.results.length === 0 ? (
                <tr><td className="empty-state" colSpan="4">Không có lượt thăm trong kỳ.</td></tr>
              ) : report.results.map((r) => (
                <tr key={`${r.student_id}-${r.visitor_id}`}>
                  <td><strong>{r.student_name}</strong><small className="cell-subtitle">{r.student_id}</small></td>
                  <td>{r.visitor_name}</td>
                  <td>{r.visitor_identity_number || '—'}</td>
                  <td className="amount-cell">{r.visit_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  )
}