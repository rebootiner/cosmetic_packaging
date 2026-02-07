import React, { useMemo, useState } from 'react'
import { extractOcr, mapDimensions } from './api'

const STEP = {
  LANDING: 1,
  VALIDATE: 2,
  ANALYZING: 3,
  RESULT: 4,
}

function normalizeBbox(item) {
  const bbox = item?.bbox || item?.box || item?.bounding_box || item?.boundingBox
  if (!bbox) return null

  if (Array.isArray(bbox) && bbox.length === 4) {
    const [x, y, width, height] = bbox
    return { x: Number(x) || 0, y: Number(y) || 0, width: Number(width) || 0, height: Number(height) || 0 }
  }

  if (Array.isArray(bbox) && bbox.length >= 2) {
    const xs = bbox.map((p) => Number(p?.x ?? p?.[0] ?? 0))
    const ys = bbox.map((p) => Number(p?.y ?? p?.[1] ?? 0))
    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)
    const minY = Math.min(...ys)
    const maxY = Math.max(...ys)
    return { x: minX, y: minY, width: maxX - minX, height: maxY - minY }
  }

  if (typeof bbox === 'object') {
    const x = Number(bbox.x ?? bbox.left ?? 0)
    const y = Number(bbox.y ?? bbox.top ?? 0)
    const width = Number(bbox.width ?? (bbox.right != null ? Number(bbox.right) - x : 0))
    const height = Number(bbox.height ?? (bbox.bottom != null ? Number(bbox.bottom) - y : 0))
    return { x, y, width, height }
  }

  return null
}

function normalizeOcrItems(payload) {
  const candidates = payload?.items || payload?.results || payload?.ocr || payload?.data?.items || payload?.data?.ocr || []
  if (!Array.isArray(candidates)) return []

  return candidates.map((item, index) => ({
    id: item?.id || `ocr-${index}`,
    key: item?.key || item?.label || item?.name || `item-${index + 1}`,
    text: item?.text || item?.value || '',
    value: item?.value ?? item?.text ?? '',
    bbox: normalizeBbox(item),
    confidence: item?.confidence,
  }))
}

