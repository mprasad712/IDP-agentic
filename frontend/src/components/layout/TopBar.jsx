import { useState, useRef, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import {
  BellIcon, ArrowRightOnRectangleIcon, UserCircleIcon,
  ExclamationTriangleIcon, CheckCircleIcon, InformationCircleIcon,
} from '@heroicons/react/24/outline'
import { toast } from 'react-toastify'
import { useAuth } from '../../context/AuthContext'
import Badge from '../ui/Badge'

// ─── Page title map ───────────────────────────────────────────────────────────

const TITLES = {
  '/dashboard':            'Dashboard',
  '/cases':                'Cases',
  '/upload':               'Upload Document',
  '/admin/document-types': 'Document Types',
  '/admin/users':          'Users',
  '/ops':                  'Operations',
  '/audit':                'Audit Log',
}

function pageTitle(pathname) {
  if (pathname.startsWith('/cases/')) return 'Case Detail'
  return TITLES[pathname] ?? 'IDP Platform'
}

// ─── Mock notifications ───────────────────────────────────────────────────────

const INIT_NOTIFS = [
  {
    id: 'n1', type: 'warning', read: false, time: '2m ago',
    title: 'Case flagged for review',
    body: 'Passport case_f1a2c3d4 — confidence 61%, needs human review',
  },
  {
    id: 'n2', type: 'success', read: false, time: '15m ago',
    title: 'Extraction completed',
    body: 'Invoice case_3d7b9e01 auto-approved at 94% confidence',
  },
  {
    id: 'n3', type: 'info', read: false, time: '1h ago',
    title: 'Model fallback triggered',
    body: 'Claude Sonnet used for long-form Salary Slip (case_e5f6a7b8)',
  },
  {
    id: 'n4', type: 'info', read: true, time: '2h ago',
    title: 'New user provisioned (JIT)',
    body: 'Priya Sharma joined as Senior Reviewer via Entra ID',
  },
  {
    id: 'n5', type: 'warning', read: true, time: '3h ago',
    title: 'Duplicate detected',
    body: 'Invoice INV-2026-04521 matched existing case_b5c6d7e8',
  },
]

const NOTIF_STYLE = {
  warning: { Icon: ExclamationTriangleIcon, cls: 'bg-amber-50 text-amber-500' },
  success: { Icon: CheckCircleIcon,         cls: 'bg-green-50 text-green-600' },
  info:    { Icon: InformationCircleIcon,   cls: 'bg-blue-50  text-blue-500'  },
}

// ─── Click-outside hook ───────────────────────────────────────────────────────

function useClickOutside(ref, handler) {
  useEffect(() => {
    function listen(e) {
      if (!ref.current || ref.current.contains(e.target)) return
      handler()
    }
    document.addEventListener('mousedown', listen)
    return () => document.removeEventListener('mousedown', listen)
  }, [ref, handler])
}

// ─── Notifications dropdown ───────────────────────────────────────────────────

function NotificationsDropdown({ notifs, onMarkAll }) {
  return (
    <div className="absolute right-0 top-full z-50 mt-2 w-80 overflow-hidden rounded-xl border border-pwc-surface-dark bg-white shadow-card-lg">
      <div className="flex items-center justify-between border-b border-pwc-surface-dark px-4 py-3">
        <p className="text-xs font-semibold text-pwc-navy">Notifications</p>
        {notifs.some((n) => !n.read) && (
          <button
            onClick={onMarkAll}
            className="text-[11px] font-medium text-pwc-orange hover:text-pwc-orange-dark transition-colors"
          >
            Mark all read
          </button>
        )}
      </div>

      <ul className="max-h-[340px] divide-y divide-pwc-surface-dark overflow-y-auto">
        {notifs.length === 0 ? (
          <li className="px-4 py-10 text-center text-xs text-pwc-gray-cool">No notifications</li>
        ) : notifs.map((n) => {
          const { Icon, cls } = NOTIF_STYLE[n.type] ?? NOTIF_STYLE.info
          return (
            <li
              key={n.id}
              className={`flex gap-3 px-4 py-3 transition-colors hover:bg-pwc-surface/60 ${!n.read ? 'bg-pwc-orange/[0.025]' : ''}`}
            >
              <div className={`mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full ${cls}`}>
                <Icon className="h-3.5 w-3.5" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-start gap-1.5">
                  <p className={`flex-1 text-xs font-medium leading-tight ${n.read ? 'text-pwc-gray-cool' : 'text-pwc-navy'}`}>
                    {n.title}
                  </p>
                  {!n.read && (
                    <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-pwc-orange" />
                  )}
                </div>
                <p className="mt-0.5 text-[11px] leading-relaxed text-pwc-gray-cool">{n.body}</p>
                <p className="mt-1 text-[10px] text-pwc-gray-cool/60">{n.time}</p>
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

// ─── Profile dropdown ─────────────────────────────────────────────────────────

function ProfileDropdown({ user, onLogout }) {
  const initials = user?.display_name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()

  return (
    <div className="absolute right-0 top-full z-50 mt-2 w-56 overflow-hidden rounded-xl border border-pwc-surface-dark bg-white shadow-card-lg">
      {/* User card */}
      <div className="border-b border-pwc-surface-dark px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-pwc-orange/15 text-sm font-bold uppercase text-pwc-orange">
            {initials}
          </div>
          <div className="min-w-0">
            <p className="truncate text-xs font-semibold text-pwc-navy">{user?.display_name}</p>
            <p className="truncate text-[11px] text-pwc-gray-cool">{user?.email}</p>
          </div>
        </div>
        <div className="mt-2.5">
          <Badge type="role" value={user?.role} />
        </div>
      </div>

      {/* Menu items */}
      <div className="p-1.5">
        <button
          disabled
          title="Coming soon"
          className="flex w-full cursor-not-allowed items-center gap-2.5 rounded-lg px-3 py-2 text-xs text-pwc-gray-cool opacity-50"
        >
          <UserCircleIcon className="h-4 w-4 flex-shrink-0" />
          My Profile
          <span className="ml-auto rounded bg-pwc-surface-dark px-1.5 py-0.5 text-[10px]">Soon</span>
        </button>
        <button
          onClick={onLogout}
          className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-xs text-red-600 hover:bg-red-50 transition-colors"
        >
          <ArrowRightOnRectangleIcon className="h-4 w-4 flex-shrink-0" />
          Sign out
        </button>
      </div>
    </div>
  )
}

// ─── TopBar ───────────────────────────────────────────────────────────────────

export default function TopBar() {
  const { pathname }     = useLocation()
  const navigate         = useNavigate()
  const { user, logout } = useAuth()

  const [notifs,      setNotifs]      = useState(INIT_NOTIFS)
  const [showNotifs,  setShowNotifs]  = useState(false)
  const [showProfile, setShowProfile] = useState(false)

  const notifsRef  = useRef(null)
  const profileRef = useRef(null)

  useClickOutside(notifsRef,  () => setShowNotifs(false))
  useClickOutside(profileRef, () => setShowProfile(false))

  const unreadCount = notifs.filter((n) => !n.read).length

  function handleMarkAll() {
    setNotifs((prev) => prev.map((n) => ({ ...n, read: true })))
  }

  function handleLogout() {
    logout()
    toast.info('Signed out successfully')
    navigate('/login')
  }

  const initials = user?.display_name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()

  return (
    <header className="flex h-14 flex-shrink-0 items-center justify-between border-b border-pwc-surface-dark bg-white px-6">
      <h1 className="text-sm font-semibold text-pwc-navy">{pageTitle(pathname)}</h1>

      <div className="flex items-center gap-2">

        {/* Notifications bell */}
        <div ref={notifsRef} className="relative">
          <button
            onClick={() => { setShowNotifs((v) => !v); setShowProfile(false) }}
            aria-label={`Notifications — ${unreadCount} unread`}
            className="relative rounded-lg p-1.5 text-pwc-gray-cool hover:bg-pwc-surface hover:text-pwc-navy transition-colors"
          >
            <BellIcon className="h-5 w-5" />
            {unreadCount > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex h-[18px] w-[18px] items-center justify-center rounded-full bg-pwc-orange text-[9px] font-bold leading-none text-white">
                {unreadCount}
              </span>
            )}
          </button>
          {showNotifs && (
            <NotificationsDropdown notifs={notifs} onMarkAll={handleMarkAll} />
          )}
        </div>

        {/* Vertical divider */}
        <div className="h-5 w-px bg-pwc-surface-dark" aria-hidden="true" />

        {/* Profile avatar */}
        <div ref={profileRef} className="relative">
          <button
            onClick={() => { setShowProfile((v) => !v); setShowNotifs(false) }}
            aria-label="Open profile menu"
            className="flex h-8 w-8 items-center justify-center rounded-full bg-pwc-orange/15 text-xs font-bold uppercase text-pwc-orange ring-2 ring-transparent hover:bg-pwc-orange/25 hover:ring-pwc-orange/30 transition-all"
          >
            {initials}
          </button>
          {showProfile && (
            <ProfileDropdown user={user} onLogout={handleLogout} />
          )}
        </div>

      </div>
    </header>
  )
}
