import { useCallback, useEffect, useState } from 'react'
import { apiJson } from '../api'
import StudentSelect from '../components/StudentSelect'
import './pages.css'

const localDate = () =>
  new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10)
const money = (v) =>
  new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(Number(v || 0))
const ROOM_OPTIONS = [
  { price: '1800000.00', capacity: 4, label: '1.800.000 VNĐ/tháng — 4 người' },
  { price: '250000.00', capacity: 8, label: '250.000 VNĐ/tháng — 8 người' },
]

// Quản lý phòng, phân phòng và kiểm tra sức chứa.
export default function RoomsPage() {
  const [rooms, setRooms] = useState([])
  const [assignments, setAssignments] = useState([])
  const [report, setReport] = useState([])
  const [reportDate, setReportDate] = useState(localDate())
  const [roomForm, setRoomForm] = useState({
    room_id: '',
    name: '',
    floor: '',
    room_option: '',
  })
  const [assignForm, setAssignForm] = useState({ student_id: '', room_id: '', start_date: localDate() })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const loadAll = useCallback(async () => {
    setError('')
    try {
      const [roomList, active, rep] = await Promise.all([
        apiJson('/rooms', { params: { date: assignForm.start_date } }),
        apiJson('/room-assignments', { params: { active: 'true' } }),
        apiJson('/reports/room-capacity', { params: { date: reportDate } }),
      ])
      setRooms(roomList)
      setAssignments(active)
      setReport(rep)
    } catch (err) {
      setError(err.message)
    }
  }, [assignForm.start_date, reportDate])

  useEffect(() => { loadAll() }, [loadAll])

  // Chạy một thao tác ghi dữ liệu, báo kết quả rồi tải lại.
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

  const saveRoom = (e) => {
    e.preventDefault()
    const option = ROOM_OPTIONS.find((item) => item.price === roomForm.room_option)
    if (!option) return
    run(
      () => apiJson('/rooms', {
        method: 'POST',
        body: {
          room_id: roomForm.room_id.trim(),
          name: roomForm.name.trim(),
          floor: roomForm.floor === '' ? null : Number(roomForm.floor),
          monthly_price: option.price,
          max_occupants: option.capacity,
        },
      }),
      'Đã thêm phòng.',
      () => setRoomForm({
        room_id: '',
        name: '',
        floor: '',
        room_option: '',
      }),
    )
  }

  const assign = (e) => {
    e.preventDefault()
    run(
      () => apiJson('/room-assignments', {
        method: 'POST',
        body: { student_id: assignForm.student_id.trim(), room_id: assignForm.room_id, start_date: assignForm.start_date },
      }),
      'Đã phân phòng.',
      () => setAssignForm({ ...assignForm, student_id: '' }),
    )
  }

  const endAssignment = (item) =>
    run(
      () => apiJson(`/room-assignments/${item.id}/end`, { method: 'PATCH', body: {} }),
      `Đã ghi nhận ${item.student_name} rời phòng ${item.room_id}.`,
    )

  const removeRoom = (room) => {
    if (!window.confirm(`Xóa phòng ${room.room_id} - ${room.name}? Phòng có lịch sử phân phòng sẽ không thể xóa.`)) return
    run(
      () => apiJson(`/rooms/${room.room_id}`, { method: 'DELETE' }),
      `Đã xóa phòng ${room.room_id}.`,
    )
  }

  return (
    <section className="management-page">
      {message && <div className="notice success" role="status">{message}</div>}
      {error && <div className="notice error" role="alert">{error}</div>}

      <div className="management-grid">
        <article className="panel">
          <div className="panel-heading">
            <div><h2>Phân phòng</h2><p>Hệ thống từ chối nếu phòng đã đủ người hoặc sinh viên đang ở nơi khác.</p></div>
            <span className="heading-icon">⌂</span>
          </div>
          <form onSubmit={assign}>
            <StudentSelect
              label="Sinh viên"
              value={assignForm.student_id}
              onChange={(e) => setAssignForm({ ...assignForm, student_id: e.target.value })}
            />
            <label>Phòng
              <select required value={assignForm.room_id} onChange={(e) => setAssignForm({ ...assignForm, room_id: e.target.value })}>
                <option value="">Chọn phòng</option>
                {rooms.map((r) => (
                  <option
                    key={r.room_id}
                    value={r.room_id}
                    disabled={r.current_occupants >= r.max_occupants}
                  >
                    {r.room_id} ({r.current_occupants}/{r.max_occupants} người)
                    {r.current_occupants >= r.max_occupants ? ' — Đã đủ chỗ' : ''}
                  </option>
                ))}
              </select>
            </label>
            <label>Ngày vào
              <input required type="date" value={assignForm.start_date} onChange={(e) => setAssignForm({ ...assignForm, start_date: e.target.value })} />
            </label>
            <button
              className="primary-button"
              type="submit"
              disabled={
                busy
                || !rooms.some(
                  (room) =>
                    room.room_id === assignForm.room_id
                    && room.current_occupants < room.max_occupants,
                )
              }
            >
              Phân phòng
            </button>
          </form>
        </article>

        <article className="panel">
          <div className="panel-heading list-heading">
            <div><h2>Đang ở</h2><p>{assignments.length} lượt ở còn hiệu lực</p></div>
            <button className="refresh-button" onClick={loadAll}>↻ <span>Làm mới</span></button>
          </div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Sinh viên</th><th>Phòng</th><th>Ngày vào</th><th></th></tr></thead>
              <tbody>
                {assignments.length === 0 ? (
                  <tr><td className="empty-state" colSpan="4">Chưa có sinh viên đang ở.</td></tr>
                ) : assignments.map((a) => (
                  <tr key={a.id}>
                    <td><strong>{a.student_name}</strong><small className="cell-subtitle">{a.student_id}</small></td>
                    <td>{a.room_id}</td>
                    <td>{a.start_date}</td>
                    <td><button className="table-action" onClick={() => endAssignment(a)} disabled={busy}>Ghi nhận rời phòng</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <article className="panel report-panel">
        <div className="panel-heading list-heading">
          <div><h2>Kiểm tra sức chứa phòng</h2><p>Số người ở so với sức chứa tại ngày được chọn.</p></div>
          <div className="date-range-controls">
            <label>Ngày<input type="date" value={reportDate} onChange={(e) => setReportDate(e.target.value)} /></label>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Phòng</th><th>Đơn giá/tháng</th><th>Đang ở</th><th>Sức chứa</th><th>Còn trống</th><th>Kiểm tra</th></tr></thead>
            <tbody>
              {report.length === 0 ? (
                <tr><td className="empty-state" colSpan="6">Chưa có phòng.</td></tr>
              ) : report.map((r) => (
                <tr key={r.room_id}>
                  <td><strong>{r.room_id}</strong><small className="cell-subtitle">{r.room_name}</small></td>
                  <td className="amount-cell">{money(r.monthly_price)}</td>
                  <td>{r.current_occupants}</td>
                  <td>{r.max_occupants}</td>
                  <td>{r.remaining}</td>
                  <td><span className={`status-pill ${r.within_limit ? 'paid' : 'unpaid'}`}>{r.within_limit ? 'Trong sức chứa' : 'Vượt sức chứa'}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      <div className="management-grid">
        <article className="panel">
          <div className="panel-heading">
            <div><h2>Thêm phòng</h2><p>Mã phòng không được trùng.</p></div>
            <span className="heading-icon">＋</span>
          </div>
          <form onSubmit={saveRoom}>
            <div className="form-row">
              <label>Mã phòng
                <input required maxLength="15" value={roomForm.room_id} onChange={(e) => setRoomForm({ ...roomForm, room_id: e.target.value })} placeholder="P101" />
              </label>
              <label>Tên phòng
                <input required maxLength="30" value={roomForm.name} onChange={(e) => setRoomForm({ ...roomForm, name: e.target.value })} placeholder="Phòng 101" />
              </label>
            </div>
            <div className="form-row">
              <label>Tầng
                <input type="number" value={roomForm.floor} onChange={(e) => setRoomForm({ ...roomForm, floor: e.target.value })} />
              </label>
              <label>Đơn giá và sức chứa
                <select required value={roomForm.room_option} onChange={(e) => setRoomForm({ ...roomForm, room_option: e.target.value })}>
                  <option value="">Chọn mức phòng</option>
                  {ROOM_OPTIONS.map((option) => (
                    <option key={option.price} value={option.price}>{option.label}</option>
                  ))}
                </select>
              </label>
            </div>
            <button className="primary-button" type="submit" disabled={busy}>Thêm phòng</button>
          </form>
          <div className="table-wrap" style={{ marginTop: 16 }}>
            <table>
              <thead><tr><th>Phòng</th><th>Đơn giá/tháng</th><th>Ở/Tối đa</th><th></th></tr></thead>
              <tbody>
                {rooms.map((r) => (
                  <tr key={r.room_id}>
                    <td><strong>{r.room_id}</strong></td>
                    <td className="amount-cell">{money(r.monthly_price)}</td>
                    <td>{r.current_occupants}/{r.max_occupants}</td>
                    <td><button className="table-action danger" onClick={() => removeRoom(r)} disabled={busy}>Xóa</button></td>
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