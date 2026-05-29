import clsx from 'clsx'
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/20/solid'

export default function StatCard({ label, value, subtext, delta, deltaLabel, icon: Icon, accent = false }) {
  const isPositive = delta > 0
  const isNeutral  = delta === 0 || delta == null

  return (
    <div className={clsx(
      'relative overflow-hidden rounded-xl border bg-white p-5 shadow-card',
      accent ? 'border-pwc-orange/30' : 'border-pwc-surface-dark'
    )}>
      {accent && <div className="absolute inset-x-0 top-0 h-0.5 bg-pwc-orange rounded-t-xl" />}

      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="text-xs font-medium text-pwc-gray-cool uppercase tracking-wide truncate">{label}</p>
          <p className="mt-2 text-2xl font-bold text-pwc-navy leading-none">{value}</p>
          {subtext && <p className="mt-1 text-xs text-pwc-gray-cool">{subtext}</p>}
        </div>
        {Icon && (
          <div className={clsx(
            'flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg',
            accent ? 'bg-pwc-orange/10' : 'bg-pwc-surface-dark'
          )}>
            <Icon className={clsx('h-5 w-5', accent ? 'text-pwc-orange' : 'text-pwc-gray-cool')} />
          </div>
        )}
      </div>

      {!isNeutral && (
        <div className={clsx(
          'mt-3 flex items-center gap-1 text-xs font-medium',
          isPositive ? 'text-green-600' : 'text-red-600'
        )}>
          {isPositive
            ? <ArrowUpIcon className="h-3.5 w-3.5" />
            : <ArrowDownIcon className="h-3.5 w-3.5" />
          }
          <span>{Math.abs(delta)}{deltaLabel ?? ''} vs yesterday</span>
        </div>
      )}
    </div>
  )
}
