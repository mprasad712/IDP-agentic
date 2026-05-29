// Mock data for IDP — swap API modules to USE_MOCK=false once backend endpoints are live

const now = new Date()
const hoursAgo = (n) => new Date(now - n * 3_600_000).toISOString()
const daysAgo  = (n) => new Date(now - n * 86_400_000).toISOString()

// ─── Users ───────────────────────────────────────────────────────────────────

export const mockUsers = [
  { user_id: 'usr_admin_001', email: 'admin@idp.local',        display_name: 'Admin User',          role: 'administrator',      is_active: true,  last_login_at: hoursAgo(2),  jit_provisioned: false },
  { user_id: 'usr_rev_001',   email: 'reviewer@idp.local',     display_name: 'Sarah Chen',           role: 'reviewer',           is_active: true,  last_login_at: hoursAgo(1),  jit_provisioned: false },
  { user_id: 'usr_rev_002',   email: 'priya.sharma@pwc.com',   display_name: 'Priya Sharma',         role: 'senior_reviewer',    is_active: true,  last_login_at: hoursAgo(4),  jit_provisioned: true  },
  { user_id: 'usr_ops_001',   email: 'ops@idp.local',          display_name: 'Operations Team',      role: 'operations',         is_active: true,  last_login_at: daysAgo(1),   jit_provisioned: false },
  { user_id: 'usr_cmp_001',   email: 'compliance@idp.local',   display_name: 'Compliance Officer',   role: 'compliance_officer', is_active: true,  last_login_at: daysAgo(2),   jit_provisioned: false },
  { user_id: 'usr_vnd_001',   email: 'vendor@acmecorp.in',     display_name: 'Acme Corp (Vendor)',   role: 'vendor_user',        is_active: true,  last_login_at: daysAgo(3),   jit_provisioned: true  },
  { user_id: 'usr_rev_003',   email: 'james.wilson@pwc.com',   display_name: 'James Wilson',         role: 'reviewer',           is_active: false, last_login_at: daysAgo(14),  jit_provisioned: false },
  { user_id: 'usr_rev_004',   email: 'anil.kumar@pwc.com',     display_name: 'Anil Kumar',           role: 'reviewer',           is_active: true,  last_login_at: hoursAgo(6),  jit_provisioned: false },
]

// ─── Document types ───────────────────────────────────────────────────────────

export const mockDocumentTypes = [
  { doc_type_id: 'dt_001', name: 'Invoice',              category: 'Financial — AP/AR',       confidentiality: 'INTERNAL',      version: 3, status: 'PUBLISHED', fields_count: 14, published_at: daysAgo(45),  published_by: 'admin@idp.local' },
  { doc_type_id: 'dt_002', name: 'Bank Statement',       category: 'Financial — Banking',     confidentiality: 'CONFIDENTIAL',  version: 2, status: 'PUBLISHED', fields_count: 9,  published_at: daysAgo(30),  published_by: 'admin@idp.local' },
  { doc_type_id: 'dt_003', name: 'Passport',             category: 'KYC & Identity',          confidentiality: 'RESTRICTED',    version: 1, status: 'PUBLISHED', fields_count: 8,  published_at: daysAgo(60),  published_by: 'admin@idp.local' },
  { doc_type_id: 'dt_004', name: 'Purchase Order',       category: 'Financial — AP/AR',       confidentiality: 'INTERNAL',      version: 2, status: 'PUBLISHED', fields_count: 11, published_at: daysAgo(20),  published_by: 'admin@idp.local' },
  { doc_type_id: 'dt_005', name: 'Contract / Agreement', category: 'Legal & Contracts',       confidentiality: 'CONFIDENTIAL',  version: 1, status: 'DRAFT',     fields_count: 7,  published_at: null,          published_by: null },
  { doc_type_id: 'dt_006', name: 'Salary Slip',          category: 'HR & Payroll',            confidentiality: 'RESTRICTED',    version: 1, status: 'PUBLISHED', fields_count: 12, published_at: daysAgo(15),  published_by: 'admin@idp.local' },
  { doc_type_id: 'dt_007', name: 'Driving Licence',      category: 'KYC & Identity',          confidentiality: 'RESTRICTED',    version: 1, status: 'DRAFT',     fields_count: 6,  published_at: null,          published_by: null },
  { doc_type_id: 'dt_008', name: 'Lab Report',           category: 'Healthcare',              confidentiality: 'RESTRICTED',    version: 1, status: 'PUBLISHED', fields_count: 10, published_at: daysAgo(7),   published_by: 'admin@idp.local' },
]

// ─── Cases list ───────────────────────────────────────────────────────────────

