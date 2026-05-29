import { useState, useEffect } from 'react'
import { toast } from 'react-toastify'
import { UserPlusIcon } from '@heroicons/react/24/outline'
import { adminApi } from '../../api/admin'
import { useAuth } from '../../context/AuthContext'
import Badge from '../../components/ui/Badge'
import Spinner, { PageLoader } from '../../components/ui/Spinner'

const ROLES = ['reviewer', 'senior_reviewer', 'administrator', 'compliance_officer', 'operations', 'vendor_user']

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function timeAgo(iso) {
  if (!iso) return 'Never'
  const diff = (Date.now() - new Date(iso)) / 1000
  if (diff < 60)    return `${Math.round(diff)}s ago`
  if (diff < 3600)  return `${Math.round(diff / 60)}m ago`
  if (diff < 86400) return `${Math.round(diff / 3600)}h ago`
  return `${Math.round(diff / 86400)}d ago`
}

function InviteModal({ onClose, onInvite }) {
  const [form, setForm] = useState({ email: '', display_name: '', role: 'reviewer' })
  const [busy, setBusy] = useState(false)
  const valid = EMAIL_RE.test(form.email) && form.display_name.trim().length >= 2

  function update(k, v) { setForm((f) => ({ ...f, [k]: v })) }

  async function submit(e) {
    e.preventDefault()
    if (!valid) return
    setBusy(true)
    try {
      const user = await adminApi.inviteUser({
        email:        form.email.trim().toLowerCase(),
        display_name: form.display_name.trim(),
        role:         form.role,
      })
      onInvite(user)
      toast.success(`Invitation sent to ${form.email}`)
      onClose()
    } catch {
      toast.error('Failed to send invitation')
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
        <h2 className="text-sm font-semibold text-pwc-navy">Invite User</h2>
        <form onSubmit={submit} className="mt-4 space-y-3" noValidate>
          <div>
            <label htmlFor="inv-email" className="mb-1 block text-xs font-medium text-pwc-navy">
              Email <span className="text-red-500" aria-hidden="true">*</span>
            </label>
            <input
              id="inv-email"
              type="email"
              autoComplete="off"
              value={form.email}
              onChange={(e) => update('email', e.target.value.slice(0, 254))}
              placeholder="user@pwc.com"
              className="w-full rounded-lg border border-pwc-surface-dark px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pwc-orange/40"
              required
            />
          </div>
          <div>
            <label htmlFor="inv-name" className="mb-1 block text-xs font-medium text-pwc-navy">
              Display Name <span className="text-red-500" aria-hidden="true">*</span>
            </label>
            <input
              id="inv-name"
              type="text"
              value={form.display_name}
              onChange={(e) => update('display_name', e.target.value.slice(0, 80))}
              placeholder="Jane Smith"
              className="w-full rounded-lg border border-pwc-surface-dark px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pwc-orange/40"
              required
            />
          </div>
          <div>
            <label htmlFor="inv-role" className="mb-1 block text-xs font-medium text-pwc-navy">Role</label>
            <select
              id="inv-role"
              value={form.role}
              onChange={(e) => update('role', e.target.value)}
              className="w-full rounded-lg border border-pwc-surface-dark bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pwc-orange/40"
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>{r.replace(/_/g, ' ')}</option>
              ))}
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
              Send Invitation
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function AdminUsers() {
  const { user: me } = useAuth()
  const [users,      setUsers]      = useState([])
  const [loading,    setLoading]    = useState(true)
  const [showInvite, setShowInvite] = useState(false)
  const [busyId,     setBusyId]     = useState(null)

  useEffect(() => {
    adminApi.listUsers().then(setUsers).finally(() => setLoading(false))
  }, [])

  async function handleRoleChange(userId, role) {
    setBusyId(userId)
    try {
      await adminApi.updateUserRole(userId, role)
      setUsers((prev) => prev.map((u) => u.user_id === userId ? { ...u, role } : u))
      toast.success('Role updated')
    } catch {
      toast.error('Failed to update role')
    } finally {
      setBusyId(null)
    }
  }

  async function handleToggleActive(userId, currentlyActive) {
    setBusyId(userId)
    try {
      await adminApi.toggleUserActive(userId, !currentlyActive)
      setUsers((prev) => prev.map((u) => u.user_id === userId ? { ...u, is_active: !currentlyActive } : u))
      toast.success(currentlyActive ? 'User deactivated' : 'User activated')
    } catch {
      toast.error('Failed to update user status')
    } finally {
      setBusyId(null)
    }
  }

  if (loading) return <PageLoader />

  const active   = users.filter((u) => u.is_active).length
  const inactive = users.length - active

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs text-pwc-gray-cool">
          {users.length} users · {active} active · {inactive} inactive
        </p>
        <button
          onClick={() => setShowInvite(true)}
          className="flex items-center gap-2 rounded-lg bg-pwc-orange px-3 py-1.5 text-xs font-medium text-white hover:bg-pwc-orange-dark transition-colors"
        >
          <UserPlusIcon className="h-3.5 w-3.5" />
          Invite User
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-pwc-surface-dark bg-white shadow-card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-pwc-surface-dark bg-pwc-surface text-left">
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">User</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Role</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Status</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Last Login</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-pwc-gray-cool">Provisioned</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-pwc-surface-dark">
              {users.map((u) => {
                const isMe = u.email === me?.email
                const isBusy = busyId === u.user_id

                return (
                  <tr
                    key={u.user_id}
                    className={`transition-colors hover:bg-pwc-surface/50 ${!u.is_active ? 'opacity-60' : ''}`}
                  >
                    {/* User cell */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-pwc-orange/10 text-[11px] font-bold uppercase text-pwc-orange">
                          {u.display_name.split(' ').map((n) => n[0]).join('').slice(0, 2)}
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-semibold text-pwc-navy">
                            {u.display_name}
                            {isMe && <span className="ml-1.5 text-[10px] font-normal text-pwc-gray-cool">(you)</span>}
                          </p>
                          <p className="truncate text-[11px] text-pwc-gray-cool">{u.email}</p>
                        </div>
                      </div>
                    </td>

                    {/* Role cell */}
                    <td className="px-4 py-3">
                      {isMe ? (
                        <Badge type="role" value={u.role} />
                      ) : (
                        <select
                          value={u.role}
                          onChange={(e) => handleRoleChange(u.user_id, e.target.value)}
                          disabled={isBusy}
                          aria-label={`Role for ${u.display_name}`}
                          className="rounded-md border border-pwc-surface-dark bg-white px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-pwc-orange/40 disabled:opacity-50"
                        >
                          {ROLES.map((r) => (
                            <option key={r} value={r}>{r.replace(/_/g, ' ')}</option>
                          ))}
                        </select>
                      )}
                    </td>

                    {/* Status cell */}
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[11px] font-medium ring-1 ring-inset ${
                        u.is_active
                          ? 'bg-green-50 text-green-700 ring-green-200'
                          : 'bg-gray-100 text-gray-500 ring-gray-200'
                      }`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${u.is_active ? 'bg-green-500' : 'bg-gray-400'}`} />
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>

                    <td className="whitespace-nowrap px-4 py-3 text-xs text-pwc-gray-cool">
                      {timeAgo(u.last_login_at)}
                    </td>

                    <td className="px-4 py-3">
                      {u.jit_provisioned && (
                        <span className="rounded-full bg-sky-50 px-2 py-0.5 text-[10px] font-medium text-sky-700 ring-1 ring-inset ring-sky-200">
                          JIT
                        </span>
                      )}
                    </td>

                    <td className="px-4 py-3 text-right">
                      {!isMe && (
                        <button
                          onClick={() => handleToggleActive(u.user_id, u.is_active)}
                          disabled={isBusy}
                          aria-label={u.is_active ? `Deactivate ${u.display_name}` : `Activate ${u.display_name}`}
                          className={`text-xs font-medium transition-colors disabled:opacity-50 ${
                            u.is_active
                              ? 'text-red-600 hover:text-red-800'
                              : 'text-green-600 hover:text-green-800'
                          }`}
                        >
                          {isBusy
                            ? <Spinner size="sm" />
                            : u.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {showInvite && (
        <InviteModal
          onClose={() => setShowInvite(false)}
          onInvite={(user) => setUsers((prev) => [...prev, user])}
        />
      )}
    </div>
  )
}
