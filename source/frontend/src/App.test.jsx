import React from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, cleanup } from '@testing-library/react'
import { ResultPanel } from './App'

afterEach(() => {
  cleanup()
})

describe('ResultPanel', () => {
  const baseProps = {
    imageUrl: 'blob:preview',
    ocrItems: [
      { id: 'o1', key: 'width_text', value: '50 mm', bbox: { x: 10, y: 20, width: 30, height: 10 } },
      { id: 'o2', key: 'height_text', value: '100 mm', bbox: null },
    ],
    dimensionItems: [
      { id: 'd1', key: 'width', value: '50', unit: 'mm' },
      { id: 'd2', key: 'height', value: '100', unit: 'mm' },
    ],
    confirming: false,
    exportJson: null,
  }

  it('renders extracted dimension list', () => {
    render(<ResultPanel {...baseProps} onEdit={vi.fn()} onConfirm={vi.fn()} />)

    expect(screen.getByText('추출 치수')).toBeTruthy()
    expect(screen.getAllByTestId('dimension-row')).toHaveLength(2)
    expect(screen.getByLabelText('width value')).toBeTruthy()
    expect(screen.getByLabelText('height value')).toBeTruthy()
  })

  it('applies inline edit callback', () => {
    const onEdit = vi.fn()
    render(<ResultPanel {...baseProps} onEdit={onEdit} onConfirm={vi.fn()} />)

    fireEvent.change(screen.getByLabelText('width value'), { target: { value: '55.2' } })

    expect(onEdit).toHaveBeenCalledWith('d1', '55.2')
  })

  it('calls confirm and shows json preview when provided', () => {
    const onConfirm = vi.fn()
    const exportJson = {
      confirmed_dimensions: [
        { key: 'width', value: '55.2', unit: 'mm' },
        { key: 'height', value: '100', unit: 'mm' },
      ],
    }

    const { rerender } = render(
      <ResultPanel {...baseProps} onEdit={vi.fn()} onConfirm={onConfirm} exportJson={null} />,
    )

    fireEvent.click(screen.getByRole('button', { name: '치수 확정' }))
    expect(onConfirm).toHaveBeenCalledTimes(1)

    rerender(<ResultPanel {...baseProps} onEdit={vi.fn()} onConfirm={onConfirm} exportJson={exportJson} />)
    expect(screen.getByTestId('json-preview').textContent).toContain('confirmed_dimensions')
  })
})