const mkCase = (id, overrides) => ({
  case_id: `case_${id}`,
  document_type: { name: 'Invoice', version: 3 },
  status: 'NEEDS_REVIEW',
  received_at: hoursAgo(Math.random() * 48),
  source_channel: 'ms365_mail',
  aggregate_confidence: 0.78 + Math.random() * 0.18,
  extraction: {
    model_provider: 'azure_openai',
    model_name: 'gpt-4o',
    tokens_used: 4800 + Math.floor(Math.random() * 2000),
    cost_usd: 0.018 + Math.random() * 0.015,
    attempt_number: 1,
  },
  assigned_to: null,
  ...overrides,
})

export const mockCases = [
  mkCase('8f4e2a1c', { document_type: { name: 'Invoice', version: 3 },        status: 'NEEDS_REVIEW',   received_at: hoursAgo(1),    source_channel: 'ms365_mail',    aggregate_confidence: 0.76, assigned_to: 'Sarah Chen' }),
  mkCase('3d7b9e01', { document_type: { name: 'Bank Statement', version: 2 }, status: 'AUTO_APPROVED',  received_at: hoursAgo(2),    source_channel: 'google_drive',  aggregate_confidence: 0.94 }),
  mkCase('f1a2c3d4', { document_type: { name: 'Passport', version: 1 },       status: 'NEEDS_REVIEW',   received_at: hoursAgo(3),    source_channel: 'vendor_portal', aggregate_confidence: 0.61, assigned_to: 'Priya Sharma' }),
  mkCase('5e6f7a8b', { document_type: { name: 'Invoice', version: 3 },        status: 'AUTO_APPROVED',  received_at: hoursAgo(4),    source_channel: 'ms365_mail',    aggregate_confidence: 0.91 }),
  mkCase('9c0d1e2f', { document_type: { name: 'Purchase Order', version: 2 }, status: 'PENDING',        received_at: hoursAgo(0.5),  source_channel: 'rest_upload',   aggregate_confidence: null }),
  mkCase('a1b2c3d4', { document_type: { name: 'Invoice', version: 3 },        status: 'REJECTED',       received_at: hoursAgo(24),   source_channel: 'ms365_mail',    aggregate_confidence: 0.45 }),
  mkCase('e5f6a7b8', { document_type: { name: 'Salary Slip', version: 1 },    status: 'NEEDS_REVIEW',   received_at: hoursAgo(6),    source_channel: 'sftp',          aggregate_confidence: 0.79, assigned_to: 'Sarah Chen' }),
  mkCase('c9d0e1f2', { document_type: { name: 'Invoice', version: 3 },        status: 'AUTO_APPROVED',  received_at: hoursAgo(8),    source_channel: 'ms365_mail',    aggregate_confidence: 0.96 }),
  mkCase('b3c4d5e6', { document_type: { name: 'Bank Statement', version: 2 }, status: 'PROCESSING',     received_at: hoursAgo(0.2),  source_channel: 'google_drive',  aggregate_confidence: null }),
  mkCase('f7a8b9c0', { document_type: { name: 'Driving Licence', version: 1 },status: 'NEEDS_REVIEW',   received_at: hoursAgo(12),   source_channel: 'vendor_portal', aggregate_confidence: 0.68 }),
  mkCase('d1e2f3a4', { document_type: { name: 'Purchase Order', version: 2 }, status: 'AUTO_APPROVED',  received_at: hoursAgo(16),   source_channel: 'rest_upload',   aggregate_confidence: 0.89 }),
  mkCase('b5c6d7e8', { document_type: { name: 'Invoice', version: 3 },        status: 'DUPLICATE',      received_at: hoursAgo(20),   source_channel: 'ms365_mail',    aggregate_confidence: 0.97 }),
  mkCase('11223344', { document_type: { name: 'Lab Report', version: 1 },     status: 'AUTO_APPROVED',  received_at: hoursAgo(28),   source_channel: 'sftp',          aggregate_confidence: 0.93 }),
  mkCase('55667788', { document_type: { name: 'Invoice', version: 3 },        status: 'NEEDS_REVIEW',   received_at: hoursAgo(36),   source_channel: 'ms365_mail',    aggregate_confidence: 0.71, assigned_to: 'Anil Kumar' }),
  mkCase('99aabbcc', { document_type: { name: 'Salary Slip', version: 1 },    status: 'AUTO_APPROVED',  received_at: hoursAgo(40),   source_channel: 'vendor_portal', aggregate_confidence: 0.88 }),
]

// ─── Case detail ─────────────────────────────────────────────────────────────

