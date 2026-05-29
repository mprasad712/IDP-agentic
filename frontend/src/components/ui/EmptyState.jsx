export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {Icon && (
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-pwc-surface-dark">
          <Icon className="h-7 w-7 text-pwc-gray-cool" />
        </div>
      )}
      <p className="text-sm font-semibold text-pwc-navy">{title}</p>
      {description && <p className="mt-1 text-sm text-pwc-gray-cool max-w-xs">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}
