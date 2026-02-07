import React from 'react'
import { act } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import App, { AnalyzingStep, LandingStep } from './App'
import * as api from './api'

vi.mock('./api', () => ({
  createJob: vi.fn(),
  getJob: vi.fn(),
  getJobResult: vi.fn(),
  updateDimensions: vi.fn(),
}))

afterEach(() => {
  cleanup()
})

describe('App step components', () => {
  it('renders landing upload CTA', () => {
    render(<LandingStep onPick={() => {}} />)
    expect(screen.getByText('이미지 선택')).toBeTruthy()
    expect(screen.getByText('Cosmetic Packaging AI')).toBeTruthy()
  })

  it('renders analyzing step with job info', () => {
    render(<AnalyzingStep jobId="job-1" status="processing" />)
    expect(screen.getByText('분석 중')).toBeTruthy()
    expect(screen.getByText('작업 ID: job-1')).toBeTruthy()
  })
})

describe('App integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useRealTimers()
  })

  afterEach(() => {
    cleanup()
  })

  it('selects file, validates, and calls createJob when analysis starts', async () => {
    api.createJob.mockResolvedValue({ job_id: 'job-1', status: 'processing' })

    render(<App />)

    const file = new File(['image-bytes'], 'sample.png', { type: 'image/png' })
    fireEvent.change(screen.getByLabelText('이미지 선택'), { target: { files: [file] } })

    expect(screen.getByText('업로드 / 검증')).toBeTruthy()
    expect(screen.getByText('검증 결과: 업로드 가능한 파일입니다.')).toBeTruthy()

    fireEvent.click(screen.getByRole('button', { name: '분석 시작' }))

    await waitFor(() => {
      expect(api.createJob).toHaveBeenCalledWith(file)
      expect(screen.getByText('분석 중')).toBeTruthy()
      expect(screen.getByText('작업 ID: job-1')).toBeTruthy()
    })
  })

  it('polls with fake timer and moves to result on completion', async () => {
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
    api.createJob.mockResolvedValue({ job_id: 'job-2', status: 'processing' })
    api.getJob.mockResolvedValue({ status: 'done' })
    api.getJobResult.mockResolvedValue({ dimensions_mm: { width: 11, height: 22, depth: 33 } })

    render(<App />)

    const file = new File(['img'], 'pack.png', { type: 'image/png' })
    fireEvent.change(screen.getByLabelText('이미지 선택'), { target: { files: [file] } })
    fireEvent.click(screen.getByRole('button', { name: '분석 시작' }))

    await waitFor(() => expect(api.createJob).toHaveBeenCalled())
    expect(screen.getByText('분석 중')).toBeTruthy()

    await act(async () => {
      vi.advanceTimersByTime(2000)
      await Promise.resolve()
    })

    await waitFor(() => {
      expect(api.getJob).toHaveBeenCalledWith('job-2')
      expect(api.getJobResult).toHaveBeenCalledWith('job-2')
      expect(screen.getByText('분석 결과')).toBeTruthy()
    })
  })

  it('polls with fake timer and shows failure message', async () => {
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
    api.createJob.mockResolvedValue({ job_id: 'job-3', status: 'processing' })
    api.getJob.mockResolvedValue({ status: 'failed' })

    render(<App />)

    const file = new File(['img'], 'pack.png', { type: 'image/png' })
    fireEvent.change(screen.getByLabelText('이미지 선택'), { target: { files: [file] } })
    fireEvent.click(screen.getByRole('button', { name: '분석 시작' }))

    await waitFor(() => expect(api.createJob).toHaveBeenCalled())

    await act(async () => {
      vi.advanceTimersByTime(2000)
      await Promise.resolve()
    })

    await waitFor(() => {
      expect(screen.getByText('⚠ 분석 작업이 실패했습니다.')).toBeTruthy()
    })
  })

  it('cleans up polling timer on unmount', async () => {
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
    api.createJob.mockResolvedValue({ job_id: 'job-4', status: 'processing' })
    api.getJob.mockResolvedValue({ status: 'processing' })

    const { unmount } = render(<App />)

    const file = new File(['img'], 'pack.png', { type: 'image/png' })
    fireEvent.change(screen.getByLabelText('이미지 선택'), { target: { files: [file] } })
    fireEvent.click(screen.getByRole('button', { name: '분석 시작' }))

    await waitFor(() => expect(api.createJob).toHaveBeenCalled())
    expect(vi.getTimerCount()).toBe(1)

    unmount()
    expect(vi.getTimerCount()).toBe(0)
  })

  it('converts dimension payload to numbers and shows success message on save', async () => {
    api.createJob.mockResolvedValue({ job_id: 'job-5', status: 'processed' })
    api.getJobResult.mockResolvedValue({ dimensions_mm: { width: 10, height: 20, depth: 30 } })
    api.updateDimensions.mockResolvedValue({ dimensions_mm: { width: 101, height: 202, depth: 303 } })

    render(<App />)

    const file = new File(['img'], 'pack.png', { type: 'image/png' })
    fireEvent.change(screen.getByLabelText('이미지 선택'), { target: { files: [file] } })
    fireEvent.click(screen.getByRole('button', { name: '분석 시작' }))

    await waitFor(() => expect(screen.getByText('분석 결과')).toBeTruthy())

    const [widthInput, heightInput, depthInput] = screen.getAllByRole('spinbutton')
    fireEvent.change(widthInput, { target: { value: '12.5' } })
    fireEvent.change(heightInput, { target: { value: '45' } })
    fireEvent.change(depthInput, { target: { value: '7' } })

    fireEvent.click(screen.getByRole('button', { name: '치수 저장' }))

    await waitFor(() => {
      expect(api.updateDimensions).toHaveBeenCalledWith('job-5', {
        width: 12.5,
        height: 45,
        depth: 7,
      })
      expect(screen.getByText('✓ 치수 저장이 완료되었습니다.')).toBeTruthy()
    })
  })

  it('shows failure message when dimension save fails', async () => {
    api.createJob.mockResolvedValue({ job_id: 'job-6', status: 'processed' })
    api.getJobResult.mockResolvedValue({ dimensions_mm: { width: 10, height: 20, depth: 30 } })
    api.updateDimensions.mockRejectedValue(new Error('저장 실패'))

    render(<App />)

    const file = new File(['img'], 'pack.png', { type: 'image/png' })
    fireEvent.change(screen.getByLabelText('이미지 선택'), { target: { files: [file] } })
    fireEvent.click(screen.getByRole('button', { name: '분석 시작' }))

    await waitFor(() => expect(screen.getByText('분석 결과')).toBeTruthy())

    fireEvent.click(screen.getByRole('button', { name: '치수 저장' }))

    await waitFor(() => {
      expect(screen.getByText('⚠ 저장 실패')).toBeTruthy()
    })
  })
})