export const mockCaseDetail = {
  case_id: 'case_8f4e2a1c',
  document_type: { name: 'Invoice', version: 3 },
  status: 'NEEDS_REVIEW',
  received_at: hoursAgo(1),
  source_channel: 'ms365_mail',
  source_identifier: 'ap-invoices@acmecorp.in',
  aggregate_confidence: 0.76,
  assigned_to: 'Sarah Chen',
  document_url: null, // null = use mock renderer; replace with Azure Blob SAS URL in prod
  extraction: {
    model_provider: 'azure_openai',
    model_name: 'gpt-4o',
    tokens_used: 5847,
    cost_usd: 0.0234,
    attempt_number: 1,
    schema_version: 3,
    duration_ms: 8312,
    page_count: 2,
  },
  fields: [
    {
      field_id: 'fld_001',
      name: 'vendor_name',
      display_name: 'Vendor Name',
      value: 'Acme Corp India Pvt Ltd',
      calibrated_confidence: 0.97,
      qa_flag: 'PASS',
      reasoning: 'Found in letterhead at top of page 1. Tax ID immediately below matches vendor_master entry for Acme Corp India Pvt Ltd.',
      page_number: 1,
      masking_mode: 'NONE',
      was_corrected: false,
    },
    {
      field_id: 'fld_002',
      name: 'invoice_number',
      display_name: 'Invoice Number',
      value: 'INV-2026-04521',
      calibrated_confidence: 0.99,
      qa_flag: 'PASS',
      reasoning: "Located in header area top-right of page 1, labeled \"Invoice No.\". Regex validator passed: ^[A-Z0-9-]+$",
      page_number: 1,
      masking_mode: 'NONE',
      was_corrected: false,
    },
    {
      field_id: 'fld_003',
      name: 'invoice_date',
      display_name: 'Invoice Date',
      value: '2026-05-20',
      calibrated_confidence: 0.95,
      qa_flag: 'PASS',
      reasoning: 'Date field adjacent to invoice number. Source DD/MM/YYYY (20/05/2026) normalised to ISO 8601. date_not_future and date_within_90_days validators passed.',
      page_number: 1,
      masking_mode: 'NONE',
      was_corrected: false,
    },
    {
      field_id: 'fld_004',
      name: 'total_amount',
      display_name: 'Total Amount',
      value: '₹12,450.00',
      calibrated_confidence: 0.72,
      qa_flag: 'NEEDS_REVIEW',
      reasoning: 'Math reconciliation: line items ₹11,200 + tax ₹1,250 = ₹12,450 ✓. Confidence below threshold (0.72 < 0.80) — faint print in total area of page 2. Human review recommended.',
      page_number: 2,
      masking_mode: 'NONE',
      was_corrected: false,
    },
    {
      field_id: 'fld_005',
      name: 'tax_amount',
      display_name: 'Tax Amount (GST)',
      value: '₹1,250.00',
      calibrated_confidence: 0.88,
      qa_flag: 'PASS',
      reasoning: 'GST amount (18%) found in tax summary table on page 2. Consistent with total_amount cross-field math reconciliation.',
      page_number: 2,
      masking_mode: 'NONE',
      was_corrected: false,
    },
    {
      field_id: 'fld_006',
      name: 'vendor_tax_id',
      display_name: 'Vendor GSTIN',
      value: 'tok_gstin_8f2a1c',
      calibrated_confidence: 0.94,
      qa_flag: 'PASS',
      reasoning: 'GSTIN in vendor details section top of page 1. Value tokenised per INTERNAL confidentiality policy; raw value in Key Vault.',
      page_number: 1,
      masking_mode: 'TOKENISE',
      was_corrected: false,
    },
    {
      field_id: 'fld_007',
      name: 'payment_terms',
      display_name: 'Payment Terms',
      value: 'Net 30',
      calibrated_confidence: 0.82,
      qa_flag: 'PASS',
      reasoning: '"Net 30" found in footer section. Matches standard terms on file for this vendor in vendor_master.',
      page_number: 2,
      masking_mode: 'NONE',
      was_corrected: false,
    },
  ],
  line_items: [
    {
      line_no: 1,
      description: 'Professional Services — Strategy Consulting (May 2026)',
      hsn_sac: '9983',
      quantity: 5.0,
      unit: 'Days',
      unit_price: 1800.00,
      tax_rate_pct: 18,
      amount: 9000.00,
    },
    {
      line_no: 2,
      description: 'Travel & Accommodation Reimbursement',
      hsn_sac: '9964',
      quantity: 1.0,
      unit: 'Lump',
      unit_price: 2200.00,
      tax_rate_pct: 0,
      amount: 2200.00,
    },
  ],
  visual_elements: [
    { element_id: 'vel_001', element_class: 'stamp',     page_number: 1, confidence: 0.91, attributes_json: { text: 'COMPANY SEAL', color: 'blue' } },
    { element_id: 'vel_002', element_class: 'signature', page_number: 2, confidence: 0.88, attributes_json: { label: 'Authorised Signatory', location: 'bottom-right' } },
    { element_id: 'vel_003', element_class: 'qr_code',   page_number: 1, confidence: 0.99, attributes_json: { decoded: 'UPI:pay?pa=acmecorp@upi', type: 'UPI Payment' } },
  ],
  image_corrections: [
    { step: 'Deskew',    detail: 'Rotated 1.2° to correct tilt' },
    { step: 'Normalise', detail: 'Contrast normalised (brightness +12%)' },
  ],
  audit_trail: [
    { log_id: 'log_001', actor: 'azure_openai/gpt-4o', action: 'extraction_completed',  entity: 'case',               timestamp: hoursAgo(0.8),  detail: 'Extraction completed in 8.3 s — 7 fields extracted.' },
    { log_id: 'log_002', actor: 'system/qa_gate',       action: 'qa_flag_raised',        entity: 'field/total_amount', timestamp: hoursAgo(0.8),  detail: 'Field total_amount flagged: calibrated confidence 0.72 < threshold 0.80.' },
    { log_id: 'log_003', actor: 'system',               action: 'case_status_changed',   entity: 'case',               timestamp: hoursAgo(0.78), detail: 'Status changed PROCESSING → NEEDS_REVIEW.' },
    { log_id: 'log_004', actor: 'Sarah Chen',            action: 'case_viewed',           entity: 'case',               timestamp: hoursAgo(0.5),  detail: 'Case opened for review.' },
  ],
}

