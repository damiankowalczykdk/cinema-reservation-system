import { Section, ResultBlock, useAction } from './ui.jsx'
import { getHealth } from './api.js'
import AuthPanel from './AuthPanel.jsx'

function HealthSection() {
  const { run, loading, error, result } = useAction(getHealth)
  return (
    <Section title="Gateway Health" method="GET">
      <button onClick={() => run()} disabled={loading}>
        Check health
      </button>
      <ResultBlock error={error} result={result} />
    </Section>
  )
}

function Overview() {
  return (
    <div>
      <h2>Overview</h2>
      <p className="note">Quick status check — pick an entity from the sidebar to exercise its endpoints.</p>
      <div className="grid">
        <HealthSection />
        <AuthPanel />
      </div>
    </div>
  )
}

export default Overview
