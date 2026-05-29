import { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import {
  ArrowUpTrayIcon, DocumentTextIcon, XMarkIcon,
  CheckCircleIcon, ArrowRightIcon,
} from '@heroicons/react/24/outline'
import { casesApi } from '../api/cases'
import Spinner from '../components/ui/Spinner'

const ACCEPTED_MIME = new Set([
  'application/pdf',
  'image/jpeg',
  'image/png',
  'image/tiff',
])
const ACCEPTED_EXT_RE = /\.(pdf|jpg|jpeg|png|tif|tiff)$/i
const MAX_MB     = 50
const MAX_BYTES  = MAX_MB * 1024 * 1024

function humanSize(bytes) {
  if (bytes < 1024)          return `${bytes} B`
  if (bytes < 1024 * 1024)   return `${(bytes / 1024).toFixed(1)} KB`
  return                           `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const CHANNEL_TIPS = [
  { label: 'M365 Mail',     icon: '✉️', desc: 'Auto-ingested from ap-invoices mailbox' },
  { label: 'Google Drive',  icon: '☁️', desc: 'Synced from monitored Drive folder' },
  { label: 'SFTP',          icon: '📁', desc: 'Polled from configured SFTP path' },
  { label: 'Vendor Portal', icon: '🏢', desc: 'Submitted by vendor via portal link' },
]

export default function Upload() {
  const navigate   = useNavigate()
  const inputRef   = useRef(null)
  const [file,     setFile]     = useState(null)
  const [fileErr,  setFileErr]  = useState(null)
  const [dragging, setDragging] = useState(false)
  const [busy,     setBusy]     = useState(false)
  const [result,   setResult]   = useState(null)

  function validateAndSet(f) {
    setFileErr(null)
    if (!f) return
    if (!ACCEPTED_MIME.has(f.type) && !ACCEPTED_EXT_RE.test(f.name)) {
      setFileErr('Unsupported file type. Please upload a PDF, JPG, PNG, or TIFF.')
      return
    }
    if (f.size > MAX_BYTES) {
      setFileErr(`File is too large (${humanSize(f.size)}). Maximum size is ${MAX_MB} MB.`)
      return
    }
    setFile(f)
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    validateAndSet(e.dataTransfer.files?.[0])
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const onDragOver  = useCallback((e) => { e.preventDefault(); setDragging(true)  }, [])
  const onDragLeave = useCallback(()  => setDragging(false), [])

  async function handleSubmit() {
    if (!file || busy) return
    setBusy(true)
    try {
      const res = await casesApi.upload(file)
      setResult(res)
      toast.success('Document submitted for processing')
    } catch {
      toast.error('Upload failed — please try again')
      setBusy(false)
    }
  }

  // ── Success state ───────────────────────────────────────────────────────────
  if (result) {
    return (
      <div className="flex h-full min-h-[480px] items-center justify-center p-8">
        <div className="w-full max-w-sm text-center">
          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <CheckCircleIcon className="h-8 w-8 text-green-600" />
          </div>
          <h2 className="text-base font-semibold text-pwc-navy">Document Submitted</h2>
          <p className="mt-2 text-xs text-pwc-gray-cool leading-relaxed">
            Your document has been queued for extraction. Average processing time is 8–15 seconds.
          </p>
          <div className="mt-4 rounded-lg bg-pwc-surface px-4 py-3">
            <p className="text-[11px] text-pwc-gray-cool">Case ID</p>
            <p className="mt-0.5 font-mono text-sm font-semibold text-pwc-navy">{result.case_id}</p>
          </div>
          <div className="mt-6 flex justify-center gap-3">
            <button
              onClick={() => navigate(`/cases/${result.case_id}`)}
              className="flex items-center gap-2 rounded-lg bg-pwc-orange px-4 py-2 text-xs font-medium text-white hover:bg-pwc-orange-dark transition-colors"
            >
              View Case
              <ArrowRightIcon className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => { setFile(null); setResult(null) }}
              className="rounded-lg border border-pwc-surface-dark px-4 py-2 text-xs font-medium text-pwc-gray-cool hover:bg-pwc-surface transition-colors"
            >
              Upload Another
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ── Upload form ─────────────────────────────────────────────────────────────
  return (
    <div className="mx-auto max-w-2xl space-y-6 p-6">
      <div>
        <h2 className="text-sm font-semibold text-pwc-navy">Upload Document</h2>
        <p className="mt-1 text-xs text-pwc-gray-cool">
          Submit a document manually for automated classification and extraction. Supported: PDF, JPG, PNG, TIFF — up to {MAX_MB} MB.
        </p>
      </div>

      {/* ── Drop zone or selected file ─────────────────────────────────── */}
      {!file ? (
        <div
          role="button"
          tabIndex={0}
          aria-label="Drop zone — click or drag to upload"
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
          className={`flex min-h-[220px] cursor-pointer flex-col items-center justify-center gap-4 rounded-xl border-2 border-dashed p-8 text-center transition-colors outline-none focus-visible:ring-2 focus-visible:ring-pwc-orange/50 ${
            dragging
              ? 'border-pwc-orange bg-pwc-orange/5'
              : 'border-pwc-surface-dark bg-white hover:border-pwc-orange/40 hover:bg-pwc-surface'
          }`}
        >
          <div className={`flex h-14 w-14 items-center justify-center rounded-full transition-colors ${
            dragging ? 'bg-pwc-orange/10' : 'bg-pwc-surface-dark'
          }`}>
            <ArrowUpTrayIcon className={`h-7 w-7 transition-colors ${dragging ? 'text-pwc-orange' : 'text-pwc-gray-cool'}`} />
          </div>
          <div>
            <p className="text-sm font-semibold text-pwc-navy">
              {dragging ? 'Drop to upload' : 'Drag & drop or click to select'}
            </p>
            <p className="mt-1 text-xs text-pwc-gray-cool">
              PDF · JPG · PNG · TIFF &nbsp;·&nbsp; max {MAX_MB} MB
            </p>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.tif,.tiff"
            className="sr-only"
            onChange={(e) => validateAndSet(e.target.files?.[0])}
            aria-hidden="true"
          />
        </div>
      ) : (
        <div className="rounded-xl border border-pwc-surface-dark bg-white p-4 shadow-card">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-pwc-orange/10">
              <DocumentTextIcon className="h-5 w-5 text-pwc-orange" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-pwc-navy">{file.name}</p>
              <p className="text-[11px] text-pwc-gray-cool">
                {humanSize(file.size)} · {file.type || 'document'}
              </p>
            </div>
            <button
              onClick={() => { setFile(null); setFileErr(null) }}
              aria-label="Remove selected file"
              className="flex-shrink-0 rounded p-1.5 text-pwc-gray-cool hover:bg-pwc-surface hover:text-red-600 transition-colors"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Error */}
      {fileErr && (
        <p className="rounded-lg bg-red-50 px-4 py-2.5 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-200">
          {fileErr}
        </p>
      )}

      {/* Submit */}
      {file && !fileErr && (
        <button
          onClick={handleSubmit}
          disabled={busy}
          className="flex items-center gap-2 rounded-lg bg-pwc-orange px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-pwc-orange-dark disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
        >
          {busy ? (
            <>
              <Spinner size="sm" className="text-white" />
              Processing…
            </>
          ) : (
            <>
              <ArrowUpTrayIcon className="h-4 w-4" />
              Submit for Extraction
            </>
          )}
        </button>
      )}

      {/* Other channels info */}
      <div>
        <p className="mb-3 text-xs font-semibold text-pwc-navy">
          Other Intake Channels
          <span className="ml-2 font-normal text-pwc-gray-cool">(configured by administrator)</span>
        </p>
        <div className="grid grid-cols-2 gap-3">
          {CHANNEL_TIPS.map((ch) => (
            <div
              key={ch.label}
              className="flex items-start gap-3 rounded-lg border border-pwc-surface-dark bg-white p-3 shadow-card"
            >
              <span className="text-xl flex-shrink-0" aria-hidden="true">{ch.icon}</span>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-pwc-navy">{ch.label}</p>
                <p className="mt-0.5 text-[11px] text-pwc-gray-cool leading-relaxed">{ch.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
