import React from 'react'
import { describe, expect, it } from 'vitest'
import { renderToStaticMarkup } from 'react-dom/server'
import { AnalyzingStep, LandingStep } from './App'

describe('App step components', () => {
  it('renders landing upload CTA', () => {
    const html = renderToStaticMarkup(<LandingStep onPick={() => {}} />)
    expect(html).toContain('이미지 선택')
    expect(html).toContain('Cosmetic Packaging AI')
  })

  it('renders analyzing step with job info', () => {
    const html = renderToStaticMarkup(<AnalyzingStep jobId="job-1" status="processing" />)
    expect(html).toContain('분석 중')
    expect(html).toContain('job-1')
  })
})
