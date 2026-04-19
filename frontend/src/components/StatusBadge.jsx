export default function StatusBadge({ status }) {
  const styles = {
    idle: 'bg-brutal-white',
    running: 'bg-brutal-yellow animate-pulse',
    success: 'bg-brutal-mint',
    error: 'bg-brutal-coral',
  }

  const labels = {
    idle: '⏸ Idle',
    running: '⚡ Running...',
    success: '✓ Complete',
    error: '✗ Error',
  }

  return (
    <span className={`tag-brutal ${styles[status] || styles.idle}`}>
      {labels[status] || status}
    </span>
  )
}