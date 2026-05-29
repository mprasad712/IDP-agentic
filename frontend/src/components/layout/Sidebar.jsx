import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import clsx from 'clsx'
import { toast } from 'react-toastify'
import {
  HomeIcon, DocumentTextIcon, DocumentDuplicateIcon,
  UserGroupIcon, ChartBarSquareIcon, ShieldCheckIcon,
  ArrowRightOnRectangleIcon, Cog6ToothIcon, ArrowUpTrayIcon,
  ChevronDoubleLeftIcon, ChevronDoubleRightIcon,
} from '@heroicons/react/24/outline'
import { useAuth } from '../../context/AuthContext'

const NAV = [
  { label: 'Dashboard',      to: '/dashboard',            icon: HomeIcon,             roles: null },
  { label: 'Cases',          to: '/cases',                icon: DocumentTextIcon,      roles: ['reviewer','senior_reviewer','administrator','operations','compliance_officer'] },
  { label: 'Upload',         to: '/upload',               icon: ArrowUpTrayIcon,       roles: ['reviewer','senior_reviewer','administrator','operations'] },
  { divider: 'Administration', roles: ['administrator'] },
  { label: 'Document Types', to: '/admin/document-types', icon: DocumentDuplicateIcon, roles: ['administrator'] },
  { label: 'Users',          to: '/admin/users',          icon: UserGroupIcon,         roles: ['administrator'] },
  { label: 'Settings',       to: '/admin/settings',       icon: Cog6ToothIcon,         roles: ['administrator'], soon: true },
  { divider: 'Monitoring',   roles: ['administrator','operations'] },
  { label: 'Operations',     to: '/ops',                  icon: ChartBarSquareIcon,    roles: ['administrator','operations'] },
  { divider: 'Compliance',   roles: ['compliance_officer','administrator'] },
  { label: 'Audit Log',      to: '/audit',                icon: ShieldCheckIcon,       roles: ['compliance_officer','administrator'], soon: true },
]

function canSee(item, role) {
  if (!item.roles) return true
  return item.roles.includes(role)
}

function userInitials(name = '') {
  return name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
}

