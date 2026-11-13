import { useCallback, useEffect, useState } from 'react'
import { apiJson } from '../api'
import StudentSelect from '../components/StudentSelect'
import './pages.css'

const nowLocal = () =>
  new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16)
const fmt = (value) => (value ? new Date(value).toLocaleString('vi-VN') : '')

// Quản lý khách, lượt thăm và thống kê số lần thăm theo tuần/tháng.
export default function VisitorsPage() {
  const [visits, setVisits] = useState([])
  const [report, setReport] = useState({ results: [] })
  const [period, setPeriod] = useState('month')
  const [refDate, setRefDate] = useState(nowLocal().slice(0, 10))
  const [visitForm, setVisitForm] = useState({
    visitor_name_input: '',
    visitor_identity_number: '',
    visitor_birth_date: '',
    student_id: '',
    arrived_at: nowLocal(),
  })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const loadAll = useCallback(async () => {
    setError('')
    try {
      const [vs, rep] = await Promise.all([
        apiJson('/visits'),
        apiJson('/reports/visits', { params: { period, date: refDate } }),
      ])
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

  const saveVisit = (e) => {
    e.preventDefault()
    run(
      () => apiJson('/visits', {
        method: 'POST',
        body: {
          visitor_name_input: visitForm.visitor_name_input.trim(),
          visitor_identity_number: visitForm.visitor_identity_number.trim() || null,
          visitor_birth_date: visitForm.visitor_birth_date || null,
          student_id: visitForm.student_id.trim(),
          arrived_at: visitForm.arrived_at,
        },
      }),
      'Đã ghi nhận lượt thăm.',
      () => setVisitForm({
        visitor_name_input: '',
        visitor_identity_number: '',
        visitor_birth_date: '',
        student_id: '',
        arrived_at: nowLocal(),
      }),
    )
  }

  const depart = async (visit) => {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      const updatedVisit = await apiJson(
        `/visits/${visit.id}/departure`,
        { method: 'PATCH', body: {} },
      )
      setVisits((current) =>
        current.map((item) => item.id === updatedVisit.id ? updatedVisit : item),
      )
      setMessage(`Đã ghi nhận ${visit.visitor_name} rời đi.`)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="management-page">
      {message && <div className="notice success" role="status">{message}</div>}
      {error && <div className="notice error" role="alert">{error}</div>}

      <article className="panel">
        <div className="panel-heading">
          <div><h2>Ghi nhận khách đến thăm</h2><p>Một khách chỉ có một lượt thăm đang mở tại một thời điểm.</p></div>
          <span className="heading-icon">＋</span>
        </div>
        <form className="record-form" onSubmit={saveVisit}>
          <label>Họ tên khách
            <input required maxLength="100" value={visitForm.visitor_name_input} onChange={(e) => setVisitForm({ ...visitForm, visitor_name_input: e.target.value })} />
          </label>
          <label>Số CMT/CCCD
            <input maxLength="20" value={visitForm.visitor_identity_number} onChange={(e) => setVisitForm({ ...visitForm, visitor_identity_number: e.target.value })} />
          </label>
          <label>Ngày sinh
            <input type="date" value={visitForm.visitor_birth_date} onChange={(e) => setVisitForm({ ...visitForm, visitor_birth_date: e.target.value })} />
          </label>
          <StudentSelect
            label="Sinh viên được thăm"
            value={visitForm.student_id}
            onChange={(e) => setVisitForm({ ...visitForm, student_id: e.target.value })}
          />
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
                  <td>
                    {v.left_at ? (
                      <>
                        <span className="status-pill paid">Đã rời đi</span>
                        <small className="cell-subtitle">{fmt(v.left_at)}</small>
                      </>
                    ) : (
                      <span className="status-pill unpaid">Đang ở</span>
                    )}
                  </td>
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