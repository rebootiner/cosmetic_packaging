import React, { useEffect, useMemo, useState } from 'react'
import { createJob, getJob, getJobResult, updateDimensions } from './api'

const STEP = {
  LANDING: 1,
  VALIDATE: 2,
  ANALYZING: 3,
  RESULT: 4,
}

const POLL_MS = 2000

function extractDimensions(payload) {
  if (!payload) return { width: '', height: '', depth: '' }
  const source = payload.dimensions_mm || payload.data?.dimensions_mm || payload.result?.dimensions_mm || payload
  return {
    width: source.width ?? '',
    height: source.height ?? '',
    depth: source.depth ?? '',
  }
}

export function LandingStep({ onPick }) {
  return (
    <section className="card">
      <h1>Cosmetic Packaging AI</h1>
      <p>패키지 이미지를 업로드하고 자동 치수 분석을 시작하세요.</p>
      <label className="file-picker">
        이미지 선택
        <input type="file" accept="image/*" onChange={onPick} />
      </label>
    </section>
  )
}

export function AnalyzingStep({ jobId, status }) {
  return (
    <section className="card">
      <h2>분석 중</h2>
      <div className="spinner" aria-label="loading" />
      <p>작업 ID: {jobId}</p>
      <p>현재 상태: {status || 'processing'}</p>
    </section>
  )
}

export default function App() {
  const [step, setStep] = useState(STEP.LANDING)
  const [file, setFile] = useState(null)
  const [jobId, setJobId] = useState('')
  const [jobStatus, setJobStatus] = useState('')
  const [result, setResult] = useState(null)
  const [dimensions, setDimensions] = useState({ width: '', height: '', depth: '' })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [warning, setWarning] = useState('')
  const [savedMessage, setSavedMessage] = useState('')

  const validation = useMemo(() => {
    if (!file) return { valid: false, message: '이미지 파일을 선택해 주세요.' }
    if (!file.type.startsWith('image/')) return { valid: false, message: '이미지 파일만 업로드할 수 있습니다.' }
    if (file.size > 10 * 1024 * 1024) return { valid: false, message: '파일 크기는 10MB 이하여야 합니다.' }
    return { valid: true, message: '업로드 가능한 파일입니다.' }
  }, [file])

  const onFilePick = (event) => {
    const selected = event.target.files?.[0]
    setSavedMessage('')
    setError('')
    if (!selected) return

    setFile(selected)
    setWarning(selected.size > 5 * 1024 * 1024 ? '파일 크기가 커서 분석 시간이 길어질 수 있습니다.' : '')
    setStep(STEP.VALIDATE)
  }

  const startAnalysis = async () => {
    if (!validation.valid || !file) return
    setLoading(true)
    setError('')
    setSavedMessage('')

    try {
      const payload = await createJob(file)
      const id = payload?.job_id || payload?.id || payload?.jobId || payload?.data?.job_id || payload?.data?.id
      if (!id) throw new Error('작업 ID를 받지 못했습니다.')

      const status = (payload?.status || 'processing').toLowerCase()
      setJobId(String(id))
      setJobStatus(status)

      if (status === 'processed') {
        await fetchResult(String(id))
      } else {
        setStep(STEP.ANALYZING)
      }
    } catch (e) {
      setError(e.message || '분석 시작에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const fetchResult = async (id) => {
    const data = await getJobResult(id)
    const parsed = extractDimensions(data)
    setResult(data)
    setDimensions(parsed)
    setStep(STEP.RESULT)
  }

  useEffect(() => {
    if (step !== STEP.ANALYZING || !jobId) return undefined

    let cancelled = false
    const timer = setInterval(async () => {
      try {
        const statusPayload = await getJob(jobId)
        const status = (statusPayload?.status || statusPayload?.data?.status || '').toLowerCase()
        if (cancelled) return

        setJobStatus(status || 'processing')

        if (status === 'done' || status === 'completed' || status === 'success' || status === 'processed') {
          clearInterval(timer)
          await fetchResult(jobId)
        }

        if (status === 'failed' || status === 'error') {
          clearInterval(timer)
          setError('분석 작업이 실패했습니다.')
        }
      } catch (e) {
        clearInterval(timer)
        if (!cancelled) setError(e.message || '작업 상태 조회 중 오류가 발생했습니다.')
      }
    }, POLL_MS)

    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [step, jobId])

  const onDimensionChange = (key, value) => {
    setSavedMessage('')
    setDimensions((prev) => ({ ...prev, [key]: value }))
  }

  const saveDimensions = async () => {
    if (!jobId) return
    setSaving(true)
    setError('')
    try {
      const payload = await updateDimensions(jobId, {
        width: Number(dimensions.width),
        height: Number(dimensions.height),
        depth: Number(dimensions.depth),
      })
      const latest = extractDimensions(payload)
      setDimensions(latest)
      setSavedMessage('치수 저장이 완료되었습니다.')
    } catch (e) {
      setError(e.message || '치수 저장 중 오류가 발생했습니다.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <main className="page">
      {error && <p className="message error">⚠ {error}</p>}
      {warning && <p className="message warning">⚠ {warning}</p>}
      {savedMessage && <p className="message success">✓ {savedMessage}</p>}

      {step === STEP.LANDING && <LandingStep onPick={onFilePick} />}

      {step === STEP.VALIDATE && (
        <section className="card">
          <h2>업로드 / 검증</h2>
          <p>파일명: {file?.name}</p>
          <p>검증 결과: {validation.message}</p>
          <div className="actions">
            <button type="button" onClick={() => setStep(STEP.LANDING)}>
              다시 선택
            </button>
            <button type="button" onClick={startAnalysis} disabled={!validation.valid || loading}>
              {loading ? '분석 시작 중...' : '분석 시작'}
            </button>
          </div>
        </section>
      )}

      {step === STEP.ANALYZING && <AnalyzingStep jobId={jobId} status={jobStatus} />}

      {step === STEP.RESULT && (
        <section className="card">
          <h2>분석 결과</h2>
          <p>작업 ID: {jobId}</p>
          <p className="hint">아래 치수를 수정한 뒤 저장할 수 있습니다.</p>

          <div className="grid">
            <label>
              Width (mm)
              <input
                type="number"
                value={dimensions.width}
                onChange={(e) => onDimensionChange('width', e.target.value)}
              />
            </label>
            <label>
              Height (mm)
              <input
                type="number"
                value={dimensions.height}
                onChange={(e) => onDimensionChange('height', e.target.value)}
              />
            </label>
            <label>
              Depth (mm)
              <input
                type="number"
                value={dimensions.depth}
                onChange={(e) => onDimensionChange('depth', e.target.value)}
              />
            </label>
          </div>

          <div className="actions">
            <button type="button" onClick={saveDimensions} disabled={saving}>
              {saving ? '저장 중...' : '치수 저장'}
            </button>
            <button type="button" onClick={() => setStep(STEP.LANDING)}>
              새 작업 시작
            </button>
          </div>

          {result && (
            <details>
              <summary>원본 응답 보기</summary>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </details>
          )}
        </section>
      )}
    </main>
  )
}
