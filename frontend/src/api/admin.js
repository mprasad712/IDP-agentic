import api from './auth'
import { mockDocumentTypes, mockUsers } from '../mock/data'

const USE_MOCK = true
const fakeDelay = (ms = 400) => new Promise((r) => setTimeout(r, ms))

export const adminApi = {
  // ─── Document types ────────────────────────────────────────────────────────
  listDocumentTypes: async () => {
    if (USE_MOCK) { await fakeDelay(); return mockDocumentTypes }
    return api.get('/admin/document-types').then((r) => r.data)
  },

  createDocumentType: async (data) => {
    if (USE_MOCK) {
      await fakeDelay(600)
      return { ...data, doc_type_id: `dt_${Date.now()}`, version: 1, status: 'DRAFT', fields_count: 0, published_at: null }
    }
    return api.post('/admin/document-types', data).then((r) => r.data)
  },

  updateDocumentType: async (id, data) => {
    if (USE_MOCK) { await fakeDelay(600); return { doc_type_id: id, ...data } }
    return api.put(`/admin/document-types/${id}`, data).then((r) => r.data)
  },

  publishDocumentType: async (id) => {
    if (USE_MOCK) {
      await fakeDelay(800)
      return { doc_type_id: id, status: 'PUBLISHED', published_at: new Date().toISOString() }
    }
    return api.post(`/admin/document-types/${id}/publish`).then((r) => r.data)
  },

  // ─── Users ─────────────────────────────────────────────────────────────────
  listUsers: async () => {
    if (USE_MOCK) { await fakeDelay(); return mockUsers }
    return api.get('/admin/users').then((r) => r.data)
  },

  updateUserRole: async (userId, role) => {
    if (USE_MOCK) { await fakeDelay(500); return { user_id: userId, role } }
    return api.put(`/admin/users/${userId}/role`, { role }).then((r) => r.data)
  },

  toggleUserActive: async (userId, is_active) => {
    if (USE_MOCK) { await fakeDelay(500); return { user_id: userId, is_active } }
    return api.put(`/admin/users/${userId}/active`, { is_active }).then((r) => r.data)
  },

  inviteUser: async (data) => {
    if (USE_MOCK) {
      await fakeDelay(800)
      return {
        user_id: `usr_${Date.now()}`,
        ...data,
        is_active: true,
        last_login_at: null,
        jit_provisioned: true,
      }
    }
    return api.post('/admin/users/invite', data).then((r) => r.data)
  },
}
