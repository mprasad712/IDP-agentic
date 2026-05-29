import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ResponsiveContainer,
} from 'recharts'
import {
  DocumentTextIcon, ClockIcon, CheckCircleIcon, ChartBarIcon,
} from '@heroicons/react/24/outline'
import { metricsApi } from '../api/metrics'
import StatCard from '../components/ui/StatCard'
import { PageLoader } from '../components/ui/Spinner'

function timeAgo(iso) {
  const diff = (Date.now() - new Date(iso)) / 1000
  if (diff < 60)   return `${Math.round(diff)}s ago`
  if (diff < 3600) return `${Math.round(diff / 60)}m ago`
  return `${Math.round(diff / 3600)}h ago`
}

function initials(name) {
  return name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
}

const ACTION_PILL = {
  'approved':           'bg-green-50 text-green-700',
  'auto-approved':      'bg-green-50 text-green-700',
  'rejected':           'bg-red-50   text-red-700',
  'corrected field':    'bg-amber-50 text-amber-700',
  'flagged for review': 'bg-amber-50 text-amber-700',
}

export default function Dashboard() {
  const [stats,    setStats]    = useState(null)
  const [overtime, setOvertime] = useState([])
  const [byStatus, setByStatus] = useState([])
  const [activity, setActivity] = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    Promise.all([
      metricsApi.dashboardStats(),
      metricsApi.casesOverTime(),
      metricsApi.casesByStatus(),
      metricsApi.recentActivity(),
    ]).then(([s, ot, bs, act]) => {
      setStats(s)
      setOvertime(ot.slice(-12))
      setByStatus(bs)
      setActivity(act)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <PageLoader />

  return (
    <div className="p-6 space-y-6">
      {/* Stats row */}
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        <StatCard
          label="Cases Today"
          value={stats?.cases_today ?? 0}
          delta={stats?.cases_today_delta}
          icon={DocumentTextIcon}
          accent
        />
        <StatCard
          label="Pending Review"
          value={stats?.pending_review ?? 0}
          delta={stats?.pending_review_delta}
          icon={ClockIcon}
        />
        <StatCard
          label="Auto-Approved"
          value={stats?.auto_approved ?? 0}
          subtext={`${stats?.auto_approved_pct ?? 0}% of today's cases`}
          icon={CheckCircleIcon}
        />
        <StatCard
          label="Avg Confidence"
          value={`${((stats?.avg_confidence ?? 0) * 100).toFixed(1)}%`}
          delta={stats?.avg_confidence_delta != null
            ? parseFloat((stats.avg_confidence_delta * 100).toFixed(1))
            : null}
          deltaLabel="pp"
          icon={ChartBarIcon}
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2 rounded-xl border border-pwc-surface-dark bg-white p-5 shadow-card">
          <p className="mb-4 text-sm font-semibold text-pwc-navy">Cases — Last 12 Hours</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={overtime} barCategoryGap="30%">
              <CartesianGrid strokeDasharray="3 3" stroke="#ECEEF2" vertical={false} />
              <XAxis dataKey="hour" tick={{ fontSize: 11, fill: '#8892A4' }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#8892A4' }} tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: '#ECEEF2', boxShadow: '0 4px 16px rgba(0,0,0,0.08)' }}
                cursor={{ fill: '#F4F5F7' }}
              />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
              <Bar dataKey="auto_approved" name="Auto-Approved" fill="#22c55e" radius={[3, 3, 0, 0]} stackId="a" />
              <Bar dataKey="needs_review"  name="Needs Review"  fill="#f59e0b" radius={[0, 0, 0, 0]} stackId="a" />
              <Bar dataKey="rejected"      name="Rejected"      fill="#ef4444" radius={[0, 0, 3, 3]} stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-xl border border-pwc-surface-dark bg-white p-5 shadow-card">
          <p className="mb-4 text-sm font-semibold text-pwc-navy">By Status — Today</p>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={byStatus}
                cx="50%"
                cy="45%"
                innerRadius={52}
                outerRadius={80}
                paddingAngle={3}
                dataKey="value"
              >
                {byStatus.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: '#ECEEF2', boxShadow: '0 4px 16px rgba(0,0,0,0.08)' }}
              />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent activity */}
      <div className="rounded-xl border border-pwc-surface-dark bg-white p-5 shadow-card">
        <p className="mb-4 text-sm font-semibold text-pwc-navy">Recent Activity</p>
        <ul className="divide-y divide-pwc-surface-dark">
          {activity.map((item) => (
            <li key={item.id} className="flex items-center gap-4 py-3">
              <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-pwc-surface-dark text-[11px] font-bold text-pwc-slate">
                {initials(item.actor)}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs text-pwc-navy leading-relaxed">
                  <span className="font-semibold">{item.actor}</span>{' '}
                  <span className={`inline-flex rounded px-1.5 py-0.5 text-[10px] font-medium ${ACTION_PILL[item.action] ?? 'bg-gray-100 text-gray-600'}`}>
                    {item.action}
                  </span>{' '}
                  <span className="font-mono text-[11px] text-pwc-gray-cool">{item.case_id}</span>
                </p>
                <p className="mt-0.5 text-[11px] text-pwc-gray-cool">{item.doc_type}</p>
              </div>
              <span className="flex-shrink-0 text-[11px] text-pwc-gray-cool whitespace-nowrap">
                {timeAgo(item.time)}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
