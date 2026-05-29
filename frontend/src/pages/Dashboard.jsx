import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { user, logout } = useAuth()
  return (
    <div className="min-h-screen bg-pwc-surface flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-pwc-navy mb-2">
          Welcome, {user?.display_name}
        </h1>
        <p className="text-pwc-gray-cool text-sm mb-6">Dashboard coming soon.</p>
        <button
          onClick={logout}
          className="text-sm text-pwc-orange hover:underline"
        >
          Sign out
        </button>
      </div>
    </div>
  )
}