// ─── Dashboard metrics ────────────────────────────────────────────────────────

export const mockDashboardStats = {
  cases_today:        142, cases_today_delta:        +18,
  pending_review:      23, pending_review_delta:       +5,
  auto_approved:       89, auto_approved_pct:        62.7,
  avg_confidence:    0.847, avg_confidence_delta:   -0.012,
}

export const mockCasesOverTime = Array.from({ length: 24 }, (_, i) => ({
  hour:           `${String(i).padStart(2, '0')}:00`,
  auto_approved:  Math.floor(4  + Math.random() * 10),
  needs_review:   Math.floor(1  + Math.random() * 5),
  rejected:       Math.floor(0  + Math.random() * 2),
}))

export const mockCasesByStatus = [
  { name: 'Auto-Approved', value: 89,  color: '#22c55e' },
  { name: 'Needs Review',  value: 23,  color: '#f59e0b' },
  { name: 'Processing',    value:  8,  color: '#3b82f6' },
  { name: 'Pending',       value: 12,  color: '#8b5cf6' },
  { name: 'Rejected',      value: 10,  color: '#ef4444' },
]

export const mockLLMCostByProvider = [
  { provider: 'Azure OpenAI',     today: 34.20, week: 239.4, color: '#0ea5e9' },
  { provider: 'Anthropic Claude', today:  8.60, week:  60.2, color: '#7c3aed' },
  { provider: 'Google Gemini',    today:  5.10, week:  35.7, color: '#10b981' },
]

export const mockLatencyData = Array.from({ length: 7 }, (_, i) => ({
  day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
  p50: parseFloat((8.2  + Math.random() * 2).toFixed(1)),
  p95: parseFloat((14.8 + Math.random() * 4).toFixed(1)),
  p99: parseFloat((22.1 + Math.random() * 6).toFixed(1)),
}))

export const mockOpsStats = {
  throughput_per_hour: 18,  throughput_delta: +3,
  p95_latency_s:       14.2, latency_delta:  -1.1,
  llm_cost_today:      47.9, cost_delta:     +4.2,
  error_rate_pct:       0.7, error_delta:    -0.2,
}

export const mockRecentActivity = [
  { id: 'act_1', actor: 'Sarah Chen',    action: 'approved',          case_id: 'case_3d7b9e01', doc_type: 'Bank Statement', time: hoursAgo(0.25) },
  { id: 'act_2', actor: 'System (AI)',   action: 'auto-approved',     case_id: 'case_5e6f7a8b', doc_type: 'Invoice',        time: hoursAgo(0.5)  },
  { id: 'act_3', actor: 'Priya Sharma',  action: 'corrected field',   case_id: 'case_f1a2c3d4', doc_type: 'Passport',       time: hoursAgo(0.75) },
  { id: 'act_4', actor: 'System (AI)',   action: 'flagged for review', case_id: 'case_8f4e2a1c', doc_type: 'Invoice',        time: hoursAgo(1)    },
  { id: 'act_5', actor: 'System (AI)',   action: 'auto-approved',     case_id: 'case_c9d0e1f2', doc_type: 'Invoice',        time: hoursAgo(1.5)  },
  { id: 'act_6', actor: 'Anil Kumar',    action: 'rejected',          case_id: 'case_a1b2c3d4', doc_type: 'Invoice',        time: hoursAgo(2)    },
]
