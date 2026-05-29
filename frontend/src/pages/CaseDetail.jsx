import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import {
  ChevronLeftIcon, CheckCircleIcon, XCircleIcon, ArrowPathIcon,
  ChevronDownIcon, ChevronUpIcon, EyeSlashIcon,
  ChevronLeftIcon as PagePrev, ChevronRightIcon as PageNext,
  DocumentMagnifyingGlassIcon,
} from '@heroicons/react/24/outline'
import { casesApi } from '../api/cases'
import { useAuth } from '../context/AuthContext'
import Badge from '../components/ui/Badge'
import ConfidenceBar from '../components/ui/ConfidenceBar'
import Spinner, { PageLoader } from '../components/ui/Spinner'

const REVIEW_ROLES = ['reviewer', 'senior_reviewer', 'administrator']
const RETRY_ROLES  = ['administrator', 'operations']

const CHANNEL_LABEL = {
  ms365_mail:    'M365 Mail',
  google_drive:  'Google Drive',
  vendor_portal: 'Vendor Portal',
  sftp:          'SFTP',
  rest_upload:   'REST Upload',
}

const MASKING_META = {
  TOKENISE:     { label: 'Tokenised',     cls: 'text-violet-600' },
  REDACT:       { label: 'Redacted',      cls: 'text-red-600'    },
  PSEUDONYMISE: { label: 'Pseudonymised', cls: 'text-amber-600'  },
}

const VISUAL_ICONS = {
  stamp:     '🔵',
  signature: '✍️',
  qr_code:   '📱',
  logo:      '🏷️',
  checkbox:  '☑️',
}

