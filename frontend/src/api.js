export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'
const TOKEN_KEY = 'ktx_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

// Giống fetch nhưng tự gắn token; gặp 401 thì báo cho ứng dụng quay về trang đăng nhập.
export async function apiFetch(url, options = {}) {
  const headers = { ...(options.headers || {}) }
  const token = getToken()
  if (token) headers.Authorization = `Token ${token}`
  const response = await fetch(url, { ...options, headers })
  if (response.status === 401) {
    clearToken()
    window.dispatchEvent(new Event('auth:logout'))
  }
  return response
}

const TRANSLATIONS = {
  'This field is required.': 'Trường này là bắt buộc.',
  'This field may not be blank.': 'Trường này không được để trống.',
  'This field may not be null.': 'Trường này không được để trống.',
  'Date has wrong format. Use one of these formats instead: YYYY-MM-DD.': 'Ngày phải có dạng YYYY-MM-DD.',
  'Not found.': 'Không tìm thấy dữ liệu yêu cầu.',
}

// Gom lỗi backend trả về thành một câu tiếng Việt.
export function errorText(data) {
  if (!data) return 'Có lỗi xảy ra.'
  if (typeof data === 'string') return data
  if (data.detail) return TRANSLATIONS[data.detail] || data.detail
  const messages = Object.values(data).flat(Infinity).map((m) => TRANSLATIONS[m] || m)
  return messages.join(' ') || 'Có lỗi xảy ra.'
}

// Gọi API trả JSON; ném Error có thông báo dễ đọc khi thất bại.
export async function apiJson(path, { method = 'GET', body, params } = {}) {
  const query = params
    ? new URLSearchParams(Object.entries(params).filter(([, v]) => v !== '' && v != null)).toString()
    : ''
  let response
  try {
    response = await apiFetch(`${API_URL}${path}${query ? `?${query}` : ''}`, {
      method,
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : {},
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new Error('Không kết nối được máy chủ.')
  }
  if (response.status === 204) return null
  let data = null
  try { data = await response.json() } catch { data = null }
  if (!response.ok) throw new Error(errorText(data))
  return data
}