// Shared CSS transition values
const W_TRANSITION  = 'width 240ms cubic-bezier(0.4, 0, 0.2, 1)'
const FX_TRANSITION = 'opacity 160ms ease, max-width 220ms cubic-bezier(0.4, 0, 0.2, 1), margin 220ms ease'

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem('idp_sidebar_collapsed') === 'true'
  )

  function toggle() {
    setCollapsed((v) => {
      localStorage.setItem('idp_sidebar_collapsed', String(!v))
      return !v
    })
  }

  async function handleLogout() {
    logout()
    toast.info('Signed out successfully')
    navigate('/login')
  }

  const role     = user?.role ?? 'reviewer'
  const initials = userInitials(user?.display_name)

  return (
    <aside
      className="relative flex h-full flex-shrink-0 flex-col bg-pwc-navy overflow-hidden"
      style={{ width: collapsed ? 64 : 256, transition: W_TRANSITION }}
    >
      {/* ── Logo header ─────────────────────────────────────────────── */}
      {/*
        Two overlapping absolute layers that cross-fade.
        No layout reflow — both are always in the DOM.
      */}
      <div className="relative h-[57px] flex-shrink-0 border-b border-white/10">
        {/* Collapsed state: centered IDP icon that doubles as expand button */}
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{
            opacity: collapsed ? 1 : 0,
            pointerEvents: collapsed ? 'auto' : 'none',
            transition: 'opacity 160ms ease',
          }}
        >
          <button
            onClick={toggle}
            title="Expand sidebar"
            className="flex h-9 w-9 items-center justify-center rounded-lg hover:bg-white/10 text-pwc-gray-cool hover:text-white transition-colors"
          >
            <ChevronDoubleRightIcon className="h-[18px] w-[18px]" />
          </button>
        </div>

        {/* Expanded state: logo + text + collapse button */}
        <div
          className="absolute inset-0 flex items-center gap-3 px-4"
          style={{
            opacity: collapsed ? 0 : 1,
            pointerEvents: collapsed ? 'none' : 'auto',
            transition: 'opacity 160ms ease',
          }}
        >
          <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg bg-pwc-orange shadow-glow-orange">
            <DocumentTextIcon className="h-[15px] w-[15px] text-white" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="block text-sm font-bold tracking-tight text-white">IDP</p>
            <p className="block text-[10px] leading-none text-pwc-gray-cool">Document Intelligence</p>
          </div>
          <button
            onClick={toggle}
            title="Collapse sidebar"
            className="flex-shrink-0 rounded p-1 text-pwc-gray-cool hover:bg-white/10 hover:text-white transition-colors"
          >
            <ChevronDoubleLeftIcon className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* ── Nav ─────────────────────────────────────────────────────── */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden px-2 py-3 space-y-0.5">
        {NAV.map((item, i) => {
          if (!canSee(item, role)) return null

          // Section dividers — simple HR when collapsed, full label when expanded
          if (item.divider) {
            return (
              <div key={i} className="overflow-hidden">
                {/* HR line — visible when collapsed */}
                <hr
                  className="border-white/10"
                  style={{
                    opacity: collapsed ? 1 : 0,
                    height: collapsed ? 1 : 0,
                    marginTop: collapsed ? 8 : 0,
                    marginBottom: collapsed ? 8 : 0,
                    marginLeft: 8,
                    marginRight: 8,
                    overflow: 'hidden',
                    transition: 'opacity 160ms ease, height 220ms ease, margin 220ms ease',
                  }}
                />
                {/* Section label — visible when expanded */}
                <p
                  className="px-3 text-[10px] font-semibold uppercase tracking-widest text-pwc-gray-cool/60 whitespace-nowrap overflow-hidden"
                  style={{
                    opacity: collapsed ? 0 : 1,
                    maxHeight: collapsed ? 0 : 40,
                    paddingTop: collapsed ? 0 : 20,
                    paddingBottom: collapsed ? 0 : 6,
                    transition: 'opacity 160ms ease, max-height 220ms ease, padding 220ms ease',
                  }}
                >
                  {item.divider}
                </p>
              </div>
            )
          }

          // Nav link
          return (
            <NavLink
              key={item.to}
              to={item.soon ? '#' : item.to}
              onClick={item.soon ? (e) => e.preventDefault() : undefined}
              title={collapsed ? item.label + (item.soon ? ' (coming soon)' : '') : undefined}
              className={({ isActive }) => clsx(
                'flex w-full items-center rounded-lg py-2 text-sm font-medium transition-colors duration-150',
                isActive && !item.soon
                  ? 'bg-pwc-orange text-white'
                  : 'text-pwc-gray-light hover:bg-white/[0.08] hover:text-white',
                item.soon && 'cursor-not-allowed opacity-50'
              )}
              style={{ paddingLeft: collapsed ? 23 : 12, paddingRight: collapsed ? 23 : 12, transition: `padding 220ms cubic-bezier(0.4,0,0.2,1)` }}
            >
              <item.icon className="h-[18px] w-[18px] flex-shrink-0" />

              {/* Label — always in DOM, collapses via max-width + opacity */}
              <span
                className="truncate text-sm font-medium"
                style={{
                  opacity: collapsed ? 0 : 1,
                  maxWidth: collapsed ? 0 : 200,
                  overflow: 'hidden',
                  whiteSpace: 'nowrap',
                  marginLeft: collapsed ? 0 : 12,
                  transition: FX_TRANSITION,
                  transitionDelay: collapsed ? '0ms' : '60ms',
                }}
              >
                {item.label}
              </span>

              {/* "Soon" badge — collapses with label */}
              {item.soon && (
                <span
                  className="rounded bg-white/10 px-1.5 py-0.5 text-[10px] font-medium text-pwc-gray-cool whitespace-nowrap"
                  style={{
                    opacity: collapsed ? 0 : 1,
                    maxWidth: collapsed ? 0 : 48,
                    overflow: 'hidden',
                    marginLeft: collapsed ? 0 : 'auto',
                    transition: FX_TRANSITION,
                  }}
                >
                  Soon
                </span>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* ── User footer ─────────────────────────────────────────────── */}
      {/*
        Same cross-fade pattern as the header.
        Two overlapping absolute layers, always in DOM.
      */}
      <div className="relative h-[60px] flex-shrink-0 border-t border-white/10">
        {/* Collapsed state: avatar + logout stacked and centered */}
        <div
          className="absolute inset-0 flex flex-col items-center justify-center gap-1"
          style={{
            opacity: collapsed ? 1 : 0,
            pointerEvents: collapsed ? 'auto' : 'none',
            transition: 'opacity 160ms ease',
          }}
        >
          <div
            title={`${user?.display_name} · ${user?.role?.replace(/_/g, ' ')}`}
            className="flex h-7 w-7 items-center justify-center rounded-full bg-pwc-orange/20 text-[10px] font-semibold uppercase text-pwc-orange"
          >
            {initials}
          </div>
          <button
            onClick={handleLogout}
            title="Sign out"
            className="rounded p-0.5 text-pwc-gray-cool hover:bg-white/10 hover:text-white transition-colors"
          >
            <ArrowRightOnRectangleIcon className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Expanded state: avatar + name/role + logout in a row */}
        <div
          className="absolute inset-0 flex items-center gap-3 px-3"
          style={{
            opacity: collapsed ? 0 : 1,
            pointerEvents: collapsed ? 'none' : 'auto',
            transition: 'opacity 160ms ease',
          }}
        >
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-pwc-orange/20 text-xs font-semibold uppercase text-pwc-orange">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-semibold text-white">{user?.display_name}</p>
            <p className="truncate text-[11px] capitalize text-pwc-gray-cool">{user?.role?.replace(/_/g, ' ')}</p>
          </div>
          <button
            onClick={handleLogout}
            title="Sign out"
            className="flex-shrink-0 rounded p-1 text-pwc-gray-cool hover:bg-white/10 hover:text-white transition-colors"
          >
            <ArrowRightOnRectangleIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}