function formatTs(iso) {
  return new Date(iso).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

// ─── Reject modal ────────────────────────────────────────────────────────────

function RejectModal({ onClose, onConfirm }) {
  const [reason, setReason] = useState('')
  const [busy,   setBusy]   = useState(false)
  const valid = reason.trim().length >= 10

  async function submit() {
    if (!valid) return
    setBusy(true)
    try { await onConfirm(reason.trim()) } catch { setBusy(false) }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={() => !busy && onClose()}
    >
      <div className="mx-4 w-full max-w-md rounded-xl bg-white p-6 shadow-card-lg" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-sm font-semibold text-pwc-navy">Reject Case</h2>
        <p className="mt-1 text-xs text-pwc-gray-cool">
          Reason is recorded in the immutable audit trail (min. 10 characters).
        </p>
        <textarea
          autoFocus
          value={reason}
          onChange={(e) => setReason(e.target.value.slice(0, 500))}
          rows={4}
          placeholder="Enter rejection reason…"
          className="mt-3 w-full resize-none rounded-lg border border-pwc-surface-dark px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pwc-orange/40"
        />
        <p className="mt-1 text-right text-[11px] text-pwc-gray-cool">{reason.length}/500</p>
        <div className="mt-4 flex justify-end gap-2">
          <button
            onClick={onClose}
            disabled={busy}
            className="rounded-lg border border-pwc-surface-dark px-4 py-2 text-sm font-medium text-pwc-gray-cool hover:bg-pwc-surface disabled:opacity-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={submit}
            disabled={!valid || busy}
            className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
          >
            {busy && <Spinner size="sm" className="text-white" />}
            Confirm Reject
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Expandable field row ─────────────────────────────────────────────────────

function FieldRow({ field }) {
  const [expanded, setExpanded] = useState(false)
  const masking = MASKING_META[field.masking_mode]

  return (
    <>
      <tr className="hover:bg-pwc-surface/40 transition-colors">
        <td className="px-4 py-2.5">
          <p className="text-xs font-medium text-pwc-navy">{field.display_name}</p>
          <p className="text-[10px] font-mono text-pwc-gray-cool/60">{field.name}</p>
          {field.was_corrected && (
            <span className="mt-0.5 inline-block rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-medium text-amber-700 ring-1 ring-inset ring-amber-200">
              Corrected
            </span>
          )}
        </td>
        <td className="px-4 py-2.5">
          {masking ? (
            <span className={`flex items-center gap-1 text-xs font-mono ${masking.cls}`}>
              <EyeSlashIcon className="h-3.5 w-3.5 flex-shrink-0" />
              <span className="truncate max-w-[180px]">{field.value}</span>
              <span className="text-[10px] text-pwc-gray-cool">({masking.label})</span>
            </span>
          ) : (
            <span className="font-mono text-xs text-pwc-navy">{field.value}</span>
          )}
        </td>
        <td className="w-32 px-4 py-2.5"><ConfidenceBar score={field.calibrated_confidence} /></td>
        <td className="px-4 py-2.5"><Badge type="qa" value={field.qa_flag} /></td>
        <td className="px-4 py-2.5 text-xs text-pwc-gray-cool">p.{field.page_number}</td>
        <td className="px-4 py-2.5">
          <button
            onClick={() => setExpanded((v) => !v)}
            className="flex items-center gap-1 text-[11px] text-pwc-gray-cool hover:text-pwc-navy transition-colors"
          >
            Reasoning
            {expanded ? <ChevronUpIcon className="h-3 w-3" /> : <ChevronDownIcon className="h-3 w-3" />}
          </button>
        </td>
      </tr>
      {expanded && (
        <tr className="bg-pwc-surface">
          <td colSpan={6} className="px-4 pb-3 pt-1">
            <p className="text-xs italic leading-relaxed text-pwc-slate">{field.reasoning}</p>
          </td>
        </tr>
      )}
    </>
  )
}

// ─── Mock document renderer ───────────────────────────────────────────────────
// Used when caseData.document_url is null (dev/mock).
// In production, swap for <iframe src={caseData.document_url} className="w-full h-full" />.

function MockDocPage1({ caseData }) {
  const fv = Object.fromEntries((caseData.fields ?? []).filter((f) => f.page_number === 1).map((f) => [f.name, f.value]))
  const lineItems = caseData.line_items ?? []
  const subtotal = lineItems.reduce((s, l) => s + l.amount, 0)

  return (
    <div style={{ background: '#fff', padding: '32px', fontFamily: '"Georgia", serif', fontSize: '11.5px', lineHeight: '1.65', color: '#1B1F2A', minHeight: '100%' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: '16px', borderBottom: '2px solid #D04A02', marginBottom: '24px' }}>
        <div>
          <div style={{ fontSize: '15px', fontWeight: 'bold' }}>{fv.vendor_name ?? 'Vendor Name'}</div>
          <div style={{ fontSize: '10px', color: '#8892A4', marginTop: '3px' }}>GSTIN: {fv.vendor_tax_id ?? '—'}</div>
          <div style={{ fontSize: '10px', color: '#8892A4' }}>ap-invoices@acmecorp.in</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '20px', fontWeight: 'bold', letterSpacing: '3px', color: '#D04A02' }}>INVOICE</div>
          <div style={{ fontSize: '11px', color: '#3D4663', marginTop: '5px', lineHeight: '1.8' }}>
            <div>No: <strong>{fv.invoice_number ?? '—'}</strong></div>
            <div>Date: <strong>{fv.invoice_date ?? '—'}</strong></div>
          </div>
        </div>
      </div>

      {/* Bill to */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '9px', fontWeight: 'bold', letterSpacing: '1.5px', color: '#8892A4', marginBottom: '5px' }}>BILL TO</div>
        <div style={{ padding: '10px 12px', background: '#F4F5F7', borderRadius: '5px' }}>
          <div style={{ fontWeight: 'bold' }}>PwC Technology Consulting India LLP</div>
          <div style={{ color: '#8892A4', fontSize: '10.5px' }}>Accounts Payable · Golf View Corporate Tower II, Sector 42, Gurugram</div>
        </div>
      </div>

      {/* Line items table */}
      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '12px', fontSize: '10.5px' }}>
        <thead>
          <tr style={{ background: '#1B1F2A', color: 'white' }}>
            <th style={{ padding: '7px 8px', textAlign: 'left', fontWeight: '600', width: '32px' }}>#</th>
            <th style={{ padding: '7px 8px', textAlign: 'left', fontWeight: '600' }}>Description</th>
            <th style={{ padding: '7px 8px', textAlign: 'center', fontWeight: '600', width: '52px' }}>HSN</th>
            <th style={{ padding: '7px 8px', textAlign: 'right', fontWeight: '600', width: '60px' }}>Qty</th>
            <th style={{ padding: '7px 8px', textAlign: 'right', fontWeight: '600', width: '80px' }}>Unit Price</th>
            <th style={{ padding: '7px 8px', textAlign: 'right', fontWeight: '600', width: '72px' }}>Amount</th>
          </tr>
        </thead>
        <tbody>
          {lineItems.map((li, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #ECEEF2', background: i % 2 === 0 ? 'white' : '#F9FAFB' }}>
              <td style={{ padding: '7px 8px', color: '#8892A4' }}>{li.line_no}</td>
              <td style={{ padding: '7px 8px' }}>{li.description}</td>
              <td style={{ padding: '7px 8px', textAlign: 'center', color: '#8892A4' }}>{li.hsn_sac}</td>
              <td style={{ padding: '7px 8px', textAlign: 'right' }}>{li.quantity} {li.unit}</td>
              <td style={{ padding: '7px 8px', textAlign: 'right' }}>₹{li.unit_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
              <td style={{ padding: '7px 8px', textAlign: 'right', fontWeight: '500' }}>₹{li.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Subtotal note */}
      <div style={{ textAlign: 'right', fontSize: '10px', color: '#8892A4', marginBottom: '8px' }}>
        Sub-total: ₹{subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })} · continued on page 2 →
      </div>

      {/* Page watermark / seal */}
      <div style={{ marginTop: '40px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '16px' }}>
        <div style={{ width: '56px', height: '56px', borderRadius: '50%', border: '3px solid #1B1F2A', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.15, fontSize: '8px', textAlign: 'center', fontWeight: 'bold', color: '#1B1F2A', letterSpacing: '0.5px' }}>
          COMPANY<br />SEAL
        </div>
      </div>

      <div style={{ marginTop: '32px', fontSize: '9px', color: '#B8C0CC', borderTop: '1px solid #ECEEF2', paddingTop: '10px', display: 'flex', justifyContent: 'space-between' }}>
        <span>Page 1 of 2</span>
        <span>Acme Corp India Pvt Ltd · CIN: U74900DL2015PTC280123</span>
      </div>
    </div>
  )
}

function MockDocPage2({ caseData }) {
  const fv = Object.fromEntries((caseData.fields ?? []).filter((f) => f.page_number === 2).map((f) => [f.name, f.value]))

  return (
    <div style={{ background: '#fff', padding: '32px', fontFamily: '"Georgia", serif', fontSize: '11.5px', lineHeight: '1.65', color: '#1B1F2A', minHeight: '100%' }}>
      <div style={{ fontSize: '10px', color: '#8892A4', marginBottom: '20px', paddingBottom: '10px', borderBottom: '1px solid #ECEEF2' }}>
        {caseData.document_type.name} · {caseData.case_id} · continued
      </div>

      {/* Totals */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '28px' }}>
        <table style={{ width: '230px', fontSize: '11px', borderCollapse: 'collapse' }}>
          <tbody>
            <tr>
              <td style={{ padding: '5px 8px', color: '#8892A4' }}>Sub-total</td>
              <td style={{ textAlign: 'right', padding: '5px 8px' }}>₹11,200.00</td>
            </tr>
            <tr>
              <td style={{ padding: '5px 8px', color: '#8892A4' }}>GST @18% (IGST)</td>
              <td style={{ textAlign: 'right', padding: '5px 8px' }}>{fv.tax_amount ?? '₹1,250.00'}</td>
            </tr>
            <tr style={{ background: '#F4F5F7' }}>
              <td style={{ padding: '5px 8px', color: '#8892A4' }}>Discount</td>
              <td style={{ textAlign: 'right', padding: '5px 8px' }}>₹0.00</td>
            </tr>
            <tr style={{ borderTop: '2px solid #1B1F2A' }}>
              <td style={{ padding: '10px 8px 6px', fontWeight: 'bold', fontSize: '13px' }}>TOTAL DUE</td>
              <td style={{ textAlign: 'right', padding: '10px 8px 6px', fontWeight: 'bold', fontSize: '13px', color: '#D04A02' }}>
                {fv.total_amount ?? '₹12,450.00'}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Payment info */}
      <div style={{ padding: '12px 14px', background: '#F4F5F7', borderRadius: '5px', marginBottom: '20px', fontSize: '11px' }}>
        <div style={{ fontWeight: 'bold', marginBottom: '6px' }}>Payment Details</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px', color: '#3D4663' }}>
          <div><span style={{ color: '#8892A4' }}>Terms:</span> <strong>{fv.payment_terms ?? 'Net 30'}</strong></div>
          <div><span style={{ color: '#8892A4' }}>Bank:</span> HDFC Bank</div>
          <div><span style={{ color: '#8892A4' }}>A/C:</span> ••••••••5812</div>
          <div><span style={{ color: '#8892A4' }}>IFSC:</span> HDFC0001234</div>
        </div>
      </div>

      {/* Signature block */}
      <div style={{ marginTop: '60px', display: 'flex', justifyContent: 'flex-end' }}>
        <div style={{ textAlign: 'center', width: '160px' }}>
          <div style={{ height: '36px', borderBottom: '1.5px solid #1B1F2A', marginBottom: '5px' }} />
          <div style={{ fontSize: '10px', color: '#8892A4' }}>Authorised Signatory</div>
          <div style={{ fontSize: '10.5px', fontWeight: 'bold', marginTop: '2px' }}>Acme Corp India Pvt Ltd</div>
        </div>
      </div>

      <div style={{ marginTop: '28px', fontSize: '9px', color: '#B8C0CC', borderTop: '1px solid #ECEEF2', paddingTop: '10px', display: 'flex', justifyContent: 'space-between' }}>
        <span>Page 2 of 2</span>
        <span>E&OE. Subject to Gurugram jurisdiction.</span>
      </div>
    </div>
  )
}

