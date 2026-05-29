import clsx from 'clsx'

const CASE_STATUS = {
  AUTO_APPROVED: { label: 'Auto-Approved', classes: 'bg-green-50  text-green-700  ring-green-200' },
  NEEDS_REVIEW:  { label: 'Needs Review',  classes: 'bg-amber-50  text-amber-700  ring-amber-200' },
  PENDING:       { label: 'Pending',       classes: 'bg-violet-50 text-violet-700 ring-violet-200' },
  PROCESSING:    { label: 'Processing',    classes: 'bg-blue-50   text-blue-700   ring-blue-200',   pulse: true },
  REJECTED:      { label: 'Rejected',      classes: 'bg-red-50    text-red-700    ring-red-200' },
  DUPLICATE:     { label: 'Duplicate',     classes: 'bg-gray-100  text-gray-600   ring-gray-200' },
}

const QA_FLAG = {
  PASS:         { label: 'Pass',         classes: 'bg-green-50 text-green-700 ring-green-200' },
  NEEDS_REVIEW: { label: 'Review',       classes: 'bg-amber-50 text-amber-700 ring-amber-200' },
  FAIL:         { label: 'Fail',         classes: 'bg-red-50   text-red-700   ring-red-200' },
}

const CONFIDENTIALITY = {
  PUBLIC:       { label: 'Public',       classes: 'bg-sky-50   text-sky-700   ring-sky-200' },
  INTERNAL:     { label: 'Internal',     classes: 'bg-blue-50  text-blue-700  ring-blue-200' },
  CONFIDENTIAL: { label: 'Confidential', classes: 'bg-amber-50 text-amber-700 ring-amber-200' },
  RESTRICTED:   { label: 'Restricted',   classes: 'bg-red-50   text-red-700   ring-red-200' },
}

const DOC_STATUS = {
  PUBLISHED: { label: 'Published', classes: 'bg-green-50 text-green-700 ring-green-200' },
  DRAFT:     { label: 'Draft',     classes: 'bg-gray-100 text-gray-600  ring-gray-200' },
}

const ROLE = {
  administrator:      { label: 'Administrator',    classes: 'bg-violet-50 text-violet-700 ring-violet-200' },
  senior_reviewer:    { label: 'Sr. Reviewer',     classes: 'bg-blue-50   text-blue-700   ring-blue-200' },
  reviewer:           { label: 'Reviewer',         classes: 'bg-sky-50    text-sky-700    ring-sky-200' },
  compliance_officer: { label: 'Compliance',       classes: 'bg-amber-50  text-amber-700  ring-amber-200' },
  operations:         { label: 'Operations',       classes: 'bg-teal-50   text-teal-700   ring-teal-200' },
  vendor_user:        { label: 'Vendor',           classes: 'bg-gray-100  text-gray-600   ring-gray-200' },
}

const maps = { status: CASE_STATUS, qa: QA_FLAG, confidentiality: CONFIDENTIALITY, docStatus: DOC_STATUS, role: ROLE }

export default function Badge({ type = 'status', value, className }) {
  const config = maps[type]?.[value]
  if (!config) return (
    <span className={clsx('inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset bg-gray-100 text-gray-600 ring-gray-200', className)}>
      {value}
    </span>
  )
  return (
    <span className={clsx('inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset', config.classes, className)}>
      {config.pulse && <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse flex-shrink-0" />}
      {config.label}
    </span>
  )
}
