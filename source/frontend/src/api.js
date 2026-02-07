const JSON_HEADERS = {
  'Content-Type': 'application/json',
}

const API_BASE = import.meta.env.VITE_API_BASE || ''

async function handleResponse(response, defaultMessage) {
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || defaultMessage)
  }

  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    return null
  }

  return response.json()
}

export async function createJob(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/api/v1/jobs`, {
    method: 'POST',
    body: formData,
  })

  return handleResponse(response, '작업 생성에 실패했습니다.')
}

export async function getJob(jobId) {
  const response = await fetch(`${API_BASE}/api/v1/jobs/${jobId}`)
  return handleResponse(response, '작업 상태 조회에 실패했습니다.')
}

export async function getJobResult(jobId) {
  const response = await fetch(`${API_BASE}/api/v1/jobs/${jobId}/result`)
  return handleResponse(response, '분석 결과 조회에 실패했습니다.')
}

export async function updateDimensions(jobId, dimensions) {
  const response = await fetch(`${API_BASE}/api/v1/jobs/${jobId}/dimensions`, {
    method: 'PATCH',
    headers: JSON_HEADERS,
    body: JSON.stringify(dimensions),
  })

  return handleResponse(response, '치수 저장에 실패했습니다.')
}
