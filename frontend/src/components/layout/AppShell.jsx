import Sidebar from './Sidebar'
import TopBar from './TopBar'

export default function AppShell({ children }) {
  return (
    <div className="flex h-screen overflow-hidden bg-pwc-surface">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
