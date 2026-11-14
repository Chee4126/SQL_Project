import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { API_URL, apiFetch } from './api'
import StudentsPage from './pages/StudentsPage'
import AccountsPage from './pages/AccountsPage'
import RoomsPage from './pages/RoomsPage'
import VisitorsPage from './pages/VisitorsPage'
import ProfilePage from './pages/ProfilePage'
import StudentSelect from './components/StudentSelect'

const PAYMENT_STATUSES = [
  { value: '', label: 'Tất cả trạng thái' },
  { value: 'CHUA_THANH_TOAN', label: 'Chưa thanh toán' },
  { value: 'DA_THANH_TOAN', label: 'Đã thanh toán' },
]

const currentDate = new Date()
const initialPeriod = {
  month: String(currentDate.getMonth() + 1),
  year: String(currentDate.getFullYear()),
}
const initialDateTime = new Date(Date.now() - currentDate.getTimezoneOffset() * 60000)
  .toISOString()
  .slice(0, 16)
const initialMonthEnd = new Date(
  Number(initialPeriod.year),
  Number(initialPeriod.month),
  0,
).getDate()

function formatCurrency(value) {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))
}

function getErrorMessage(error, fallback) {
  const translations = {
    'This field is required.': 'Trường này là bắt buộc.',
    'This field may not be blank.': 'Trường này không được để trống.',
    'A valid integer is required.': 'Giá trị phải là số nguyên hợp lệ.',
    'A valid number is required.': 'Giá trị phải là số hợp lệ.',
    'A valid date/time is required.': 'Thời điểm không hợp lệ.',
    'Not found.': 'Không tìm thấy dữ liệu yêu cầu.',
  }
  const translate = (message) => {
    if (typeof message !== 'string') return ''
    if (translations[message]) return translations[message]
    if (/^Invalid pk ".*" - object does not exist\.$/.test(message)) {
      return 'Không tìm thấy sinh viên hoặc dữ liệu liên quan đã chọn.'
    }
    if (/^Method "[A-Z]+" not allowed\.$/.test(message)) {
      return 'Thao tác này không được hỗ trợ.'
    }
    return /^[\x00-\x7F]*$/.test(message) && /[A-Za-z]/.test(message)
      ? fallback
      : message
  }
  if (typeof error === 'string') return translate(error) || fallback
  if (error && typeof error === 'object') {
    const messages = Object.values(error)
      .flat(Infinity)
      .map(translate)
      .filter(Boolean)
    return messages.join(' ') || fallback
  }
  return fallback
}

function getRequestErrorMessage(error, fallback) {
  if (error instanceof TypeError || error instanceof SyntaxError) {
    return 'Không thể kết nối máy chủ hoặc máy chủ trả về dữ liệu không hợp lệ.'
  }
  return getErrorMessage(error?.message, fallback)
}

