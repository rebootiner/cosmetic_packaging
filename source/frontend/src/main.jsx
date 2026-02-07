import React from 'react'
import { createRoot } from 'react-dom/client'

function App() {
  return (
    <main style={{ fontFamily: 'sans-serif', padding: 24 }}>
      <h1>Cosmetic Packaging AI</h1>
      <p>Stage 1 bootstrap complete.</p>
    </main>
  )
}

createRoot(document.getElementById('root')).render(<App />)
