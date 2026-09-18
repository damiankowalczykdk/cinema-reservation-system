import { useState } from 'react'

function ResultBlock({ error, result }) {
  if (error) return <p className="error">{error}</p>
  if (result === undefined) return null
  return <pre>{JSON.stringify(result, null, 2)}</pre>
}

function Section({ title, method, children, variant }) {
  return (
    <section className={variant ? `panel panel--${variant}` : 'panel'}>
      <h3>
        {title}
        {method && <span className={`method method--${method.toLowerCase()}`}>{method}</span>}
      </h3>
      {children}
    </section>
  )
}

function useAction(fn) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(undefined)

  async function run(...args) {
    setLoading(true)
    setError(null)
    try {
      const data = await fn(...args)
      setResult(data)
    } catch (err) {
      setError(err.message)
      setResult(undefined)
    } finally {
      setLoading(false)
    }
  }

  return { run, loading, error, result }
}

function Field({ field, value, onChange, required }) {
  const { name, label, type, options } = field
  if (type === 'select') {
    return (
      <div className="field">
        <label>{label}</label>
        <select value={value} onChange={(e) => onChange(name, e.target.value)} required={required}>
          <option value="" disabled>
            select…
          </option>
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>
    )
  }
  return (
    <div className="field">
      <label>{label}</label>
      <input
        type={type === 'decimal' ? 'number' : type}
        step={type === 'decimal' ? '0.01' : undefined}
        value={value}
        onChange={(e) => onChange(name, e.target.value)}
        required={required}
      />
    </div>
  )
}

export { ResultBlock, Section, useAction, Field }
