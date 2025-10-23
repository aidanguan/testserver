/**
 * 项目状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectAPI } from '../api'

export const useProjectStore = defineStore('project', () => {
  const projects = ref([])
  const currentProject = ref(null)
  
  // 获取项目列表
  async function fetchProjects() {
    const data = await projectAPI.list()
    projects.value = data
    return data
  }
  
  // 获取项目详情
  async function fetchProject(id) {
    const data = await projectAPI.get(id)
    currentProject.value = data
    return data
  }
  
  // 创建项目
  async function createProject(projectData) {
    const data = await projectAPI.create(projectData)
    projects.value.push(data)
    return data
  }
  
  // 更新项目
  async function updateProject(id, projectData) {
    const data = await projectAPI.update(id, projectData)
    const index = projects.value.findIndex(p => p.id === id)
    if (index !== -1) {
      projects.value[index] = data
    }
    if (currentProject.value?.id === id) {
      currentProject.value = data
    }
    return data
  }
  
  // 删除项目
  async function deleteProject(id) {
    await projectAPI.delete(id)
    projects.value = projects.value.filter(p => p.id !== id)
    if (currentProject.value?.id === id) {
      currentProject.value = null
    }
  }
  
  return {
    projects,
    currentProject,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject
  }
})