function normalizeDimensionItems(payload) {
  const mapped = payload?.dimensions || payload?.data?.dimensions || payload?.mapped_dimensions || []
  if (Array.isArray(mapped) && mapped.length) {
    return mapped.map((item, index) => ({
      id: item?.id || `dim-${index}`,
      key: item?.key || item?.name || item?.label || `dimension-${index + 1}`,
      value: item?.value ?? '',
      unit: item?.unit || 'mm',
      sourceText: item?.source_text || item?.text || '',
      bbox: normalizeBbox(item),
    }))
  }

  const dims = payload?.dimensions_mm || payload?.data?.dimensions_mm || payload?.result?.dimensions_mm
  if (dims && typeof dims === 'object') {
    return Object.entries(dims).map(([key, value]) => ({
      id: key,
      key,
      value: value ?? '',
      unit: 'mm',
      sourceText: '',
      bbox: null,
    }))
  }

  return []
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

function OcrOverlay({ imageUrl, items }) {
  const hasBbox = items.some((item) => item.bbox)

  return (
    <div>
      <div className="preview-frame">
        <img src={imageUrl} alt="업로드 원본 미리보기" className="preview-image" />
        {hasBbox && (
          <div className="overlay-layer" data-testid="overlay-layer">
            {items.map((item) =>
              item.bbox ? (
                <div
                  key={item.id}
                  className="bbox"
                  title={`${item.key}: ${item.value}`}
                  style={{
                    left: `${item.bbox.x}%`,
                    top: `${item.bbox.y}%`,
                    width: `${item.bbox.width}%`,
                    height: `${item.bbox.height}%`,
                  }}
                >
                  <span>{item.key}</span>
                </div>
              ) : null,
            )}
          </div>
        )}
      </div>

      {!hasBbox && (
        <p className="hint" data-testid="no-bbox-hint">
          bbox 정보가 없어 리스트만 표시합니다.
        </p>
      )}
    </div>
  )
}

export function ResultPanel({ imageUrl, ocrItems, dimensionItems, onEdit, onConfirm, confirming, exportJson }) {
  return (
    <section className="card">
      <h2>분석 결과</h2>
      <p className="hint">원본 이미지와 OCR 결과를 확인하고 치수를 수동 보정하세요.</p>

      <OcrOverlay imageUrl={imageUrl} items={ocrItems} />

      <div className="list-panel">
        <h3>추출 치수</h3>
        <ul>
          {dimensionItems.map((item) => (
            <li key={item.id} className="list-row" data-testid="dimension-row">
              <strong>{item.key}</strong>
              <input
                aria-label={`${item.key} value`}
                value={item.value}
                onChange={(e) => onEdit(item.id, e.target.value)}
              />
              <span>{item.unit}</span>
            </li>
          ))}
        </ul>

        {dimensionItems.length === 0 && <p className="hint">추출된 치수가 없습니다.</p>}

        <div className="actions">
          <button type="button" onClick={onConfirm} disabled={confirming || dimensionItems.length === 0}>
            {confirming ? '확정 중...' : '치수 확정'}
          </button>
        </div>
      </div>

      {exportJson && (
        <details open>
          <summary>JSON export 미리보기</summary>
          <pre data-testid="json-preview">{JSON.stringify(exportJson, null, 2)}</pre>
        </details>
      )}
    </section>
  )
}

export default function App() {
  const [step, setStep] = useState(STEP.LANDING)
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [ocrItems, setOcrItems] = useState([])
  const [dimensionItems, setDimensionItems] = useState([])
  const [rawResult, setRawResult] = useState(null)
  const [exportJson, setExportJson] = useState(null)
  const [loading, setLoading] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [error, setError] = useState('')
  const [statusMessage, setStatusMessage] = useState('')

  const validation = useMemo(() => {
    if (!file) return { valid: false, message: '이미지 파일을 선택해 주세요.' }
    if (!file.type.startsWith('image/')) return { valid: false, message: '이미지 파일만 업로드할 수 있습니다.' }
    if (file.size > 10 * 1024 * 1024) return { valid: false, message: '파일 크기는 10MB 이하여야 합니다.' }
    return { valid: true, message: '업로드 가능한 파일입니다.' }
  }, [file])

  const onFilePick = (event) => {
    const selected = event.target.files?.[0]
    setError('')
    setStatusMessage('')
    setExportJson(null)
    setRawResult(null)
    if (!selected) return

    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(URL.createObjectURL(selected))
    setFile(selected)
    setStep(STEP.VALIDATE)
  }

  const startAnalysis = async () => {
    if (!validation.valid || !file) return
    setLoading(true)
    setStep(STEP.ANALYZING)
    setError('')
    setStatusMessage('OCR 추출 요청 중...')

    try {
      const ocrPayload = await extractOcr(file)
      const parsedOcr = normalizeOcrItems(ocrPayload)
      setOcrItems(parsedOcr)

      setStatusMessage('치수 매핑 요청 중...')
      const mapPayload = await mapDimensions({ ocr: parsedOcr, raw: ocrPayload })
      const parsedDimensions = normalizeDimensionItems(mapPayload)
      setDimensionItems(parsedDimensions)
      setRawResult({ ocrPayload, mapPayload })

      setStatusMessage('분석 완료')
      setStep(STEP.RESULT)
    } catch (e) {
      setError(e.message || '분석 중 오류가 발생했습니다.')
      setStep(STEP.VALIDATE)
    } finally {
      setLoading(false)
    }
  }

  const onEditDimension = (id, value) => {
    setExportJson(null)
    setDimensionItems((prev) => prev.map((item) => (item.id === id ? { ...item, value } : item)))
  }

  const onConfirm = async () => {
    setConfirming(true)
    setError('')
    try {
      const payload = {
        confirmed_dimensions: dimensionItems.map((item) => ({
          key: item.key,
          value: item.value,
          unit: item.unit,
        })),
      }
      setExportJson(payload)
      setStatusMessage('치수 확정 완료')
    } catch (e) {
      setError(e.message || '치수 확정 중 오류가 발생했습니다.')
    } finally {
      setConfirming(false)
    }
  }

  return (
    <main className="page">
      {error && <p className="message error">⚠ {error}</p>}
      {statusMessage && <p className="message success">{statusMessage}</p>}

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

      {step === STEP.ANALYZING && (
        <section className="card">
          <h2>분석 중</h2>
          <div className="spinner" aria-label="loading" />
          <p>{statusMessage || '요청 처리 중...'}</p>
        </section>
      )}

      {step === STEP.RESULT && (
        <ResultPanel
          imageUrl={previewUrl}
          ocrItems={ocrItems}
          dimensionItems={dimensionItems}
          onEdit={onEditDimension}
          onConfirm={onConfirm}
          confirming={confirming}
          exportJson={exportJson}
        />
      )}

      {rawResult && step === STEP.RESULT && (
        <details>
          <summary>원본 응답 보기</summary>
          <pre>{JSON.stringify(rawResult, null, 2)}</pre>
        </details>
      )}
    </main>
  )
}
