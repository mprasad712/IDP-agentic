import api from './auth'
import {
  mockDashboardStats, mockCasesOverTime, mockCasesByStatus,
  mockLLMCostByProvider, mockLatencyData, mockOpsStats, mockRecentActivity,
} from '../mock/data'

const USE_MOCK = true
const fakeDelay = (ms = 300) => new Promise((r) => setTimeout(r, ms))

export const metricsApi = {
  dashboardStats: async () => {
    if (USE_MOCK) { await fakeDelay(); return mockDashboardStats }
    return api.get('/metrics/dashboard').then((r) => r.data)
  },

  casesOverTime: async () => {
    if (USE_MOCK) { await fakeDelay(); return mockCasesOverTime }
    return api.get('/metrics/cases-over-time').then((r) => r.data)
  },

  casesByStatus: async () => {
    if (USE_MOCK) { await fakeDelay(); return mockCasesByStatus }
    return api.get('/metrics/cases-by-status').then((r) => r.data)
  },

  llmCost: async () => {
    if (USE_MOCK) { await fakeDelay(); return mockLLMCostByProvider }
    return api.get('/metrics/llm-cost').then((r) => r.data)
  },

  latency: async () => {
    if (USE_MOCK) { await fakeDelay(); return mockLatencyData }
    return api.get('/metrics/latency').then((r) => r.data)
  },

  opsStats: async () => {
    if (USE_MOCK) { await fakeDelay(); return mockOpsStats }
    return api.get('/metrics/ops').then((r) => r.data)
  },

  recentActivity: async () => {
    if (USE_MOCK) { await fakeDelay(); return mockRecentActivity }
    return api.get('/metrics/activity').then((r) => r.data)
  },
}