function DocumentViewer({ caseData }) {
  const [page, setPage] = useState(1)
  const totalPages = caseData.extraction?.page_count ?? 2

  const pageMap = { 1: MockDocPage1, 2: MockDocPage2 }
  const PageComponent = pageMap[page] ?? MockDocPage1

  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Viewer toolbar */}
      <div className="flex flex-shrink-0 items-center gap-2 border-b border-pwc-surface-dark bg-white px-3 py-2">
        <DocumentMagnifyingGlassIcon className="h-4 w-4 flex-shrink-0 text-pwc-gray-cool" />
        <span className="min-w-0 flex-1 truncate font-mono text-xs text-pwc-navy">
          {caseData.case_id}.pdf
        </span>
        <div className="flex flex-shrink-0 items-center gap-1">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="rounded p-1 text-pwc-gray-cool hover:text-pwc-navy disabled:opacity-30 transition-colors"
            aria-label="Previous page"
          >
            <PagePrev className="h-3.5 w-3.5" />
          </button>
          <span className="w-14 text-center text-[11px] text-pwc-gray-cool">
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="rounded p-1 text-pwc-gray-cool hover:text-pwc-navy disabled:opacity-30 transition-colors"
            aria-label="Next page"
          >
            <PageNext className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Document area */}
      <div className="flex-1 overflow-y-auto bg-gray-200 p-3">
        {caseData.document_url ? (
          // Production: real PDF from Azure Blob
          <iframe
            src={caseData.document_url}
            className="h-full w-full rounded border-0"
            title="Document preview"
          />
        ) : (
          // Mock: rendered HTML document
          <div className="rounded-lg shadow-card-lg overflow-hidden">
            <PageComponent caseData={caseData} />
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function CaseDetail() {
  const { id }     = useParams()
  const { user }   = useAuth()
  const [caseData,   setCaseData]   = useState(null)
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)
  const [showReject, setShowReject] = useState(false)
  const [actionBusy, setActionBusy] = useState(false)
  const [showDoc,    setShowDoc]    = useState(true)

  useEffect(() => {
    casesApi.getById(id)
      .then(setCaseData)
      .catch((e) => setError(e.message ?? 'Case not found'))
      .finally(() => setLoading(false))
  }, [id])

  async function handleApprove() {
    setActionBusy(true)
    try {
      await casesApi.approve(id)
      setCaseData((prev) => ({ ...prev, status: 'AUTO_APPROVED' }))
      toast.success('Case approved')
    } catch {
      toast.error('Failed to approve — please try again')
    } finally {
      setActionBusy(false)
    }
  }

  async function handleReject(reason) {
    await casesApi.reject(id, reason)
    setCaseData((prev) => ({ ...prev, status: 'REJECTED' }))
    toast.success('Case rejected')
    setShowReject(false)
  }

  async function handleRetry() {
    setActionBusy(true)
    try {
      await casesApi.retry(id)
      setCaseData((prev) => ({ ...prev, status: 'PROCESSING' }))
      toast.info('Extraction re-queued')
    } catch {
      toast.error('Failed to retry — please try again')
    } finally {
      setActionBusy(false)
    }
  }

  if (loading) return <PageLoader />
  if (error) return (
    <div className="flex h-full min-h-[400px] items-center justify-center">
      <p className="text-sm text-red-600">{error}</p>
    </div>
  )
  if (!caseData) return null

  const canReview  = REVIEW_ROLES.includes(user?.role)
  const canRetry   = RETRY_ROLES.includes(user?.role)
  const isTerminal = ['AUTO_APPROVED', 'REJECTED', 'DUPLICATE'].includes(caseData.status)

  // Separate header fields vs line items
  const headerFields = caseData.fields ?? []
  const lineItems    = caseData.line_items ?? []

  // Build line-item column names from data keys (dynamic)
  const lineItemColumns = lineItems.length > 0
    ? Object.keys(lineItems[0]).filter((k) => k !== 'line_no')
    : []

  function colLabel(k) {
    const map = {
      description:  'Description',
      hsn_sac:      'HSN / SAC',
      quantity:     'Qty',
      unit:         'Unit',
      unit_price:   'Unit Price (₹)',
      tax_rate_pct: 'Tax %',
      amount:       'Amount (₹)',
    }
    return map[k] ?? k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
  }

  function fmtCell(k, v) {
    if (k === 'unit_price' || k === 'amount') return Number(v).toLocaleString('en-IN', { minimumFractionDigits: 2 })
    if (k === 'tax_rate_pct') return `${v}%`
    return String(v ?? '—')
  }

  return (
    <>
      {/* Split layout — height = viewport minus TopBar (h-14 = 56px) */}
      <div className="flex overflow-hidden" style={{ height: 'calc(100vh - 56px)' }}>

        {/* ── Left panel: extraction data ───────────────────────────────── */}
        <div className="min-w-0 flex-1 space-y-5 overflow-y-auto p-5">

          {/* Breadcrumb */}
          <nav className="flex items-center gap-1.5 text-xs" aria-label="Breadcrumb">
            <Link to="/cases" className="flex items-center gap-1 text-pwc-gray-cool hover:text-pwc-navy transition-colors">
              <ChevronLeftIcon className="h-3.5 w-3.5" />
              Cases
            </Link>
            <span className="text-pwc-gray-cool/40">/</span>
            <span className="font-mono text-pwc-navy">{id}</span>
          </nav>

          {/* Case header card */}
          <div className="rounded-xl border border-pwc-surface-dark bg-white p-4 shadow-card">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2.5">
                  <h2 className="font-mono text-sm font-bold text-pwc-navy">{caseData.case_id}</h2>
                  <Badge type="status" value={caseData.status} />
                </div>
                <dl className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-pwc-gray-cool">
                  <div><dt className="inline font-medium text-pwc-navy">Type: </dt><dd className="inline">{caseData.document_type.name} v{caseData.document_type.version}</dd></div>
                  <div><dt className="inline font-medium text-pwc-navy">Source: </dt><dd className="inline">{CHANNEL_LABEL[caseData.source_channel] ?? caseData.source_channel}</dd></div>
                  {caseData.source_identifier && <div><dt className="inline font-medium text-pwc-navy">From: </dt><dd className="inline">{caseData.source_identifier}</dd></div>}
                  <div><dt className="inline font-medium text-pwc-navy">Received: </dt><dd className="inline">{formatTs(caseData.received_at)}</dd></div>
                  {caseData.assigned_to && <div><dt className="inline font-medium text-pwc-navy">Assigned: </dt><dd className="inline">{caseData.assigned_to}</dd></div>}
                </dl>
              </div>

              {/* Action buttons */}
              <div className="flex flex-shrink-0 flex-wrap items-center gap-2">
                {/* Document panel toggle */}
                <button
                  onClick={() => setShowDoc((v) => !v)}
                  className="rounded-lg border border-pwc-surface-dark px-2.5 py-1.5 text-xs font-medium text-pwc-gray-cool hover:bg-pwc-surface transition-colors"
                  title={showDoc ? 'Hide document' : 'Show document'}
                >
                  {showDoc ? 'Hide Doc' : 'Show Doc'}
                </button>

                {canRetry && !isTerminal && (
                  <button
                    onClick={handleRetry}
                    disabled={actionBusy || caseData.status === 'PROCESSING'}
                    className="flex items-center gap-1.5 rounded-lg border border-pwc-surface-dark px-3 py-1.5 text-xs font-medium text-pwc-gray-cool hover:bg-pwc-surface disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                  >
                    <ArrowPathIcon className="h-3.5 w-3.5" />
                    Retry
                  </button>
                )}
                {canReview && !isTerminal && (
                  <>
                    <button
                      onClick={() => setShowReject(true)}
                      disabled={actionBusy}
                      className="flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                    >
                      <XCircleIcon className="h-3.5 w-3.5" />
                      Reject
                    </button>
                    <button
                      onClick={handleApprove}
                      disabled={actionBusy}
                      className="flex items-center gap-1.5 rounded-lg bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                    >
                      {actionBusy ? <Spinner size="sm" className="text-white" /> : <CheckCircleIcon className="h-3.5 w-3.5" />}
                      Approve
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* Extraction meta strip */}
            {caseData.extraction && (
              <dl className="mt-3 flex flex-wrap gap-x-5 gap-y-1 rounded-lg bg-pwc-surface px-4 py-2.5 text-xs text-pwc-gray-cool">
                <div><dt className="inline font-medium text-pwc-navy">Model: </dt><dd className="inline">{caseData.extraction.model_provider}/{caseData.extraction.model_name}</dd></div>
                <div><dt className="inline font-medium text-pwc-navy">Attempt: </dt><dd className="inline">#{caseData.extraction.attempt_number}</dd></div>
                <div><dt className="inline font-medium text-pwc-navy">Tokens: </dt><dd className="inline">{caseData.extraction.tokens_used?.toLocaleString()}</dd></div>
                <div><dt className="inline font-medium text-pwc-navy">Cost: </dt><dd className="inline">${caseData.extraction.cost_usd?.toFixed(4)}</dd></div>
                {caseData.extraction.duration_ms != null && <div><dt className="inline font-medium text-pwc-navy">Duration: </dt><dd className="inline">{(caseData.extraction.duration_ms / 1000).toFixed(1)}s</dd></div>}
                <div><dt className="inline font-medium text-pwc-navy">Confidence: </dt><dd className="inline font-semibold text-pwc-navy">{((caseData.aggregate_confidence ?? 0) * 100).toFixed(0)}%</dd></div>
              </dl>
            )}
          </div>

          {/* ── Header fields table ───────────────────────────────────── */}
          {headerFields.length > 0 && (
            <div className="overflow-hidden rounded-xl border border-pwc-surface-dark bg-white shadow-card">
              <div className="border-b border-pwc-surface-dark bg-pwc-surface px-5 py-2.5">
                <p className="text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">
                  Header Fields
                  <span className="ml-2 font-normal normal-case">({headerFields.length} fields extracted)</span>
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-pwc-surface-dark text-left">
                      <th className="px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Field</th>
                      <th className="px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Extracted Value</th>
                      <th className="w-32 px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Confidence</th>
                      <th className="px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">QA</th>
                      <th className="px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Pg</th>
                      <th className="px-4 py-2.5" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-pwc-surface-dark">
                    {headerFields.map((f) => <FieldRow key={f.field_id} field={f} />)}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ── Line items table ──────────────────────────────────────── */}
          {lineItems.length > 0 && (
            <div className="overflow-hidden rounded-xl border border-pwc-surface-dark bg-white shadow-card">
              <div className="border-b border-pwc-surface-dark bg-pwc-surface px-5 py-2.5">
                <p className="text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">
                  Line Items
                  <span className="ml-2 font-normal normal-case">({lineItems.length} rows)</span>
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-pwc-surface-dark bg-pwc-surface text-left">
                      <th className="px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">#</th>
                      {lineItemColumns.map((k) => (
                        <th key={k} className="px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool whitespace-nowrap">
                          {colLabel(k)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-pwc-surface-dark">
                    {lineItems.map((li, i) => (
                      <tr key={i} className="hover:bg-pwc-surface/50 transition-colors">
                        <td className="px-4 py-2.5 text-xs text-pwc-gray-cool tabular-nums">{li.line_no}</td>
                        {lineItemColumns.map((k) => (
                          <td
                            key={k}
                            className={`px-4 py-2.5 text-xs text-pwc-navy ${
                              k === 'amount' || k === 'unit_price' ? 'text-right tabular-nums font-medium' : ''
                            } ${k === 'tax_rate_pct' ? 'text-center tabular-nums' : ''}`}
                          >
                            {fmtCell(k, li[k])}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                  {/* Totals footer */}
                  <tfoot className="border-t-2 border-pwc-surface-dark bg-pwc-surface">
                    <tr>
                      <td
                        colSpan={lineItemColumns.indexOf('amount')}
                        className="px-4 py-2 text-xs font-semibold text-pwc-navy text-right"
                      >
                        Total
                      </td>
                      {lineItemColumns.map((k, idx) => {
                        if (idx < lineItemColumns.indexOf('amount')) return null
                        if (k === 'amount') return (
                          <td key={k} className="px-4 py-2 text-xs font-bold text-pwc-orange text-right tabular-nums">
                            ₹{lineItems.reduce((s, li) => s + li.amount, 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </td>
                        )
                        return <td key={k} />
                      })}
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          )}

          {/* ── Visual elements ───────────────────────────────────────── */}
          {caseData.visual_elements?.length > 0 && (
            <div className="rounded-xl border border-pwc-surface-dark bg-white p-4 shadow-card">
              <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">
                Visual Elements
                <span className="ml-2 font-normal normal-case">({caseData.visual_elements.length} detected)</span>
              </p>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                {caseData.visual_elements.map((el) => (
                  <div key={el.element_id} className="rounded-lg border border-pwc-surface-dark p-3">
                    <div className="flex items-center gap-2">
                      <span className="text-base" aria-hidden="true">{VISUAL_ICONS[el.element_class] ?? '🔍'}</span>
                      <div className="min-w-0">
                        <p className="truncate text-xs font-semibold capitalize text-pwc-navy">{el.element_class.replace(/_/g, ' ')}</p>
                        <p className="text-[11px] text-pwc-gray-cool">Page {el.page_number} · {(el.confidence * 100).toFixed(0)}%</p>
                      </div>
                    </div>
                    {el.attributes_json && (
                      <ul className="mt-2 space-y-0.5">
                        {Object.entries(el.attributes_json).map(([k, v]) => (
                          <li key={k} className="text-[11px] text-pwc-gray-cool">
                            <span className="capitalize font-medium">{k.replace(/_/g, ' ')}:</span> {String(v)}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Image pre-processing ─────────────────────────────────── */}
          {caseData.image_corrections?.length > 0 && (
            <div className="rounded-xl border border-pwc-surface-dark bg-white p-4 shadow-card">
              <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Image Pre-processing</p>
              <ol className="space-y-2">
                {caseData.image_corrections.map((step, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-pwc-orange/10 text-[10px] font-bold text-pwc-orange">
                      {i + 1}
                    </span>
                    <p className="text-xs text-pwc-navy">
                      <span className="font-semibold">{step.step}: </span>
                      <span className="text-pwc-gray-cool">{step.detail}</span>
                    </p>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* ── Audit trail ──────────────────────────────────────────── */}
          {caseData.audit_trail?.length > 0 && (
            <div className="rounded-xl border border-pwc-surface-dark bg-white p-4 shadow-card">
              <p className="mb-4 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Audit Trail</p>
              <ol className="relative ml-3 space-y-5 border-l border-pwc-surface-dark">
                {caseData.audit_trail.map((log) => (
                  <li key={log.log_id} className="pl-5">
                    <span className="absolute -left-1.5 mt-1 h-3 w-3 rounded-full border border-white bg-pwc-orange/30 ring-1 ring-pwc-orange/20" />
                    <p className="text-xs font-semibold capitalize text-pwc-navy">{log.action.replace(/_/g, ' ')}</p>
                    <p className="mt-0.5 text-[11px] text-pwc-gray-cool">{log.detail}</p>
                    <p className="mt-0.5 text-[11px] text-pwc-gray-cool/70">{log.actor} · {formatTs(log.timestamp)}</p>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>

        {/* ── Right panel: document viewer ─────────────────────────────── */}
        {showDoc && (
          <div className="hidden w-[460px] flex-shrink-0 border-l border-pwc-surface-dark xl:flex xl:flex-col overflow-hidden">
            <DocumentViewer caseData={caseData} />
          </div>
        )}
      </div>

      {showReject && (
        <RejectModal onClose={() => setShowReject(false)} onConfirm={handleReject} />
      )}
    </>
  )
}
