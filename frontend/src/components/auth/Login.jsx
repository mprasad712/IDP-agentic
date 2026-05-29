import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { useAuth } from '../../context/AuthContext'
import { authApi } from '../../api/auth'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({ email: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.email || !form.password) {
      setError('Email and password are required.')
      return
    }
    setLoading(true)
    try {
      const data = await authApi.login(form.email, form.password)
      login(data.access_token, data.user)
      toast.success(`Welcome back, ${data.user.display_name}`)
      navigate('/dashboard')
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Invalid credentials. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-pwc-navy">
      {/* ── Left panel — branding ── */}
      <div className="hidden lg:flex lg:w-[55%] flex-col relative overflow-hidden">
        {/* Background gradient layers */}
        <div className="absolute inset-0 bg-gradient-to-br from-pwc-navy via-pwc-navy-light to-pwc-navy-muted" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(208,74,2,0.18),transparent_60%)]" />
        <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-pwc-navy to-transparent" />

        {/* Grid texture overlay */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`,
            backgroundSize: '48px 48px',
          }}
        />

        {/* Content */}
        <div className="relative flex flex-col h-full px-14 py-12">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-pwc-orange rounded-lg flex items-center justify-center shadow-glow-orange">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
            </div>
            <span className="text-white font-bold text-xl tracking-tight">IDP</span>
          </div>

          {/* Main headline */}
          <div className="mt-auto mb-16">
            <div className="inline-flex items-center gap-2 bg-pwc-orange/10 border border-pwc-orange/20 rounded-full px-4 py-1.5 mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-pwc-orange animate-pulse" />
              <span className="text-pwc-orange text-xs font-medium tracking-wide uppercase">AI-Powered · Audit-Grade</span>
            </div>

            <h1 className="text-5xl font-extrabold text-white leading-[1.1] tracking-tight mb-5">
              One Platform.<br />
              <span className="text-pwc-orange">Any Document.</span><br />
              Any Channel.
            </h1>

            <p className="text-pwc-gray-cool text-lg leading-relaxed max-w-md">
              Classify, extract, validate and audit data from any document — with full reasoning trace and compliance-grade provenance.
            </p>

            {/* Stats row */}
            <div className="mt-10 flex gap-8">
              {[
                { value: '30+', label: 'Document types' },
                { value: '99%', label: 'Extraction accuracy' },
                { value: '7yr', label: 'Audit retention' },
              ].map((s) => (
                <div key={s.label}>
                  <p className="text-2xl font-bold text-white">{s.value}</p>
                  <p className="text-pwc-gray-cool text-xs mt-0.5">{s.label}</p>
                </div>
              ))}
            </div>

            {/* Pillar chips */}
            <div className="mt-8 flex flex-wrap gap-2">
              {['Channel-Agnostic Intake', 'Image Quality Pipeline', 'Visual Element Detection',
                'Long Document Handling', 'Audit-Grade Output'].map((p) => (
                <span
                  key={p}
                  className="text-xs text-pwc-gray-light bg-white/5 border border-white/10 rounded-full px-3 py-1"
                >
                  {p}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Right panel — login form ── */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 sm:px-12 bg-pwc-surface relative">
        {/* Mobile logo */}
        <div className="lg:hidden absolute top-8 left-6 flex items-center gap-2">
          <div className="w-8 h-8 bg-pwc-orange rounded-md flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
          </div>
          <span className="text-pwc-navy font-bold text-lg tracking-tight">IDP</span>
        </div>

        <div className="w-full max-w-[400px]">
          {/* Header */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-pwc-navy">Sign in</h2>
            <p className="text-pwc-gray-cool text-sm mt-1">
              Use your organisation credentials to continue
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} noValidate className="space-y-5">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-pwc-navy mb-1.5">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                value={form.email}
                onChange={handleChange}
                placeholder="you@organisation.com"
                className="w-full rounded-lg border border-pwc-surface-dark bg-white px-4 py-2.5 text-sm
                  text-pwc-navy placeholder-pwc-gray-cool
                  focus:outline-none focus:ring-2 focus:ring-pwc-orange focus:border-transparent
                  transition-all duration-150"
              />
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="password" className="block text-sm font-medium text-pwc-navy">
                  Password
                </label>
                <button
                  type="button"
                  className="text-xs text-pwc-orange hover:text-pwc-orange-dark font-medium transition-colors"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  className="w-full rounded-lg border border-pwc-surface-dark bg-white px-4 py-2.5 pr-11 text-sm
                    text-pwc-navy placeholder-pwc-gray-cool
                    focus:outline-none focus:ring-2 focus:ring-pwc-orange focus:border-transparent
                    transition-all duration-150"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-pwc-gray-cool hover:text-pwc-navy transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <svg className="w-4.5 h-4.5 w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                    </svg>
                  ) : (
                    <svg className="w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Error message */}
            {error && (
              <div className="flex items-start gap-2.5 rounded-lg bg-red-50 border border-red-200 px-4 py-3">
                <svg className="w-4 h-4 text-red-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                </svg>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-pwc-orange
                px-4 py-2.5 text-sm font-semibold text-white
                hover:bg-pwc-orange-dark active:scale-[0.99]
                focus:outline-none focus:ring-2 focus:ring-pwc-orange focus:ring-offset-2
                disabled:opacity-60 disabled:cursor-not-allowed
                transition-all duration-150 shadow-sm"
            >
              {loading ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Signing in…
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          {/* SSO divider */}
          <div className="mt-6 flex items-center gap-3">
            <div className="flex-1 h-px bg-pwc-surface-dark" />
            <span className="text-xs text-pwc-gray-cool whitespace-nowrap">or continue with</span>
            <div className="flex-1 h-px bg-pwc-surface-dark" />
          </div>

          {/* SSO buttons */}
          <div className="mt-4 grid grid-cols-2 gap-3">
            {/* Microsoft */}
            <button
              type="button"
              disabled
              title="Microsoft SSO — coming soon"
              className="flex items-center justify-center gap-2 rounded-lg border border-pwc-surface-dark
                bg-white px-3 py-2.5 text-sm font-medium text-pwc-slate
                hover:border-pwc-gray-cool hover:bg-pwc-surface
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-150"
            >
              {/* Microsoft logo */}
              <svg className="w-4 h-4 shrink-0" viewBox="0 0 21 21" fill="none">
                <rect x="1" y="1" width="9" height="9" fill="#F25022" />
                <rect x="11" y="1" width="9" height="9" fill="#7FBA00" />
                <rect x="1" y="11" width="9" height="9" fill="#00A4EF" />
                <rect x="11" y="11" width="9" height="9" fill="#FFB900" />
              </svg>
              Microsoft
            </button>

            {/* Google */}
            <button
              type="button"
              disabled
              title="Google SSO — coming soon"
              className="flex items-center justify-center gap-2 rounded-lg border border-pwc-surface-dark
                bg-white px-3 py-2.5 text-sm font-medium text-pwc-slate
                hover:border-pwc-gray-cool hover:bg-pwc-surface
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-150"
            >
              {/* Google logo */}
              <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google
            </button>
          </div>

          <p className="mt-2 text-center text-[11px] text-pwc-gray-cool">
            SSO integration available — contact your administrator
          </p>

          {/* Register link */}
          <p className="mt-6 text-center text-sm text-pwc-gray-cool">
            Don't have an account?{' '}
            <a
              href="/register"
              className="font-semibold text-pwc-orange hover:text-pwc-orange-dark transition-colors"
            >
              Request access
            </a>
          </p>

          {/* Demo credentials hint */}
          <div className="mt-5 rounded-lg border border-pwc-surface-dark bg-white px-4 py-3">
            <p className="text-xs font-medium text-pwc-navy mb-2">Demo credentials</p>
            <div className="space-y-1">
              <p className="text-xs text-pwc-gray-cool">
                <span className="font-medium text-pwc-slate">Admin:</span>{' '}
                admin@idp.local / Admin@123
              </p>
              <p className="text-xs text-pwc-gray-cool">
                <span className="font-medium text-pwc-slate">Reviewer:</span>{' '}
                reviewer@idp.local / Review@123
              </p>
            </div>
          </div>

          {/* Footer */}
          <p className="mt-6 text-center text-xs text-pwc-gray-cool">
            © {new Date().getFullYear()} Document Intelligence Platform
          </p>
        </div>
      </div>
    </div>
  )
}
