import { Routes, Route, Navigate } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import { AuthProvider, useAuth } from './context/AuthContext'
import AppShell from './components/layout/AppShell'
import Login from './components/auth/Login'
import Register from './components/auth/Register'
import Dashboard from './pages/Dashboard'
import CasesList from './pages/CasesList'
import CaseDetail from './pages/CaseDetail'
import AdminDocumentTypes from './pages/admin/DocumentTypes'
import AdminUsers from './pages/admin/Users'
import Operations from './pages/Operations'
import Upload from './pages/Upload'

const CASE_ROLES   = ['reviewer', 'senior_reviewer', 'administrator', 'operations', 'compliance_officer']
const UPLOAD_ROLES = ['reviewer', 'senior_reviewer', 'administrator', 'operations']
const ADMIN_ROLES  = ['administrator']
const OPS_ROLES    = ['administrator', 'operations']

function PrivateRoute({ children, roles }) {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  if (roles?.length && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />
  return children
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return null
  return !user ? children : <Navigate to="/dashboard" replace />
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login"    element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

      {/* Protected — all roles */}
      <Route path="/dashboard" element={
        <PrivateRoute>
          <AppShell><Dashboard /></AppShell>
        </PrivateRoute>
      } />

      {/* Protected — reviewer+ (upload) */}
      <Route path="/upload" element={
        <PrivateRoute roles={UPLOAD_ROLES}>
          <AppShell><Upload /></AppShell>
        </PrivateRoute>
      } />

      {/* Protected — reviewer+ */}
      <Route path="/cases" element={
        <PrivateRoute roles={CASE_ROLES}>
          <AppShell><CasesList /></AppShell>
        </PrivateRoute>
      } />
      <Route path="/cases/:id" element={
        <PrivateRoute roles={CASE_ROLES}>
          <AppShell><CaseDetail /></AppShell>
        </PrivateRoute>
      } />

      {/* Protected — administrator only */}
      <Route path="/admin/document-types" element={
        <PrivateRoute roles={ADMIN_ROLES}>
          <AppShell><AdminDocumentTypes /></AppShell>
        </PrivateRoute>
      } />
      <Route path="/admin/users" element={
        <PrivateRoute roles={ADMIN_ROLES}>
          <AppShell><AdminUsers /></AppShell>
        </PrivateRoute>
      } />

      {/* Protected — ops + admin */}
      <Route path="/ops" element={
        <PrivateRoute roles={OPS_ROLES}>
          <AppShell><Operations /></AppShell>
        </PrivateRoute>
      } />

      {/* Fallback: unknown routes go to dashboard (PrivateRoute handles unauthenticated → /login) */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        closeOnClick
        pauseOnHover
        draggable
        theme="light"
      />
    </AuthProvider>
  )
}
