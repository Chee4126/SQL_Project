import { useCallback, useEffect, useState } from 'react'
import { apiJson } from '../api'

export default function StudentSelect({
  label,
  value,
  onChange,
  includeAll = false,
  disabled = false,
}) {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadStudents = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      setStudents(await apiJson('/students'))
    } catch (requestError) {
      setError(requestError.message)
      setStudents([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadStudents()
  }, [loadStudents])

  return (
    <label>
      {label}
      <select
        required={!includeAll}
        value={value}
        onChange={onChange}
        disabled={disabled || loading || Boolean(error)}
      >
        <option value="">
          {loading
            ? 'Đang tải sinh viên...'
            : error
              ? 'Không tải được danh sách sinh viên'
              : includeAll
                ? 'Tất cả sinh viên'
                : students.length
                  ? 'Chọn sinh viên'
                  : 'Chưa có sinh viên'}
        </option>
        {students.map((student) => (
          <option key={student.student_id} value={student.student_id}>
            {student.student_id} — {student.name}
          </option>
        ))}
      </select>
      {error && (
        <small className="field-hint">
          {error}{' '}
          <button type="button" className="table-action" onClick={loadStudents}>
            Tải lại
          </button>
        </small>
      )}
    </label>
  )
}
