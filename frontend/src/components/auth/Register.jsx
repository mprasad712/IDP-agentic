import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../../api/auth'

const PASSWORD_RE = /^(?=.*[A-Z])(?=.*\d).{8,}$/

function PasswordStrength({ password }) {
  if (!password) return null
  const checks = [
    { label: '8+ characters',    ok: password.length >= 8 },
    { label: 'Uppercase letter', ok: /[A-Z]/.test(password) },
    { label: 'Number',           ok: /\d/.test(password) },
  ]
  return (
    <div className="mt-1.5 flex gap-3">
      {checks.map(({ label, ok }) => (
        <span key={label} className={`text-[11px] font-medium ${ok ? 'text-green-600' : 'text-pwc-gray-cool'}`}>
          {ok ? '✓' : '·'} {label}
        </span>
      ))}
    </div>
  )
}

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    display_name: '',
    email: '',
    password: '',
    confirm_password: '',
  })
  const [error,     setError]     = useState(null)
  const [busy,      setBusy]      = useState(false)
  const [submitted, setSubmitted] = useState(false)

  function update(k, v) { setForm((f) => ({ ...f, [k]: v })); setError(null) }

  const passwordOk = PASSWORD_RE.test(form.password)
  const confirmOk  = form.password === form.confirm_password && form.confirm_password.length > 0
  const canSubmit  = form.display_name.trim().length >= 2
    && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)
    && passwordOk
    && confirmOk

  async function handleSubmit(e) {
    e.preventDefault()
    if (!canSubmit || busy) return
    setBusy(true)
    setError(null)
    try {
      await authApi.register({
        email:        form.email.trim().toLowerCase(),
        display_name: form.display_name.trim(),
        password:     form.password,
      })
      setSubmitted(true)
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Registration failed. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-pwc-navy">
      {/* Left branding panel */}
      <div className="hidden lg:flex lg:w-[55%] flex-col relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-pwc-navy via-pwc-navy-light to-pwc-navy-muted" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(208,74,2,0.18),transparent_60%)]" />
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`,
            backgroundSize: '48px 48px',
          }}
        />
        <div className="relative flex h-full flex-col px-14 py-12">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-pwc-orange shadow-glow-orange">
              <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
            </div>
            <span className="text-xl font-bold tracking-tight text-white">IDP</span>
          </div>
          <div className="mb-16 mt-auto">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-pwc-orange/20 bg-pwc-orange/10 px-4 py-1.5">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-pwc-orange" />
              <span className="text-xs font-medium uppercase tracking-wide text-pwc-orange">Create Account</span>
            </div>
            <h1 className="mb-5 text-5xl font-extrabold leading-[1.1] tracking-tight text-white">
              Join the<br />
              <span className="text-pwc-orange">Intelligence</span><br />
              Platform.
            </h1>
            <p className="max-w-md text-lg leading-relaxed text-pwc-gray-cool">
              Sign up to start reviewing AI-extracted documents with full audit-grade provenance.
            </p>
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="relative flex flex-1 flex-col items-center justify-center bg-pwc-surface px-6 sm:px-12">
        <div className="lg:hidden absolute left-6 top-8 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-pwc-orange">
            <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
          </div>
          <span className="text-lg font-bold tracking-tight text-pwc-navy">IDP</span>
        </div>

        <div className="w-full max-w-[400px]">
          {submitted ? (
            /* ── Success ───────────────────────────────────────────────── */
            <div className="py-8 text-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
                <svg className="h-7 w-7 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
              </div>
              <h2 className="mb-2 text-xl font-bold text-pwc-navy">Account created</h2>
              <p className="mb-1 text-sm text-pwc-gray-cool">
                You've been registered as a <span className="font-semibold text-pwc-navy">Reviewer</span>.
              </p>
              <p className="mb-6 text-sm text-pwc-gray-cool">
                An administrator can promote your role from <strong>Admin › Users</strong> if needed.
              </p>
              <button
                onClick={() => navigate('/login')}
                className="rounded-lg bg-pwc-orange px-5 py-2.5 text-sm font-semibold text-white hover:bg-pwc-orange-dark transition-colors"
              >
                Sign in now →
              </button>
            </div>
          ) : (
            /* ── Form ──────────────────────────────────────────────────── */
            <>
              <div className="mb-7">
                <h2 className="text-2xl font-bold text-pwc-navy">Create account</h2>
                <p className="mt-1 text-sm text-pwc-gray-cool">
                  You'll be assigned the <span className="font-medium text-pwc-navy">Reviewer</span> role by default. An admin can adjust it later.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                {/* Display name */}
                <div>
                  <label htmlFor="reg-name" className="mb-1.5 block text-sm font-medium text-pwc-navy">
                    Full name <span className="text-red-500" aria-hidden="true">*</span>
                  </label>
                  <input
                    id="reg-name"
                    type="text"
                    autoComplete="name"
                    value={form.display_name}
                    onChange={(e) => update('display_name', e.target.value.slice(0, 80))}
                    placeholder="Jane Smith"
                    required
                    className="w-full rounded-lg border border-pwc-surface-dark bg-white px-4 py-2.5 text-sm text-pwc-navy placeholder-pwc-gray-cool transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-pwc-orange"
                  />
                </div>

                {/* Email */}
                <div>
                  <label htmlFor="reg-email" className="mb-1.5 block text-sm font-medium text-pwc-navy">
                    Work email <span className="text-red-500" aria-hidden="true">*</span>
                  </label>
                  <input
                    id="reg-email"
                    type="email"
                    autoComplete="email"
                    value={form.email}
                    onChange={(e) => update('email', e.target.value.slice(0, 254))}
                    placeholder="jane@organisation.com"
                    required
                    className="w-full rounded-lg border border-pwc-surface-dark bg-white px-4 py-2.5 text-sm text-pwc-navy placeholder-pwc-gray-cool transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-pwc-orange"
                  />
                </div>

                {/* Password */}
                <div>
                  <label htmlFor="reg-pw" className="mb-1.5 block text-sm font-medium text-pwc-navy">
                    Password <span className="text-red-500" aria-hidden="true">*</span>
                  </label>
                  <input
                    id="reg-pw"
                    type="password"
                    autoComplete="new-password"
                    value={form.password}
                    onChange={(e) => update('password', e.target.value.slice(0, 128))}
                    placeholder="Min. 8 characters"
                    required
                    className="w-full rounded-lg border border-pwc-surface-dark bg-white px-4 py-2.5 text-sm text-pwc-navy placeholder-pwc-gray-cool transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-pwc-orange"
                  />
                  <PasswordStrength password={form.password} />
                </div>

                {/* Confirm password */}
                <div>
                  <label htmlFor="reg-cpw" className="mb-1.5 block text-sm font-medium text-pwc-navy">
                    Confirm password <span className="text-red-500" aria-hidden="true">*</span>
                  </label>
                  <input
                    id="reg-cpw"
                    type="password"
                    autoComplete="new-password"
                    value={form.confirm_password}
                    onChange={(e) => update('confirm_password', e.target.value.slice(0, 128))}
                    placeholder="Repeat your password"
                    required
                    className={`w-full rounded-lg border bg-white px-4 py-2.5 text-sm text-pwc-navy placeholder-pwc-gray-cool transition-all focus:border-transparent focus:outline-none focus:ring-2 focus:ring-pwc-orange ${
                      form.confirm_password && !confirmOk
                        ? 'border-red-300'
                        : 'border-pwc-surface-dark'
                    }`}
                  />
                  {form.confirm_password && !confirmOk && (
                    <p className="mt-1 text-[11px] text-red-600">Passwords do not match</p>
                  )}
                </div>

                {/* Server error */}
                {error && (
                  <p className="rounded-lg bg-red-50 px-4 py-2.5 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-200">
                    {error}
                  </p>
                )}

                <button
                  type="submit"
                  disabled={!canSubmit || busy}
                  className="w-full rounded-lg bg-pwc-orange px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-pwc-orange-dark active:scale-[0.99] focus:outline-none focus:ring-2 focus:ring-pwc-orange focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy ? 'Creating account…' : 'Create account'}
                </button>
              </form>

              <p className="mt-6 text-center text-sm text-pwc-gray-cool">
                Already have an account?{' '}
                <Link to="/login" className="font-semibold text-pwc-orange hover:text-pwc-orange-dark transition-colors">
                  Sign in
                </Link>
              </p>
              <p className="mt-4 text-center text-xs text-pwc-gray-cool">
                © {new Date().getFullYear()} Document Intelligence Platform
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
