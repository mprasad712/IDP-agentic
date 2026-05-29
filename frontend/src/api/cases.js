import api from './auth'
import { mockCases, mockCaseDetail } from '../mock/data'

// TODO: set USE_MOCK=false once backend case endpoints are implemented
const USE_MOCK = true
const fakeDelay = (ms = 400) => new Promise((r) => setTimeout(r, ms))

export const casesApi = {
  list: async ({ status, docType, search, page = 1, pageSize = 15 } = {}) => {
    if (USE_MOCK) {
      await fakeDelay()
      let results = [...mockCases]
      if (status?.length)  results = results.filter((c) => status.includes(c.status))
      if (docType)         results = results.filter((c) => c.document_type.name === docType)
      if (search)          results = results.filter((c) =>
        c.case_id.includes(search.toLowerCase()) ||
        c.document_type.name.toLowerCase().includes(search.toLowerCase())
      )
      const total  = results.length
      const sliced = results.slice((page - 1) * pageSize, page * pageSize)
      return { data: sliced, total, page, pageSize, totalPages: Math.ceil(total / pageSize) }
    }
    return api.get('/cases', { params: { status, docType, search, page, pageSize } }).then((r) => r.data)
  },

  getById: async (id) => {
    if (USE_MOCK) {
      await fakeDelay(600)
      if (id === mockCaseDetail.case_id) return mockCaseDetail
      const base = mockCases.find((c) => c.case_id === id)
      if (!base) throw new Error('Case not found')
      return { ...mockCaseDetail, ...base }
    }
    return api.get(`/cases/${id}`).then((r) => r.data)
  },

  approve: async (id) => {
    if (USE_MOCK) { await fakeDelay(800); return { case_id: id, status: 'AUTO_APPROVED' } }
    return api.post(`/cases/${id}/approve`).then((r) => r.data)
  },

  reject: async (id, reason) => {
    if (USE_MOCK) { await fakeDelay(800); return { case_id: id, status: 'REJECTED', reason } }
    return api.post(`/cases/${id}/reject`, { reason }).then((r) => r.data)
  },

  correctField: async (caseId, fieldId, newValue) => {
    if (USE_MOCK) { await fakeDelay(500); return { field_id: fieldId, value: newValue, was_corrected: true } }
    return api.post(`/cases/${caseId}/fields/${fieldId}/correct`, { value: newValue }).then((r) => r.data)
  },

  retry: async (id) => {
    if (USE_MOCK) { await fakeDelay(1000); return { case_id: id, status: 'PROCESSING' } }
    return api.post(`/cases/${id}/retry`).then((r) => r.data)
  },

  upload: async (file) => {
    if (USE_MOCK) {
      await fakeDelay(1600)
      const caseId = `case_${Math.random().toString(36).slice(2, 10)}`
      return {
        case_id: caseId,
        status: 'PROCESSING',
        document_type: { name: 'Invoice', version: 3 },
        received_at: new Date().toISOString(),
        source_channel: 'rest_upload',
      }
    }
    const fd = new FormData()
    fd.append('file', file)
    return api.post('/cases/upload', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },
}
