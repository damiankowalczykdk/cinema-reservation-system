import { useState } from 'react'
import { Section, ResultBlock, useAction, Field } from './ui.jsx'

function castValue(field, raw) {
  if (field.type === 'number') return raw === '' ? undefined : Number(raw)
  return raw // text, decimal (kept as string, exact), select, date, datetime-local
}

function emptyForm(fields) {
  return Object.fromEntries(fields.map((f) => [f.name, '']))
}

function buildPayload(fields, form) {
  return Object.fromEntries(fields.map((f) => [f.name, castValue(f, form[f.name])]))
}

// Only send fields the user actually filled in — PATCH omits untouched keys
// so the gateway leaves them unchanged, rather than overwriting with ''.
function buildUpdatePayload(fields, form) {
  return Object.fromEntries(
    fields
      .map((f) => [f, typeof form[f.name] === 'string' ? form[f.name].trim() : form[f.name]])
      .filter(([, v]) => v !== '')
      .map(([f, v]) => [f.name, castValue(f, v)])
  )
}

function CreateSection({ resource, fields, create }) {
  const [form, setForm] = useState(emptyForm(fields))
  const { run, loading, error, result } = useAction(create)

  function handleSubmit(e) {
    e.preventDefault()
    run(buildPayload(fields, form))
  }

  return (
    <Section title={`Create ${resource}`} method="POST">
      <form onSubmit={handleSubmit}>
        {fields.map((f) => (
          <Field key={f.name} field={f} value={form[f.name]} onChange={(name, v) => setForm({ ...form, [name]: v })} required />
        ))}
        <button type="submit" disabled={loading}>
          Create
        </button>
      </form>
      <ResultBlock error={error} result={result} />
    </Section>
  )
}

function GetByIdSection({ resource, getById }) {
  const [id, setId] = useState('')
  const { run, loading, error, result } = useAction(getById)

  function handleSubmit(e) {
    e.preventDefault()
    run(id)
  }

  return (
    <Section title={`Get ${resource} by ID`} method="GET">
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>ID</label>
          <input value={id} onChange={(e) => setId(e.target.value)} required />
        </div>
        <button type="submit" disabled={loading}>
          Get
        </button>
      </form>
      <ResultBlock error={error} result={result} />
    </Section>
  )
}

function SearchSection({ resource, fields, search }) {
  const [form, setForm] = useState(emptyForm(fields))
  const { run, loading, error, result } = useAction(search)

  function handleSubmit(e) {
    e.preventDefault()
    run(...fields.map((f) => castValue(f, form[f.name])))
  }

  return (
    <Section title={`Search ${resource}`} method="GET">
      <form onSubmit={handleSubmit}>
        {fields.map((f) => (
          <Field key={f.name} field={f} value={form[f.name]} onChange={(name, v) => setForm({ ...form, [name]: v })} required />
        ))}
        <button type="submit" disabled={loading}>
          Search
        </button>
      </form>
      <ResultBlock error={error} result={result} />
    </Section>
  )
}

function UpdateSection({ resource, fields, update }) {
  const [id, setId] = useState('')
  const [form, setForm] = useState(emptyForm(fields))
  const { run, loading, error, result } = useAction(update)

  function handleSubmit(e) {
    e.preventDefault()
    run(id, buildUpdatePayload(fields, form))
  }

  return (
    <Section title={`Update ${resource}`} method="PATCH">
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>ID</label>
          <input value={id} onChange={(e) => setId(e.target.value)} required />
        </div>
        {fields.map((f) => (
          <Field
            key={f.name}
            field={{ ...f, label: `${f.label} (optional)` }}
            value={form[f.name]}
            onChange={(name, v) => setForm({ ...form, [name]: v })}
          />
        ))}
        <button type="submit" disabled={loading}>
          Update
        </button>
      </form>
      <ResultBlock error={error} result={result} />
    </Section>
  )
}

function DeleteSection({ resource, remove }) {
  const [id, setId] = useState('')
  const { run, loading, error, result } = useAction(async (entityId) => {
    await remove(entityId)
    return { deleted: entityId }
  })

  function handleSubmit(e) {
    e.preventDefault()
    if (!window.confirm(`Delete ${resource.toLowerCase()} #${id}? This cannot be undone.`)) return
    run(id)
  }

  return (
    <Section title={`Delete ${resource}`} method="DELETE" variant="danger">
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>ID</label>
          <input value={id} onChange={(e) => setId(e.target.value)} required />
        </div>
        <button type="submit" className="btn-danger" disabled={loading}>
          Delete
        </button>
      </form>
      <ResultBlock error={error} result={result} />
    </Section>
  )
}

// Config-driven CRUD dashboard page for one gateway entity — Cinema/Hall/Movie/Screening
// all follow the same create/get/search/update/delete shape, only the fields differ.
function EntityCrud({ resource, note, fields, searchFields, api }) {
  return (
    <div>
      <h2>{resource}s</h2>
      {note && <p className="note">{note}</p>}
      <div className="grid">
        <CreateSection resource={resource} fields={fields} create={api.create} />
        <GetByIdSection resource={resource} getById={api.getById} />
        {api.search && <SearchSection resource={resource} fields={searchFields} search={api.search} />}
        <UpdateSection resource={resource} fields={fields} update={api.update} />
        <DeleteSection resource={resource} remove={api.remove} />
      </div>
    </div>
  )
}

export default EntityCrud
