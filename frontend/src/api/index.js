/**
 * 认证相关API
 */
import apiClient from './client'

export const authAPI = {
  // 登录
  login(username, password) {
    return apiClient.post('/auth/login', { username, password })
  },
  
  // 登出
  logout() {
    return apiClient.post('/auth/logout')
  },
  
  // 获取当前用户信息
  getCurrentUser() {
    return apiClient.get('/auth/current')
  }
}

/**
 * 项目相关API
 */
export const projectAPI = {
  // 获取项目列表
  list() {
    return apiClient.get('/projects')
  },
  
  // 获取项目详情
  get(id) {
    return apiClient.get(`/projects/${id}`)
  },
  
  // 创建项目
  create(data) {
    return apiClient.post('/projects', data)
  },
  
  // 更新项目
  update(id, data) {
    return apiClient.put(`/projects/${id}`, data)
  },
  
  // 删除项目
  delete(id) {
    return apiClient.delete(`/projects/${id}`)
  },
  
  // 获取仪表盘统计数据
  getDashboardStats() {
    return apiClient.get('/projects/stats/dashboard')
  }
}

/**
 * 测试用例相关API
 */
export const testCaseAPI = {
  // 获取项目的测试用例列表
  listByProject(projectId) {
    return apiClient.get(`/projects/${projectId}/cases`)
  },
  
  // 获取用例详情
  get(id) {
    return apiClient.get(`/cases/${id}`)
  },
  
  // 创建用例
  create(projectId, data) {
    return apiClient.post(`/projects/${projectId}/cases`, data)
  },
  
  // 更新用例
  update(id, data) {
    return apiClient.put(`/cases/${id}`, data)
  },
  
  // 删除用例
  delete(id) {
    return apiClient.delete(`/cases/${id}`)
  },
  
  // 从自然语言生成用例
  generateFromNL(projectId, naturalLanguage) {
    return apiClient.post('/cases/generate-from-nl', {
      project_id: projectId,
      natural_language: naturalLanguage
    })
  },
  
  // 生成Playwright脚本
  generateScript(testCaseId) {
    return apiClient.post('/cases/generate-script', {
      test_case_id: testCaseId
    })
  }
}

/**
 * 测试执行相关API
 */
export const testRunAPI = {
  // 执行测试用例
  execute(caseId) {
    return apiClient.post(`/cases/${caseId}/execute`)
  },
  
  // 获取运行详情
  get(runId) {
    return apiClient.get(`/runs/${runId}`)
  },
  
  // 获取运行列表
  list(params) {
    return apiClient.get('/runs', { params })
  },
  
  // 获取步骤执行记录
  getSteps(runId) {
    return apiClient.get(`/runs/${runId}/steps`)
  }
}

/**
 * 用户管理相关API
 */
export const userAPI = {
  // 获取用户列表
  list() {
    return apiClient.get('/users')
  },
  
  // 创建用户
  create(data) {
    return apiClient.post('/users', data)
  },
  
  // 更新用户
  update(id, data) {
    return apiClient.put(`/users/${id}`, data)
  },
  
  // 删除用户
  delete(id) {
    return apiClient.delete(`/users/${id}`)
  }
}
