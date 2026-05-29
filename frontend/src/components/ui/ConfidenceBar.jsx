import clsx from 'clsx'

function level(score) {
  if (score >= 0.9)  return { label: `${Math.round(score * 100)}%`, color: 'bg-green-500',  text: 'text-green-700' }
  if (score >= 0.75) return { label: `${Math.round(score * 100)}%`, color: 'bg-amber-400',  text: 'text-amber-700' }
  return               { label: `${Math.round(score * 100)}%`, color: 'bg-red-400',    text: 'text-red-700'   }
}

export default function ConfidenceBar({ score, showLabel = true, className }) {
  if (score == null) return <span className="text-xs text-pwc-gray-cool">—</span>
  const { label, color, text } = level(score)
  return (
    <div className={clsx('flex items-center gap-2', className)}>
      <div className="flex-1 h-1.5 rounded-full bg-pwc-surface-dark overflow-hidden">
        <div className={clsx('h-full rounded-full transition-all', color)} style={{ width: `${score * 100}%` }} />
      </div>
      {showLabel && <span className={clsx('text-xs font-semibold tabular-nums w-9 text-right', text)}>{label}</span>}
    </div>
  )
}
