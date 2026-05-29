import { useState, useEffect } from 'react'
import { toast } from 'react-toastify'
import { PlusIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline'
import { adminApi } from '../../api/admin'
import Badge from '../../components/ui/Badge'
import Spinner, { PageLoader } from '../../components/ui/Spinner'
import EmptyState from '../../components/ui/EmptyState'

const CATEGORIES = [
  'Financial — AP/AR',
  'Financial — Banking',
  'KYC & Identity',
  'Legal & Contracts',
  'HR & Payroll',
  'Healthcare',
  'Other',
]

const CONFIDENTIALITY_LEVELS = ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED']

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

function CreateModal({ onClose, onCreate }) {
  const [form, setForm] = useState({ name: '', category: '', confidentiality: 'INTERNAL' })
  const [busy, setBusy] = useState(false)
  const valid = form.name.trim().length >= 2 && form.category.length > 0

  function update(k, v) { setForm((f) => ({ ...f, [k]: v })) }

  async function submit(e) {
    e.preventDefault()
    if (!valid) return
    setBusy(true)
    try {
      const created = await adminApi.createDocumentType({
        name:            form.name.trim(),
        category:        form.category,
        confidentiality: form.confidentiality,
      })
      onCreate(created)
      toast.success(`"${created.name}" created`)
      onClose()
    } catch {
      toast.error('Failed to create document type')
      setBusy(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="mx-4 w-full max-w-md rounded-xl bg-white p-6 shadow-card-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-sm font-semibold text-pwc-navy">New Document Type</h2>
        <form onSubmit={submit} className="mt-4 space-y-3" noValidate>
          <div>
            <label htmlFor="dt-name" className="mb-1 block text-xs font-medium text-pwc-navy">
              Name <span className="text-red-500" aria-hidden="true">*</span>
            </label>
            <input
              id="dt-name"
              type="text"
              value={form.name}
              onChange={(e) => update('name', e.target.value.slice(0, 80))}
              placeholder="e.g. Trade Finance LC"
              className="w-full rounded-lg border border-pwc-surface-dark px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pwc-orange/40"
              required
            />
          </div>
          <div>
            <label htmlFor="dt-category" className="mb-1 block text-xs font-medium text-pwc-navy">
              Category <span className="text-red-500" aria-hidden="true">*</span>
            </label>
            <select
              id="dt-category"
              value={form.category}
              onChange={(e) => update('category', e.target.value)}
              className="w-full rounded-lg border border-pwc-surface-dark bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pwc-orange/40"
              required
            >
              <option value="">Select category…</option>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="dt-conf" className="mb-1 block text-xs font-medium text-pwc-navy">
              Confidentiality
            </label>
            <select
              id="dt-conf"
              value={form.confidentiality}
              onChange={(e) => update('confidentiality', e.target.value)}
              className="w-full rounded-lg border border-pwc-surface-dark bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pwc-orange/40"
            >
              {CONFIDENTIALITY_LEVELS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="mt-5 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-pwc-surface-dark px-4 py-2 text-sm font-medium text-pwc-gray-cool hover:bg-pwc-surface transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!valid || busy}
              className="flex items-center gap-2 rounded-lg bg-pwc-orange px-4 py-2 text-sm font-medium text-white hover:bg-pwc-orange-dark disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
            >
              {busy && <Spinner size="sm" className="text-white" />}
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function AdminDocumentTypes() {
  const [items,       setItems]       = useState([])
  const [loading,     setLoading]     = useState(true)
  const [showCreate,  setShowCreate]  = useState(false)
  const [publishingId, setPublishingId] = useState(null)

  useEffect(() => {
    adminApi.listDocumentTypes().then(setItems).finally(() => setLoading(false))
  }, [])

  async function handlePublish(id) {
    setPublishingId(id)
    try {
      const updated = await adminApi.publishDocumentType(id)
      setItems((prev) => prev.map((d) => d.doc_type_id === id ? { ...d, ...updated } : d))
      toast.success('Document type published')
    } catch {
      toast.error('Failed to publish')
    } finally {
      setPublishingId(null)
    }
  }

  if (loading) return <PageLoader />

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs text-pwc-gray-cool">
          {items.length} document type{items.length !== 1 ? 's' : ''}
        </p>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 rounded-lg bg-pwc-orange px-3 py-1.5 text-xs font-medium text-white hover:bg-pwc-orange-dark transition-colors"
        >
          <PlusIcon className="h-3.5 w-3.5" />
          New Document Type
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-pwc-surface-dark bg-white shadow-card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-pwc-surface-dark bg-pwc-surface text-left">
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Name</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Category</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Confidentiality</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Status</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Fields</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Published</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">By</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-pwc-surface-dark">
              {items.length === 0 ? (
                <tr>
                  <td colSpan={8}>
                    <EmptyState
                      icon={DocumentDuplicateIcon}
                      title="No document types"
                      description="Create your first document type to begin classifying documents."
                    />
                  </td>
                </tr>
              ) : items.map((d) => (
                <tr key={d.doc_type_id} className="hover:bg-pwc-surface/50 transition-colors">
                  <td className="px-4 py-3">
                    <span className="text-xs font-semibold text-pwc-navy">{d.name}</span>
                    <span className="ml-1.5 text-[10px] text-pwc-gray-cool">v{d.version}</span>
                  </td>
                  <td className="px-4 py-3 text-xs text-pwc-gray-cool">{d.category}</td>
                  <td className="px-4 py-3"><Badge type="confidentiality" value={d.confidentiality} /></td>
                  <td className="px-4 py-3"><Badge type="docStatus" value={d.status} /></td>
                  <td className="px-4 py-3 text-xs text-pwc-navy tabular-nums">{d.fields_count}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-xs text-pwc-gray-cool">{formatDate(d.published_at)}</td>
                  <td className="px-4 py-3 text-xs text-pwc-gray-cool">{d.published_by ?? '—'}</td>
                  <td className="px-4 py-3 text-right">
                    {d.status === 'DRAFT' && (
                      <button
                        onClick={() => handlePublish(d.doc_type_id)}
                        disabled={publishingId === d.doc_type_id}
                        className="ml-auto flex items-center gap-1.5 rounded-lg bg-green-600 px-3 py-1 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
                      >
                        {publishingId === d.doc_type_id
                          ? <Spinner size="sm" className="text-white" />
                          : null}
                        Publish
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showCreate && (
        <CreateModal
          onClose={() => setShowCreate(false)}
          onCreate={(item) => setItems((prev) => [item, ...prev])}
        />
      )}
    </div>
  )
}
