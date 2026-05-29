import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  MagnifyingGlassIcon, FunnelIcon,
  ChevronLeftIcon, ChevronRightIcon, DocumentTextIcon,
} from '@heroicons/react/24/outline'
import { casesApi } from '../api/cases'
import Badge from '../components/ui/Badge'
import ConfidenceBar from '../components/ui/ConfidenceBar'
import EmptyState from '../components/ui/EmptyState'
import { PageLoader } from '../components/ui/Spinner'

const ALL_STATUSES = ['NEEDS_REVIEW', 'AUTO_APPROVED', 'PENDING', 'PROCESSING', 'REJECTED', 'DUPLICATE']
const DOC_TYPES    = ['Invoice', 'Bank Statement', 'Passport', 'Purchase Order', 'Salary Slip', 'Driving Licence', 'Lab Report']

const CHANNEL_LABEL = {
  ms365_mail:    'M365 Mail',
  google_drive:  'Google Drive',
  vendor_portal: 'Vendor Portal',
  sftp:          'SFTP',
  rest_upload:   'REST Upload',
}

function timeAgo(iso) {
  const diff = (Date.now() - new Date(iso)) / 1000
  if (diff < 60)    return `${Math.round(diff)}s ago`
  if (diff < 3600)  return `${Math.round(diff / 60)}m ago`
  if (diff < 86400) return `${Math.round(diff / 3600)}h ago`
  return `${Math.round(diff / 86400)}d ago`
}

export default function CasesList() {
  const [data,     setData]     = useState({ data: [], total: 0, totalPages: 1 })
  const [loading,  setLoading]  = useState(true)
  const [page,     setPage]     = useState(1)
  const [search,   setSearch]   = useState('')
  const [statuses, setStatuses] = useState([])
  const [docType,  setDocType]  = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    casesApi.list({ status: statuses, docType, search, page })
      .then((r) => { if (!cancelled) setData(r) })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [search, statuses, docType, page]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleSearch(v) {
    setSearch(v)
    if (page !== 1) setPage(1)
  }

  function handleDocType(v) {
    setDocType(v)
    if (page !== 1) setPage(1)
  }

  function toggleStatus(s) {
    setStatuses((prev) => prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s])
    if (page !== 1) setPage(1)
  }

  return (
    <div className="p-6 space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative min-w-[200px] max-w-xs flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-pwc-gray-cool pointer-events-none" />
          <input
            type="search"
            placeholder="Search case ID or doc type…"
            value={search}
            onChange={(e) => handleSearch(e.target.value.slice(0, 100))}
            className="w-full rounded-lg border border-pwc-surface-dark bg-white py-2 pl-9 pr-3 text-sm placeholder:text-pwc-gray-cool focus:outline-none focus:ring-2 focus:ring-pwc-orange/40"
          />
        </div>

        <select
          value={docType}
          onChange={(e) => handleDocType(e.target.value)}
          className="rounded-lg border border-pwc-surface-dark bg-white px-3 py-2 text-sm text-pwc-navy focus:outline-none focus:ring-2 focus:ring-pwc-orange/40"
        >
          <option value="">All Document Types</option>
          {DOC_TYPES.map((d) => <option key={d} value={d}>{d}</option>)}
        </select>

        <div className="flex flex-wrap items-center gap-1 rounded-lg border border-pwc-surface-dark bg-white px-2 py-1.5">
          <FunnelIcon className="h-3.5 w-3.5 text-pwc-gray-cool" />
          {ALL_STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => toggleStatus(s)}
              className={`rounded-full px-2 py-0.5 text-[11px] font-medium transition-colors ${
                statuses.includes(s)
                  ? 'bg-pwc-orange text-white'
                  : 'text-pwc-gray-cool hover:text-pwc-navy'
              }`}
            >
              {s.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-xl border border-pwc-surface-dark bg-white shadow-card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-pwc-surface-dark bg-pwc-surface text-left">
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Case ID</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Document Type</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Status</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Channel</th>
                <th className="w-36 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Confidence</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Received</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Assigned</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-pwc-surface-dark">
              {loading ? (
                <tr><td colSpan={8} className="py-16"><PageLoader /></td></tr>
              ) : data.data.length === 0 ? (
                <tr>
                  <td colSpan={8}>
                    <EmptyState
                      icon={DocumentTextIcon}
                      title="No cases found"
                      description="Try adjusting your filters or search term."
                    />
                  </td>
                </tr>
              ) : data.data.map((c) => (
                <tr key={c.case_id} className="hover:bg-pwc-surface/50 transition-colors">
                  <td className="px-4 py-3">
                    <span className="font-mono text-xs text-pwc-navy">{c.case_id.replace('case_', '')}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs font-medium text-pwc-navy">{c.document_type.name}</span>
                    <span className="ml-1.5 text-[10px] text-pwc-gray-cool">v{c.document_type.version}</span>
                  </td>
                  <td className="px-4 py-3"><Badge type="status" value={c.status} /></td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-pwc-gray-cool">
                      {CHANNEL_LABEL[c.source_channel] ?? c.source_channel}
                    </span>
                  </td>
                  <td className="w-36 px-4 py-3">
                    <ConfidenceBar score={c.aggregate_confidence} />
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-xs text-pwc-gray-cool">
                    {timeAgo(c.received_at)}
                  </td>
                  <td className="px-4 py-3 text-xs text-pwc-gray-cool">
                    {c.assigned_to ?? <span className="text-pwc-surface-dark">—</span>}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      to={`/cases/${c.case_id}`}
                      className="text-xs font-medium text-pwc-orange hover:text-pwc-orange-dark transition-colors"
                    >
                      Review →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {!loading && data.total > 0 && (
          <div className="flex items-center justify-between border-t border-pwc-surface-dark px-4 py-3">
            <span className="text-xs text-pwc-gray-cool">
              {data.total} case{data.total !== 1 ? 's' : ''} · Page {page} of {data.totalPages}
            </span>
            <div className="flex items-center gap-1">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="rounded p-1 text-pwc-gray-cool hover:bg-pwc-surface disabled:cursor-not-allowed disabled:opacity-40 transition-colors"
              >
                <ChevronLeftIcon className="h-4 w-4" />
              </button>
              <button
                disabled={page >= data.totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="rounded p-1 text-pwc-gray-cool hover:bg-pwc-surface disabled:cursor-not-allowed disabled:opacity-40 transition-colors"
              >
                <ChevronRightIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
