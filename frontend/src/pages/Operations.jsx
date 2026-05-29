import { useState, useEffect } from 'react'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, Cell,
} from 'recharts'
import {
  BoltIcon, ClockIcon, CurrencyDollarIcon, ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import { metricsApi } from '../api/metrics'
import StatCard from '../components/ui/StatCard'
import { PageLoader } from '../components/ui/Spinner'

const TOOLTIP_STYLE = {
  fontSize: 12,
  borderRadius: 8,
  borderColor: '#ECEEF2',
  boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
}

export default function Operations() {
  const [opsStats, setOpsStats] = useState(null)
  const [latency,  setLatency]  = useState([])
  const [llmCost,  setLLMCost]  = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    Promise.all([
      metricsApi.opsStats(),
      metricsApi.latency(),
      metricsApi.llmCost(),
    ]).then(([ops, lat, cost]) => {
      setOpsStats(ops)
      setLatency(lat)
      setLLMCost(cost)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <PageLoader />

  const totalToday = llmCost.reduce((s, p) => s + p.today, 0)
  const totalWeek  = llmCost.reduce((s, p) => s + p.week,  0)

  return (
    <div className="p-6 space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        <StatCard
          label="Throughput / hr"
          value={opsStats?.throughput_per_hour ?? 0}
          delta={opsStats?.throughput_delta}
          icon={BoltIcon}
          accent
        />
        <StatCard
          label="P95 Latency"
          value={`${opsStats?.p95_latency_s ?? 0}s`}
          delta={opsStats?.latency_delta}
          deltaLabel="s"
          icon={ClockIcon}
        />
        <StatCard
          label="LLM Cost Today"
          value={`$${(opsStats?.llm_cost_today ?? 0).toFixed(2)}`}
          delta={opsStats?.cost_delta}
          deltaLabel="$"
          icon={CurrencyDollarIcon}
        />
        <StatCard
          label="Error Rate"
          value={`${opsStats?.error_rate_pct ?? 0}%`}
          delta={opsStats?.error_delta}
          deltaLabel="%"
          icon={ExclamationTriangleIcon}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {/* Latency */}
        <div className="rounded-xl border border-pwc-surface-dark bg-white p-5 shadow-card">
          <p className="mb-4 text-sm font-semibold text-pwc-navy">Extraction Latency — 7 Days</p>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={latency}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ECEEF2" vertical={false} />
              <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#8892A4' }} tickLine={false} axisLine={false} />
              <YAxis unit="s" tick={{ fontSize: 11, fill: '#8892A4' }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v) => [`${v}s`]} />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
              <Line type="monotone" dataKey="p50" name="P50" stroke="#22c55e" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="p95" name="P95" stroke="#f59e0b" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="p99" name="P99" stroke="#ef4444" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* LLM cost by provider */}
        <div className="rounded-xl border border-pwc-surface-dark bg-white p-5 shadow-card">
          <p className="mb-4 text-sm font-semibold text-pwc-navy">LLM Cost by Provider — Today</p>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={llmCost} layout="vertical" barCategoryGap="35%">
              <CartesianGrid strokeDasharray="3 3" stroke="#ECEEF2" horizontal={false} />
              <XAxis
                type="number"
                unit="$"
                tick={{ fontSize: 11, fill: '#8892A4' }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                type="category"
                dataKey="provider"
                tick={{ fontSize: 11, fill: '#8892A4' }}
                tickLine={false}
                width={115}
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(v) => [`$${v.toFixed(2)}`]}
              />
              <Bar dataKey="today" name="Today ($)" radius={[0, 3, 3, 0]}>
                {llmCost.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Provider cost breakdown table */}
      <div className="rounded-xl border border-pwc-surface-dark bg-white p-5 shadow-card">
        <p className="mb-4 text-sm font-semibold text-pwc-navy">Provider Cost Breakdown</p>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-pwc-surface-dark text-left">
              <th className="pb-2.5 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Provider</th>
              <th className="pb-2.5 text-right text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Today</th>
              <th className="pb-2.5 text-right text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">This Week</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-pwc-surface-dark">
            {llmCost.map((p) => (
              <tr key={p.provider} className="hover:bg-pwc-surface/50 transition-colors">
                <td className="py-3">
                  <div className="flex items-center gap-2">
                    <span
                      className="h-2.5 w-2.5 flex-shrink-0 rounded-full"
                      style={{ backgroundColor: p.color }}
                    />
                    <span className="text-xs font-medium text-pwc-navy">{p.provider}</span>
                  </div>
                </td>
                <td className="py-3 text-right text-xs tabular-nums text-pwc-navy">${p.today.toFixed(2)}</td>
                <td className="py-3 text-right text-xs tabular-nums text-pwc-navy">${p.week.toFixed(2)}</td>
              </tr>
            ))}
            <tr className="border-t-2 border-pwc-surface-dark font-semibold">
              <td className="pt-3 text-xs text-pwc-navy">Total</td>
              <td className="pt-3 text-right text-xs tabular-nums text-pwc-navy">${totalToday.toFixed(2)}</td>
              <td className="pt-3 text-right text-xs tabular-nums text-pwc-navy">${totalWeek.toFixed(2)}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