function App({ user, onLogout, onUserUpdated }) {
  const [filters, setFilters] = useState({
    ...initialPeriod,
    status: '',
    student_id: '',
  })
  const [form, setForm] = useState({
    student_id: '',
    ...initialPeriod,
    room_amount: '',
  })
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [page, setPage] = useState('invoices')
  const [reportData, setReportData] = useState({
    costs: [],
    serviceUsage: [],
    serviceRevenue: [],
    vehicleLimits: [],
  })
  const [reportErrors, setReportErrors] = useState({})
  const [reportLoading, setReportLoading] = useState(false)
  const [printRequested, setPrintRequested] = useState(false)
  const [printMode, setPrintMode] = useState('list')
  const [reportStudentId, setReportStudentId] = useState('')
  const [services, setServices] = useState([])
  const [serviceUsages, setServiceUsages] = useState([])
  const [serviceLoading, setServiceLoading] = useState(false)
  const [serviceReportLoading, setServiceReportLoading] = useState(false)
  const [serviceSubmitting, setServiceSubmitting] = useState(false)
  const [serviceUsageSubmitting, setServiceUsageSubmitting] = useState(false)
  const [serviceForm, setServiceForm] = useState({ name: '', price: '', unit: '' })
  const [serviceUsageForm, setServiceUsageForm] = useState({
    student_id: '',
    service_id: '',
    used_at: initialDateTime,
    quantity: '1',
  })
  const [serviceDateRange, setServiceDateRange] = useState({
    date_from: `${initialPeriod.year}-${initialPeriod.month.padStart(2, '0')}-01`,
    date_to: `${initialPeriod.year}-${initialPeriod.month.padStart(2, '0')}-${String(initialMonthEnd).padStart(2, '0')}`,
  })
  const [editingServiceId, setEditingServiceId] = useState(null)
  const [serviceMessage, setServiceMessage] = useState('')
  const [serviceError, setServiceError] = useState('')
  const [serviceReportError, setServiceReportError] = useState('')
  const [registrations, setRegistrations] = useState([])
  const [registrationLoading, setRegistrationLoading] = useState(false)
  const [registrationSubmitting, setRegistrationSubmitting] = useState(false)
  const [eventSubmitting, setEventSubmitting] = useState(false)
  const [registrationForm, setRegistrationForm] = useState({
    student_id: '',
    plate_number: '',
    vehicle_type: 'Xe máy',
    month: initialPeriod.month,
    year: initialPeriod.year,
  })
  const [vehicleFilters, setVehicleFilters] = useState({
    month: initialPeriod.month,
    year: initialPeriod.year,
    student_id: '',
  })
  const [eventForm, setEventForm] = useState({
    registration_id: '',
    event_type: 'GUI',
    event_at: initialDateTime,
  })
  const [vehicleMessage, setVehicleMessage] = useState('')
  const [vehicleError, setVehicleError] = useState('')

  // Tải lại danh sách theo bộ lọc, đồng thời đưa lỗi API ra giao diện.
  const loadInvoices = useCallback(async () => {
    setLoading(true)
    setError('')
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value)
    })

    try {
      const response = await apiFetch(`${API_URL}/invoices?${params.toString()}`)
      const data = await response.json()
      if (!response.ok) throw new Error(getErrorMessage(data, 'Không thể tải hóa đơn.'))
      setInvoices(data)
    } catch (requestError) {
      setError(getRequestErrorMessage(requestError, 'Không thể tải danh sách hóa đơn.'))
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    if (page === 'invoices') loadInvoices()
  }, [page, loadInvoices])

  // Tải độc lập từng báo cáo để một API lỗi không ẩn kết quả các báo cáo khác.
  const loadReports = useCallback(async () => {
    setReportLoading(true)
    const month = Number(filters.month)
    const year = Number(filters.year)
    const dateFrom = `${year}-${String(month).padStart(2, '0')}-01`
    const lastDay = new Date(year, month, 0).getDate()
    const dateTo = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
    const requests = [
      ['costs', `/reports/monthly-student-costs?month=${month}&year=${year}`],
      [
        'serviceUsage',
        `/reports/service-usage?date_from=${dateFrom}&date_to=${dateTo}`,
      ],
      ['serviceRevenue', `/reports/service-revenue?month=${month}&year=${year}`],
      [
        'vehicleLimits',
        `/reports/vehicle-registration-limits?month=${month}&year=${year}`,
      ],
    ]

    try {
      const results = await Promise.all(
        requests.map(async ([key, path]) => {
          try {
            const response = await apiFetch(`${API_URL}${path}`)
            const data = await response.json()
            if (!response.ok) {
              throw new Error(getErrorMessage(data, 'Không thể tải báo cáo.'))
            }
            return [key, data, '']
          } catch (requestError) {
            return [
              key,
              [],
              getRequestErrorMessage(requestError, 'Không thể tải báo cáo.'),
            ]
          }
        }),
      )
      setReportData((previous) => {
        const next = { ...previous }
        results.forEach(([key, data, message]) => { next[key] = message ? [] : data })
        return next
      })
      setReportErrors(
        Object.fromEntries(results.filter(([, , message]) => message).map(([key, , message]) => [key, message])),
      )
    } finally {
      setReportLoading(false)
    }
  }, [filters.month, filters.year])

  useEffect(() => {
    if (page === 'reports') loadReports()
  }, [page, loadReports])

  useEffect(() => {
    if (!printRequested) return undefined

    const resetPrintRequest = () => setPrintRequested(false)
    window.addEventListener('afterprint', resetPrintRequest)
    window.print()
    return () => window.removeEventListener('afterprint', resetPrintRequest)
  }, [printRequested])

  // Tải danh mục dịch vụ; dữ liệu giá hiện tại không làm thay đổi giá đã chốt.
  const loadServices = useCallback(async () => {
    setServiceLoading(true)
    setServiceError('')
    try {
      const response = await apiFetch(`${API_URL}/services`)
      const data = await response.json()
      if (!response.ok) throw new Error(getErrorMessage(data, 'Không thể tải dịch vụ.'))
      setServices(data)
    } catch (requestError) {
      setServiceError(getRequestErrorMessage(requestError, 'Không thể tải danh mục dịch vụ.'))
    } finally {
      setServiceLoading(false)
    }
  }, [])

  // API báo cáo nhóm phát sinh theo sinh viên/dịch vụ trong khoảng ngày.
  const loadServiceUsages = useCallback(async () => {
    if (!serviceDateRange.date_from || !serviceDateRange.date_to) return
    setServiceReportLoading(true)
    setServiceReportError('')
    try {
      const params = new URLSearchParams(serviceDateRange)
      const response = await apiFetch(`${API_URL}/reports/service-usage?${params}`)
      const data = await response.json()
      if (!response.ok) throw new Error(getErrorMessage(data, 'Không thể tải báo cáo dịch vụ.'))
      setServiceUsages(data)
    } catch (requestError) {
      setServiceReportError(getRequestErrorMessage(requestError, 'Không thể tải báo cáo dịch vụ.'))
      setServiceUsages([])
    } finally {
      setServiceReportLoading(false)
    }
  }, [serviceDateRange])

  useEffect(() => {
    if (page === 'services') {
      loadServices()
      loadServiceUsages()
    }
  }, [page, loadServices, loadServiceUsages])

  // Tạo mới hoặc cập nhật danh mục qua API; đơn giá phải không âm.
  async function saveService(event) {
    event.preventDefault()
    setServiceSubmitting(true)
    setServiceError('')
    setServiceMessage('')
    try {
      const response = await apiFetch(
        `${API_URL}/services${editingServiceId ? `/${editingServiceId}` : ''}`,
        {
          method: editingServiceId ? 'PUT' : 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: serviceForm.name.trim(),
            price: serviceForm.price,
            unit: serviceForm.unit.trim(),
          }),
        },
      )
      const data = await response.json()
      if (!response.ok) throw new Error(getErrorMessage(data, 'Không thể lưu dịch vụ.'))
      setServiceMessage(
        editingServiceId
          ? `Đã cập nhật dịch vụ ${data.name}.`
          : `Đã thêm dịch vụ ${data.name}.`,
      )
      setServiceForm({ name: '', price: '', unit: '' })
      setEditingServiceId(null)
      await loadServices()
    } catch (requestError) {
      setServiceError(getRequestErrorMessage(requestError, 'Không thể lưu dịch vụ.'))
    } finally {
      setServiceSubmitting(false)
    }
  }

  // Ghi nhận sử dụng; backend tự chụp đơn giá dịch vụ ở thời điểm này.
  async function recordServiceUsage(event) {
    event.preventDefault()
    setServiceUsageSubmitting(true)
    setServiceError('')
    setServiceMessage('')
    try {
      const response = await apiFetch(`${API_URL}/service-usages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...serviceUsageForm,
          student_id: serviceUsageForm.student_id.trim(),
          quantity: Number(serviceUsageForm.quantity),
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(getErrorMessage(data, 'Không thể ghi nhận dịch vụ.'))
      setServiceMessage(
        `Đã ghi nhận ${data.quantity} đơn vị; đơn giá áp dụng ${formatCurrency(data.applied_price)}.`,
      )
      setServiceUsageForm((previous) => ({ ...previous, quantity: '1' }))
      await loadServiceUsages()
    } catch (requestError) {
      setServiceError(getRequestErrorMessage(requestError, 'Không thể ghi nhận sử dụng dịch vụ.'))
    } finally {
      setServiceUsageSubmitting(false)
    }
  }

  function startEditingService(service) {
    setEditingServiceId(service.id)
    setServiceForm({
      name: service.name,
      price: service.price,
      unit: service.unit,
    })
    setServiceMessage('')
    setServiceError('')
  }

  async function removeService(service) {
    if (!window.confirm(`Xóa dịch vụ "${service.name}"? Dịch vụ đã phát sinh lượt sử dụng sẽ không thể xóa.`)) return

    setServiceSubmitting(true)
    setServiceError('')
    setServiceMessage('')
    try {
      const response = await apiFetch(`${API_URL}/services/${service.id}`, { method: 'DELETE' })
      if (!response.ok) {
        const data = await response.json()
        throw new Error(getErrorMessage(data, 'Không thể xóa dịch vụ.'))
      }
      setServiceMessage(`Đã xóa dịch vụ ${service.name}.`)
      if (editingServiceId === service.id) {
        setEditingServiceId(null)
        setServiceForm({ name: '', price: '', unit: '' })
      }
      await loadServices()
    } catch (requestError) {
      setServiceError(getRequestErrorMessage(requestError, 'Không thể xóa dịch vụ.'))
    } finally {
      setServiceSubmitting(false)
    }
  }

  // Lọc danh sách đăng ký theo kỳ và mã sinh viên tùy chọn.
  const loadRegistrations = useCallback(async () => {
    setRegistrationLoading(true)
    setVehicleError('')
    const params = new URLSearchParams()
    Object.entries(vehicleFilters).forEach(([key, value]) => {
      if (value) params.set(key, value)
    })
    try {
      const response = await apiFetch(
        `${API_URL}/monthly-vehicle-registrations?${params}`,
      )
      const data = await response.json()
      if (!response.ok) throw new Error(getErrorMessage(data, 'Không thể tải đăng ký xe.'))
      setRegistrations(data)
    } catch (requestError) {
      setVehicleError(getRequestErrorMessage(requestError, 'Không thể tải đăng ký xe.'))
      setRegistrations([])
    } finally {
      setRegistrationLoading(false)
    }
  }, [vehicleFilters])

  useEffect(() => {
    if (page === 'vehicles') loadRegistrations()
  }, [page, loadRegistrations])

  // Đăng ký vé tháng; API áp giá mặc định và kiểm tra xe trùng/giới hạn 2 xe.
  async function registerVehicle(event) {
    event.preventDefault()
    setRegistrationSubmitting(true)
    setVehicleError('')
    setVehicleMessage('')
    try {
      const response = await apiFetch(`${API_URL}/monthly-vehicle-registrations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...registrationForm,
          student_id: registrationForm.student_id.trim(),
          plate_number: registrationForm.plate_number.trim().toUpperCase(),
          vehicle_type: registrationForm.vehicle_type.trim(),
          month: Number(registrationForm.month),
          year: Number(registrationForm.year),
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(getErrorMessage(data, 'Không thể đăng ký xe.'))
      setVehicleMessage(
        `Đã đăng ký ${data.vehicle.plate_number}; phí vé tháng ${formatCurrency(data.monthly_price)}.`,
      )
      setVehicleFilters((previous) => ({
        ...previous,
        month: String(data.month),
        year: String(data.year),
        student_id: data.student_id,
      }))
      setRegistrationForm((previous) => ({
        ...previous,
        plate_number: '',
      }))
    } catch (requestError) {
      setVehicleError(getRequestErrorMessage(requestError, 'Không thể đăng ký xe.'))
    } finally {
      setRegistrationSubmitting(false)
    }
  }

  // Ghi nhận lượt gửi/lấy của xe trong kỳ đăng ký.
  async function recordVehicleEvent(event) {
    event.preventDefault()
    setEventSubmitting(true)
    setVehicleError('')
    setVehicleMessage('')
    try {
      const response = await apiFetch(
        `${API_URL}/monthly-vehicle-registrations/${eventForm.registration_id}/events`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            event_type: eventForm.event_type,
            event_at: eventForm.event_at,
          }),
        },
      )
      const data = await response.json()
      if (!response.ok) throw new Error(getErrorMessage(data, 'Không thể ghi nhận lượt xe.'))
      setVehicleMessage('Đã ghi nhận lượt gửi/lấy xe.')
    } catch (requestError) {
      setVehicleError(getRequestErrorMessage(requestError, 'Không thể ghi nhận lượt xe.'))
    } finally {
      setEventSubmitting(false)
    }
  }

  // Backend tự tính tiền dịch vụ và vé tháng; lượt gửi/lấy không tính phí.
  async function generateInvoice(event) {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    setMessage('')

    const payload = {
      student_id: form.student_id.trim(),
      month: Number(form.month),
      year: Number(form.year),
    }
    if (form.room_amount !== '') payload.room_amount = form.room_amount

    try {
      const response = await apiFetch(`${API_URL}/invoices/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(getErrorMessage(data, 'Không thể lập hóa đơn.'))
      setMessage(`Đã lập hóa đơn ${data.id} cho ${data.student_name}.`)
      setFilters((previous) => ({
        ...previous,
        month: String(data.month),
        year: String(data.year),
        student_id: data.student_id,
      }))
    } catch (requestError) {
      setError(getRequestErrorMessage(requestError, 'Không thể lập hóa đơn.'))
    } finally {
      setSubmitting(false)
    }
  }

  // Chỉ gửi trạng thái, không cho giao diện thay đổi các khoản tiền.
  async function updateStatus(invoice) {
    const nextStatus =
      invoice.status === 'DA_THANH_TOAN' ? 'CHUA_THANH_TOAN' : 'DA_THANH_TOAN'
    setError('')
    setMessage('')

    try {
      const response = await apiFetch(`${API_URL}/invoices/${invoice.id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: nextStatus }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(getErrorMessage(data, 'Không thể cập nhật.'))
      setMessage(`Đã cập nhật trạng thái hóa đơn ${invoice.id}.`)
      await loadInvoices()
    } catch (requestError) {
      setError(getRequestErrorMessage(requestError, 'Không thể cập nhật trạng thái hóa đơn.'))
    }
  }

  const unpaidTotal = invoices
    .filter((invoice) => invoice.status === 'CHUA_THANH_TOAN')
    .reduce((sum, invoice) => sum + Number(invoice.total_amount), 0)
  const paidTotal = invoices
    .filter((invoice) => invoice.status === 'DA_THANH_TOAN')
    .reduce((sum, invoice) => sum + Number(invoice.total_amount), 0)
  const reportCostTotal = reportData.costs.reduce(
    (sum, row) => sum + Number(row.total_amount),
    0,
  )
  const reportServiceRevenue = reportData.serviceRevenue.reduce(
    (sum, row) => sum + Number(row.total_revenue),
    0,
  )
  const registeredVehicleStudents = reportData.vehicleLimits.length
  const registrationViolations = reportData.vehicleLimits.filter(
    (row) => !row.within_limit,
  ).length

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/" aria-label="Quản lý ký túc xá">
          <span className="brand-mark">K</span>
          <span>
            <strong>KTX Manager</strong>
            <small>Quản lý ký túc xá</small>
          </span>
        </a>
        <p className="nav-caption">QUẢN LÝ</p>
        <button
          className={`nav-item ${page === 'invoices' ? 'active' : ''}`}
          onClick={() => setPage('invoices')}
        >
          <span aria-hidden="true">▤</span> Hóa đơn
        </button>
        <button
          className={`nav-item ${page === 'reports' ? 'active' : ''}`}
          onClick={() => setPage('reports')}
        >
          <span aria-hidden="true">▥</span> Báo cáo & thống kê
        </button>
        <button
          className={`nav-item ${page === 'services' ? 'active' : ''}`}
          onClick={() => setPage('services')}
        >
          <span aria-hidden="true">◈</span> Quản lý dịch vụ
        </button>
                  <button
          className={`nav-item ${page === 'vehicles' ? 'active' : ''}`}
          onClick={() => setPage('vehicles')}
        >
          <span aria-hidden="true">▰</span> Quản lý xe
        </button>
        <button
          className={`nav-item ${page === 'students' ? 'active' : ''}`}
          onClick={() => setPage('students')}
        >
          <span aria-hidden="true">☰</span> Sinh viên
        </button>
                <button
          className={`nav-item ${page === 'rooms' ? 'active' : ''}`}
          onClick={() => setPage('rooms')}
        >
          <span aria-hidden="true">⌂</span> Phòng ở
        </button>
        <button
          className={`nav-item ${page === 'visitors' ? 'active' : ''}`}
          onClick={() => setPage('visitors')}
        >
          <span aria-hidden="true">☺</span> Khách thăm
        </button>
        <button
          className={`nav-item ${page === 'accounts' ? 'active' : ''}`}
          onClick={() => setPage('accounts')}
        >
          <span aria-hidden="true">⚿</span> Tài khoản
        </button>
        <button
          className={`nav-item ${page === 'profile' ? 'active' : ''}`}
          onClick={() => setPage('profile')}
        >
          <span aria-hidden="true">◎</span> Hồ sơ tài khoản
        </button>
        <div className="sidebar-note">
          <span aria-hidden="true">i</span>
          <p>
            {{
              invoices: 'Hóa đơn tự cập nhật khi phát sinh tiền phòng, dịch vụ hoặc vé tháng.',
              reports: 'Báo cáo chỉ tổng hợp trên các nguồn dữ liệu đã có trong hệ thống.',
              services: 'Giá dịch vụ được lưu theo từng lần sử dụng để bảo toàn lịch sử.',
              vehicles: 'Mỗi sinh viên tối đa 2 xe vé tháng; lượt gửi/lấy phải thuộc kỳ đăng ký.',
              students: 'Hồ sơ sinh viên là cơ sở cho phân phòng, dịch vụ, xe và hóa đơn.',
              rooms: 'Đơn giá và sức chứa được cấu hình trực tiếp trên từng phòng.',
              visitors: 'Mỗi lượt thăm ghi nhận thời gian đến và rời đi của khách.',
              accounts: 'Quản lý danh sách và tạo tài khoản Staff.',
              profile: 'Cập nhật thông tin cá nhân và mật khẩu tài khoản.',
            }[page]}
          </p>
        </div>
      </aside>

      <main className="main-content" id={page}>
        <header className="topbar">
          <div>
            <p className="eyebrow">
              {{
                invoices: 'TÀI CHÍNH / HÓA ĐƠN',
                reports: 'TỔNG QUAN / BÁO CÁO',
                services: 'VẬN HÀNH / DỊCH VỤ',
                vehicles: 'VẬN HÀNH / XE THÁNG',
                students: 'DANH MỤC / SINH VIÊN',
                rooms: 'DANH MỤC / PHÒNG Ở',
                visitors: 'VẬN HÀNH / KHÁCH THĂM',
                accounts: 'HỆ THỐNG / TÀI KHOẢN',
                profile: 'TÀI KHOẢN / HỒ SƠ',
              }[page]}
            </p>
            <h1>
              {{
                invoices: 'Quản lý hóa đơn',
                reports: 'Báo cáo & thống kê',
                services: 'Quản lý dịch vụ',
                vehicles: 'Quản lý xe',
                students: 'Quản lý sinh viên',
                rooms: 'Quản lý phòng',
                visitors: 'Quản lý khách thăm',
                accounts: 'Quản lý tài khoản',
                profile: 'Hồ sơ tài khoản',
              }[page]}
            </h1>
          </div>
          <span className="user-badge">
            <span /> {user.username} (Staff)
            <button className="table-action" onClick={onLogout}>Đăng xuất</button>
          </span>
        </header>

        <section className="intro">
          <div>
            <h2>
              {{
                invoices: 'Hóa đơn hàng tháng',
                reports: 'Báo cáo hoạt động',
                services: 'Danh mục và sử dụng dịch vụ',
                vehicles: 'Đăng ký vé tháng và lượt gửi/lấy',
                students: 'Hồ sơ sinh viên',
                rooms: 'Phòng và phân phòng',
                visitors: 'Khách và lượt thăm',
                accounts: 'Tài khoản nhân viên',
                profile: 'Thông tin cá nhân và bảo mật tài khoản',
              }[page]}
            </h2>
            <p>
              {{
                invoices: 'Hóa đơn tự cập nhật khi phát sinh tiền phòng, dịch vụ hoặc vé tháng.',
                reports: 'Tổng hợp chi phí, dịch vụ và đăng ký xe theo tháng được chọn.',
                services: 'Quản lý đơn giá, ghi nhận sử dụng và xem tổng hợp theo ngày.',
                vehicles: 'Quản lý đăng ký xe và ghi nhận lượt gửi/lấy trong kỳ.',
                students: 'Tìm kiếm, thêm mới và cập nhật hồ sơ sinh viên.',
                rooms: 'Quản lý phòng, đơn giá, sức chứa và lịch sử phân phòng.',
                visitors: 'Ghi nhận khách đến thăm và thống kê theo tuần hoặc tháng.',
                accounts: 'Tạo tài khoản cho nhân viên vận hành hệ thống.',
                profile: 'Cập nhật thông tin cá nhân hoặc đổi mật khẩu.',
              }[page]}
            </p>
          </div>
          {['invoices', 'reports', 'services', 'vehicles'].includes(page) && (
            <div className="period-tag">Kỳ {filters.month}/{filters.year}</div>
          )}
        </section>

        {page === 'invoices' ? (
          <>
        <section className="summary-grid" aria-label="Tổng quan hóa đơn">
          <article className="summary-card">
            <span className="summary-icon icon-blue">▤</span>
            <div><p>Tổng hóa đơn</p><strong>{invoices.length}</strong></div>
            <small>Trong danh sách hiện tại</small>
          </article>
          <article className="summary-card">
            <span className="summary-icon icon-orange">◷</span>
            <div><p>Chưa thanh toán</p><strong>{formatCurrency(unpaidTotal)}</strong></div>
            <small>Khoản cần thu</small>
          </article>
          <article className="summary-card">
            <span className="summary-icon icon-green">✓</span>
            <div><p>Đã thanh toán</p><strong>{formatCurrency(paidTotal)}</strong></div>
            <small>Đã thu trong danh sách</small>
          </article>
        </section>
          </>
        ) : page === 'reports' ? (
          <section className="report-page">
            <div className="report-toolbar panel">
              <div>
                <h2>Kỳ báo cáo</h2>
                <p>Chọn tháng và năm để tải lại các thống kê.</p>
              </div>
              <div className="report-period-controls">
                <label>
                  Tháng
                  <input
                    type="number"
                    min="1"
                    max="12"
                    value={filters.month}
                    onChange={(event) => setFilters({ ...filters, month: event.target.value })}
                  />
                </label>
                <label>
                  Năm
                  <input
                    type="number"
                    min="1"
                    max="9999"
                    value={filters.year}
                    onChange={(event) => setFilters({ ...filters, year: event.target.value })}
                  />
                </label>
                <button className="refresh-button" onClick={loadReports} disabled={reportLoading}>
                  ↻ <span>{reportLoading ? 'Đang tải' : 'Làm mới'}</span>
                </button>
              </div>
            </div>

            <section className="summary-grid report-summary" aria-label="Tóm tắt báo cáo">
              <article className="summary-card">
                <span className="summary-icon icon-blue">₫</span>
                <div><p>Tổng chi phí tháng</p><strong>{formatCurrency(reportCostTotal)}</strong></div>
                <small>{reportData.costs.length} sinh viên nội trú</small>
              </article>
              <article className="summary-card">
                <span className="summary-icon icon-green">↗</span>
                <div><p>Doanh thu dịch vụ</p><strong>{formatCurrency(reportServiceRevenue)}</strong></div>
                <small>Giá tại thời điểm sử dụng</small>
              </article>
              <article className="summary-card">
                <span className="summary-icon icon-orange">▣</span>
                <div><p>Sinh viên có đăng ký xe</p><strong>{registeredVehicleStudents}</strong></div>
                <small>{registrationViolations} trường hợp vượt giới hạn</small>
              </article>
            </section>

            <article
              className="panel report-panel"
              id="monthly-student-cost-report"
              data-print-mode={printMode}
            >
              <div className="panel-heading">
                <div>
                  <h2>Chi phí theo sinh viên</h2>
                  <p>Tổng hợp tiền phòng, dịch vụ và vé xe trong tháng, xếp theo tên sinh viên.</p>
                </div>
                <div className="report-print-controls no-print">
                  <button
                    className="refresh-button"
                    onClick={() => {
                      setPrintMode('list')
                      setPrintRequested(true)
                    }}
                    disabled={reportLoading || reportData.costs.length === 0}
                  >
                    In danh sách
                  </button>
                  <label>
                    Sinh viên cần in
                    <select
                      value={reportStudentId}
                      onChange={(event) => setReportStudentId(event.target.value)}
                      disabled={reportLoading || reportData.costs.length === 0}
                    >
                      <option value="">Chọn sinh viên</option>
                      {reportData.costs.map((row) => (
                        <option key={row.student_id} value={row.student_id}>
                          {row.student_name} ({row.student_id})
                        </option>
                      ))}
                    </select>
                  </label>
                  <button
                    className="refresh-button"
                    onClick={() => {
                      setPrintMode('student')
                      setPrintRequested(true)
                    }}
                    disabled={
                      reportLoading ||
                      !reportData.costs.some((row) => row.student_id === reportStudentId)
                    }
                  >
                    In cá nhân
                  </button>
                </div>
              </div>
              <p className="print-period">
                Báo cáo chi phí tháng {filters.month}/{filters.year}
              </p>
              {reportErrors.costs ? (
                <div className="notice error" role="alert">{reportErrors.costs}</div>
              ) : (
                <>
                  <div className="table-wrap cost-list-print">
                    <table>
                      <thead>
                        <tr>
                          <th>Sinh viên</th><th>Phòng</th><th>Dịch vụ</th><th>Vé xe</th>
                          <th>Tổng phải trả</th>
                        </tr>
                      </thead>
                      <tbody>
                        {reportData.costs.length === 0 ? (
                          <tr><td className="empty-state" colSpan="5">Không có sinh viên nội trú trong kỳ.</td></tr>
                        ) : reportData.costs.map((row) => (
                          <tr key={row.student_id}>
                            <td><strong>{row.student_name}</strong><small className="cell-subtitle">{row.student_id}</small></td>
                            <td>{formatCurrency(row.room_amount)}</td>
                            <td>{formatCurrency(row.service_amount)}</td>
                            <td>{formatCurrency(row.vehicle_amount)}</td>
                            <td className="amount-cell">{formatCurrency(row.total_amount)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {reportData.costs.filter((row) => row.student_id === reportStudentId).map((row) => (
                    <section className="student-print-only" key={row.student_id}>
                      <h2>{row.student_name}</h2>
                      <p>Mã sinh viên: {row.student_id}</p>
                      <p>Kỳ thanh toán: {filters.month}/{filters.year}</p>
                      <table>
                        <tbody>
                          <tr><th>Tiền phòng</th><td>{formatCurrency(row.room_amount)}</td></tr>
                          <tr><th>Tiền dịch vụ</th><td>{formatCurrency(row.service_amount)}</td></tr>
                          <tr><th>Tiền vé xe</th><td>{formatCurrency(row.vehicle_amount)}</td></tr>
                          <tr><th>Tổng phải trả</th><td className="amount-cell">{formatCurrency(row.total_amount)}</td></tr>
                        </tbody>
                      </table>
                    </section>
                  ))}
                </>
              )}
            </article>

            <div className="report-tables">
              <article className="panel report-panel">
                <div className="panel-heading">
                  <div><h2>Sử dụng dịch vụ</h2><p>Số lượng và chi phí từ ngày đầu đến ngày cuối tháng.</p></div>
                </div>
                {reportErrors.serviceUsage ? (
                  <div className="notice error" role="alert">{reportErrors.serviceUsage}</div>
                ) : (
                  <div className="table-wrap">
                    <table>
                      <thead><tr><th>Sinh viên</th><th>Dịch vụ</th><th>Số lượng</th><th>Thành tiền</th></tr></thead>
                      <tbody>
                        {reportData.serviceUsage.length === 0 ? (
                          <tr><td className="empty-state" colSpan="4">Không có phát sinh dịch vụ.</td></tr>
                        ) : reportData.serviceUsage.map((row) => (
                          <tr key={`${row.student_id}-${row.service_id}`}>
                            <td>{row.student_name}</td><td>{row.service_name}</td>
                            <td>{row.total_quantity}</td><td>{formatCurrency(row.total_amount)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </article>

              <article className="panel report-panel">
                <div className="panel-heading">
                  <div><h2>Doanh thu dịch vụ</h2><p>Thống kê theo danh mục dịch vụ trong tháng.</p></div>
                </div>
                {reportErrors.serviceRevenue ? (
                  <div className="notice error" role="alert">{reportErrors.serviceRevenue}</div>
                ) : (
                  <div className="table-wrap">
                    <table>
                      <thead><tr><th>Dịch vụ</th><th>Số lượng</th><th>Doanh thu</th></tr></thead>
                      <tbody>
                        {reportData.serviceRevenue.length === 0 ? (
                          <tr><td className="empty-state" colSpan="3">Chưa có dịch vụ trong danh mục.</td></tr>
                        ) : reportData.serviceRevenue.map((row) => (
                          <tr key={row.service_id}>
                            <td>{row.service_name}</td>
                            <td>{row.total_quantity} {row.unit}</td>
                            <td className="amount-cell">{formatCurrency(row.total_revenue)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </article>
            </div>

            <article className="panel report-panel">
              <div className="panel-heading">
                <div><h2>Kiểm tra giới hạn xe tháng</h2><p>Mỗi sinh viên được đăng ký tối đa 2 xe trong một kỳ.</p></div>
              </div>
              {reportErrors.vehicleLimits ? (
                <div className="notice error" role="alert">{reportErrors.vehicleLimits}</div>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Sinh viên</th><th>Số xe đăng ký</th><th>Kiểm tra</th></tr></thead>
                    <tbody>
                      {reportData.vehicleLimits.length === 0 ? (
                        <tr><td className="empty-state" colSpan="3">Không có đăng ký xe trong kỳ.</td></tr>
                      ) : reportData.vehicleLimits.map((row) => (
                        <tr key={row.student_id}>
                          <td>{row.student_name} <small className="cell-subtitle">{row.student_id}</small></td>
                          <td>{row.registration_count}</td>
                          <td><span className={`status-pill ${row.within_limit ? 'paid' : 'unpaid'}`}>
                            {row.within_limit ? 'Trong giới hạn' : 'Vượt giới hạn'}
                          </span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </article>

          </section>
        ) : null}

        {page === 'invoices' && (
        <section className="content-grid">
          <article className="panel generate-panel">
            <div className="panel-heading">
              <div>
                <h2>Lập hóa đơn</h2>
                <p>Tổng hợp các khoản phát sinh trong kỳ.</p>
              </div>
              <span className="heading-icon">＋</span>
            </div>
            <form onSubmit={generateInvoice}>
              <StudentSelect
                label="Sinh viên"
                value={form.student_id}
                onChange={(event) => setForm({ ...form, student_id: event.target.value })}
              />
              <div className="form-row">
                <label>
                  Tháng
                  <input
                    required
                    type="number"
                    min="1"
                    max="12"
                    value={form.month}
                    onChange={(event) => setForm({ ...form, month: event.target.value })}
                  />
                </label>
                <label>
                  Năm
                  <input
                    required
                    type="number"
                    min="1"
                    max="9999"
                    value={form.year}
                    onChange={(event) => setForm({ ...form, year: event.target.value })}
                  />
                </label>
              </div>
              <label>
                Tiền phòng (VNĐ)
                <input
                  required
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.room_amount}
                  onChange={(event) => setForm({ ...form, room_amount: event.target.value })}
                  placeholder="Nhập khoản tiền phòng"
                />
              </label>
              <button className="primary-button" type="submit" disabled={submitting}>
                {submitting ? 'Đang tổng hợp...' : 'Tạo / cập nhật hóa đơn'}
              </button>
            </form>
          </article>

          <article className="panel invoice-panel">
            <div className="panel-heading list-heading">
              <div>
                <h2>Danh sách hóa đơn</h2>
                <p>{invoices.length} hóa đơn phù hợp bộ lọc</p>
              </div>
              <button className="refresh-button" onClick={loadInvoices} disabled={loading}>
                ↻ <span>Làm mới</span>
              </button>
            </div>
            <div className="filters">
              <label>
                Tháng
                <input
                  type="number"
                  min="1"
                  max="12"
                  value={filters.month}
                  onChange={(event) => setFilters({ ...filters, month: event.target.value })}
                />
              </label>
              <label>
                Năm
                <input
                  type="number"
                  min="1"
                  max="9999"
                  value={filters.year}
                  onChange={(event) => setFilters({ ...filters, year: event.target.value })}
                />
              </label>
              <label>
                Trạng thái
                <select
                  value={filters.status}
                  onChange={(event) => setFilters({ ...filters, status: event.target.value })}
                >
                  {PAYMENT_STATUSES.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </label>
              <StudentSelect
                label="Sinh viên"
                value={filters.student_id}
                includeAll
                onChange={(event) => setFilters({ ...filters, student_id: event.target.value })}
              />
            </div>

            {message && <div className="notice success" role="status">{message}</div>}
            {error && <div className="notice error" role="alert">{error}</div>}

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Sinh viên</th>
                    <th>Kỳ</th>
                    <th>Chi tiết khoản thu</th>
                    <th>Tổng tiền</th>
                    <th>Trạng thái</th>
                    <th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td className="empty-state" colSpan="6">Đang tải dữ liệu...</td></tr>
                  ) : invoices.length === 0 ? (
                    <tr><td className="empty-state" colSpan="6">Chưa có hóa đơn phù hợp.</td></tr>
                  ) : invoices.map((invoice) => (
                    <tr key={invoice.id}>
                      <td>
                        <strong>{invoice.student_name}</strong>
                        <small className="cell-subtitle">{invoice.student_id}</small>
                      </td>
                      <td>{String(invoice.month).padStart(2, '0')}/{invoice.year}</td>
                      <td>
                        <details>
                          <summary>Xem các khoản</summary>
                          <div className="breakdown">
                            <span>Phòng <b>{formatCurrency(invoice.room_amount)}</b></span>
                            <span>Dịch vụ <b>{formatCurrency(invoice.service_amount)}</b></span>
                            {invoice.service_lines?.length ? (
                              <div className="invoice-service-lines">
                                {invoice.service_lines.map((line) => (
                                  <div key={line.id}>
                                    {line.service_name} — {line.quantity}{line.unit ? ` ${line.unit}` : ''}
                                    {' × '}{formatCurrency(line.applied_price)}
                                    {' = '}{formatCurrency(line.amount)}
                                  </div>
                                ))}
                              </div>
                            ) : Number(invoice.service_amount) > 0 ? (
                              <span>Chi tiết dịch vụ chưa có</span>
                            ) : (
                              <span>Không phát sinh dịch vụ</span>
                            )}
                            <span>Vé xe <b>{formatCurrency(invoice.vehicle_amount)}</b></span>
                            <span>Gửi xe <b>{formatCurrency(invoice.parking_amount)}</b></span>
                          </div>
                        </details>
                      </td>
                      <td className="amount-cell">{formatCurrency(invoice.total_amount)}</td>
                      <td>
                        <span className={`status-pill ${invoice.status === 'DA_THANH_TOAN' ? 'paid' : 'unpaid'}`}>
                          {invoice.status === 'DA_THANH_TOAN' ? 'Đã thanh toán' : 'Chưa thanh toán'}
                        </span>
                      </td>
                      <td>
                        <button className="table-action" onClick={() => updateStatus(invoice)}>
                          {invoice.status === 'DA_THANH_TOAN' ? 'Đánh dấu chưa thu' : 'Đánh dấu đã thu'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>
        </section>
        )}

        {page === 'services' && (
          <section className="management-page">
            {serviceMessage && <div className="notice success" role="status">{serviceMessage}</div>}
            {serviceError && <div className="notice error" role="alert">{serviceError}</div>}

            <div className="management-grid">
              <article className="panel">
                <div className="panel-heading">
                  <div>
                    <h2>{editingServiceId ? 'Cập nhật dịch vụ' : 'Thêm dịch vụ'}</h2>
                    <p>Khai báo tên, đơn giá hiện hành và đơn vị tính.</p>
                  </div>
                  <span className="heading-icon">◈</span>
                </div>
                <form onSubmit={saveService}>
                  <label>
                    Tên dịch vụ
                    <input
                      required
                      maxLength="100"
                      value={serviceForm.name}
                      onChange={(event) => setServiceForm({ ...serviceForm, name: event.target.value })}
                      placeholder="Ví dụ: Giặt là"
                    />
                  </label>
                  <label>
                    Đơn giá (VNĐ)
                    <input
                      required
                      type="number"
                      min="0"
                      step="0.01"
                      value={serviceForm.price}
                      onChange={(event) => setServiceForm({ ...serviceForm, price: event.target.value })}
                      placeholder="15000"
                    />
                  </label>
                  <label>
                    Đơn vị tính
                    <input
                      maxLength="30"
                      value={serviceForm.unit}
                      onChange={(event) => setServiceForm({ ...serviceForm, unit: event.target.value })}
                      placeholder="kg, lần, chai..."
                    />
                  </label>
                  <div className="form-actions">
                    <button className="primary-button" type="submit" disabled={serviceSubmitting}>
                      {serviceSubmitting ? 'Đang lưu...' : editingServiceId ? 'Lưu thay đổi' : 'Thêm dịch vụ'}
                    </button>
                    {editingServiceId && (
                      <button
                        className="secondary-button"
                        type="button"
                        onClick={() => {
                          setEditingServiceId(null)
                          setServiceForm({ name: '', price: '', unit: '' })
                        }}
                      >
                        Hủy
                      </button>
                    )}
                  </div>
                </form>
              </article>

              <article className="panel">
                <div className="panel-heading list-heading">
                  <div>
                    <h2>Danh mục dịch vụ</h2>
                    <p>{services.length} dịch vụ</p>
                  </div>
                  <button className="refresh-button" onClick={loadServices} disabled={serviceLoading}>
                    ↻ <span>Làm mới</span>
                  </button>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Mã</th><th>Tên dịch vụ</th><th>Đơn vị</th><th>Đơn giá</th><th></th></tr></thead>
                    <tbody>
                      {serviceLoading && services.length === 0 ? (
                        <tr><td className="empty-state" colSpan="5">Đang tải dịch vụ...</td></tr>
                      ) : services.length === 0 ? (
                        <tr><td className="empty-state" colSpan="5">Chưa có dịch vụ.</td></tr>
                      ) : services.map((service) => (
                        <tr key={service.id}>
                          <td>DV{String(service.id).padStart(3, '0')}</td>
                          <td><strong>{service.name}</strong></td>
                          <td>{service.unit || '—'}</td>
                          <td className="amount-cell">{formatCurrency(service.price)}</td>
                          <td>
                            <button className="table-action" onClick={() => startEditingService(service)}>
                              Sửa
                            </button>
                            {' · '}
                            <button className="table-action danger" onClick={() => removeService(service)} disabled={serviceSubmitting}>
                              Xóa
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </article>
            </div>

            <article className="panel">
              <div className="panel-heading">
                <div>
                  <h2>Ghi nhận sử dụng dịch vụ</h2>
                  <p>Mỗi lần sử dụng được tính theo đơn giá tại thời điểm ghi nhận.</p>
                </div>
                <span className="heading-icon">＋</span>
              </div>
              <form className="record-form" onSubmit={recordServiceUsage}>
                <StudentSelect
                  label="Sinh viên"
                  value={serviceUsageForm.student_id}
                  onChange={(event) => setServiceUsageForm({ ...serviceUsageForm, student_id: event.target.value })}
                />
                <label>
                  Dịch vụ
                  <select
                    required
                    value={serviceUsageForm.service_id}
                    onChange={(event) => setServiceUsageForm({ ...serviceUsageForm, service_id: event.target.value })}
                  >
                    <option value="">Chọn dịch vụ</option>
                    {services.map((service) => (
                      <option key={service.id} value={service.id}>
                        {service.name} — {formatCurrency(service.price)}/{service.unit || 'đơn vị'}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Thời điểm sử dụng
                  <input
                    required
                    type="datetime-local"
                    value={serviceUsageForm.used_at}
                    onChange={(event) => setServiceUsageForm({ ...serviceUsageForm, used_at: event.target.value })}
                  />
                </label>
                <label>
                  Số lượng
                  <input
                    required
                    type="number"
                    min="1"
                    step="1"
                    value={serviceUsageForm.quantity}
                    onChange={(event) => setServiceUsageForm({ ...serviceUsageForm, quantity: event.target.value })}
                  />
                </label>
                <button className="primary-button" type="submit" disabled={serviceUsageSubmitting || services.length === 0}>
                  {serviceUsageSubmitting ? 'Đang ghi nhận...' : 'Ghi nhận sử dụng'}
                </button>
              </form>
            </article>

            <article className="panel report-panel">
              <div className="panel-heading list-heading">
                <div>
                  <h2>Tổng hợp sử dụng</h2>
                  <p>Báo cáo nhóm theo sinh viên và dịch vụ trong khoảng ngày.</p>
                </div>
                <div className="date-range-controls">
                  <label>Từ ngày<input type="date" value={serviceDateRange.date_from} onChange={(event) => setServiceDateRange({ ...serviceDateRange, date_from: event.target.value })} /></label>
                  <label>Đến ngày<input type="date" value={serviceDateRange.date_to} onChange={(event) => setServiceDateRange({ ...serviceDateRange, date_to: event.target.value })} /></label>
                  <button className="refresh-button" onClick={loadServiceUsages} disabled={serviceReportLoading}>
                    {serviceReportLoading ? 'Đang tải...' : 'Lọc'}
                  </button>
                </div>
              </div>
              {serviceReportError ? (
                <div className="notice error" role="alert">{serviceReportError}</div>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Sinh viên</th><th>Dịch vụ</th><th>Số lượng</th><th>Tổng tiền</th></tr></thead>
                    <tbody>
                      {serviceUsages.length === 0 ? (
                        <tr><td className="empty-state" colSpan="4">Không có phát sinh trong khoảng ngày.</td></tr>
                      ) : serviceUsages.map((usage) => (
                        <tr key={`${usage.student_id}-${usage.service_id}`}>
                          <td><strong>{usage.student_name}</strong><small className="cell-subtitle">{usage.student_id}</small></td>
                          <td>{usage.service_name}</td>
                          <td>{usage.total_quantity}</td>
                          <td className="amount-cell">{formatCurrency(usage.total_amount)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </article>
          </section>
        )}

        {page === 'vehicles' && (
          <section className="management-page">
            {vehicleMessage && <div className="notice success" role="status">{vehicleMessage}</div>}
            {vehicleError && <div className="notice error" role="alert">{vehicleError}</div>}

            <div className="management-grid vehicle-management-grid">
              <article className="panel">
                <div className="panel-heading">
                  <div>
                    <h2>Đăng ký xe vé tháng</h2>
                    <p>Đăng ký một xe cho sinh viên trong kỳ được chọn.</p>
                  </div>
                  <span className="heading-icon">▰</span>
                </div>
                <form onSubmit={registerVehicle}>
                  <StudentSelect
                    label="Sinh viên"
                    value={registrationForm.student_id}
                    onChange={(event) => setRegistrationForm({ ...registrationForm, student_id: event.target.value })}
                    disabled={registrationSubmitting}
                  />
                  <label>
                    Biển số xe
                    <input
                      required
                      maxLength="20"
                      value={registrationForm.plate_number}
                      onChange={(event) => setRegistrationForm({ ...registrationForm, plate_number: event.target.value.toUpperCase() })}
                      placeholder="51A-12345"
                    />
                  </label>
                  <label>
                    Loại xe
                    <input
                      required
                      maxLength="50"
                      value={registrationForm.vehicle_type}
                      onChange={(event) => setRegistrationForm({ ...registrationForm, vehicle_type: event.target.value })}
                    />
                  </label>
                  <div className="form-row">
                    <label>
                      Tháng
                      <input required type="number" min="1" max="12" value={registrationForm.month} onChange={(event) => setRegistrationForm({ ...registrationForm, month: event.target.value })} />
                    </label>
                    <label>
                      Năm
                      <input required type="number" min="1" max="9999" value={registrationForm.year} onChange={(event) => setRegistrationForm({ ...registrationForm, year: event.target.value })} />
                    </label>
                  </div>
                  <button className="primary-button" type="submit" disabled={registrationSubmitting}>
                    {registrationSubmitting ? 'Đang đăng ký...' : 'Đăng ký xe'}
                  </button>
                </form>
              </article>

              <article className="panel">
                <div className="panel-heading list-heading">
                  <div>
                    <h2>Đăng ký trong kỳ</h2>
                    <p>{registrations.length} xe đã đăng ký</p>
                  </div>
                  <button className="refresh-button" onClick={loadRegistrations} disabled={registrationLoading}>
                    ↻ <span>Làm mới</span>
                  </button>
                </div>
                <div className="filters vehicle-filters">
                  <label>
                    Tháng
                    <input type="number" min="1" max="12" value={vehicleFilters.month} onChange={(event) => setVehicleFilters({ ...vehicleFilters, month: event.target.value })} />
                  </label>
                  <label>
                    Năm
                    <input type="number" min="1" max="9999" value={vehicleFilters.year} onChange={(event) => setVehicleFilters({ ...vehicleFilters, year: event.target.value })} />
                  </label>
                  <StudentSelect
                    label="Sinh viên"
                    value={vehicleFilters.student_id}
                    includeAll
                    onChange={(event) => setVehicleFilters({ ...vehicleFilters, student_id: event.target.value })}
                  />
                </div>
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Sinh viên</th><th>Biển số</th><th>Loại xe</th><th>Phí vé tháng</th><th>Lượt xe</th></tr></thead>
                    <tbody>
                      {registrationLoading && registrations.length === 0 ? (
                        <tr><td className="empty-state" colSpan="5">Đang tải đăng ký...</td></tr>
                      ) : registrations.length === 0 ? (
                        <tr><td className="empty-state" colSpan="5">Chưa có xe đăng ký trong kỳ.</td></tr>
                      ) : registrations.map((registration) => (
                        <tr key={registration.id}>
                          <td>
                            <strong>{registration.student_name}</strong>
                            <small className="cell-subtitle">{registration.student_id}</small>
                          </td>
                          <td><strong>{registration.vehicle.plate_number}</strong></td>
                          <td>{registration.vehicle.vehicle_type}</td>
                          <td className="amount-cell">{formatCurrency(registration.monthly_price)}</td>
                          <td>
                            <button
                              className="table-action"
                              onClick={() => setEventForm({
                                registration_id: String(registration.id),
                                event_type: 'GUI',
                                event_at: initialDateTime,
                              })}
                            >
                              Ghi lượt
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </article>
            </div>

            {eventForm.registration_id && (
              <article className="panel">
                <div className="panel-heading">
                  <div>
                    <h2>Ghi nhận lượt gửi / lấy</h2>
                    <p>Mã đăng ký #{eventForm.registration_id}</p>
                  </div>
                  <button className="refresh-button" onClick={() => setEventForm({ ...eventForm, registration_id: '' })}>
                    Đóng
                  </button>
                </div>
                <form className="record-form" onSubmit={recordVehicleEvent}>
                  <label>
                    Loại lượt
                    <select value={eventForm.event_type} onChange={(event) => setEventForm({ ...eventForm, event_type: event.target.value })}>
                      <option value="GUI">Gửi xe</option>
                      <option value="LAY">Lấy xe</option>
                    </select>
                  </label>
                  <label>
                    Thời điểm
                    <input required type="datetime-local" value={eventForm.event_at} onChange={(event) => setEventForm({ ...eventForm, event_at: event.target.value })} />
                  </label>
                  <button className="primary-button" type="submit" disabled={eventSubmitting}>
                    {eventSubmitting ? 'Đang ghi nhận...' : 'Ghi nhận lượt xe'}
                  </button>
                </form>
              </article>
            )}

          </section>
        )}
        {page === 'students' && <StudentsPage />}
        {page === 'rooms' && <RoomsPage />}
        {page === 'visitors' && <VisitorsPage />}
        {page === 'accounts' && <AccountsPage user={user} />}
        {page === 'profile' && (
          <ProfilePage user={user} onUserUpdated={onUserUpdated} />
        )}
      </main>
    </div>
  )
}

export default App
