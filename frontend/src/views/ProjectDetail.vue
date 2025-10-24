<template>
  <div class="project-detail">
    <el-page-header @back="goBack" :title="project?.name || '项目详情'">
      <template #content>
        <div style="display: flex; align-items: center; gap: 10px;">
          <span>{{ project?.description }}</span>
          <el-button 
            v-if="authStore.isAdmin" 
            size="small" 
            type="primary"
            @click="handleEditProject"
          >
            编辑项目
          </el-button>
        </div>
      </template>
    </el-page-header>
    
    <el-tabs v-model="activeTab" style="margin-top: 20px">
      <el-tab-pane label="测试用例" name="cases">
        <div class="tab-header">
          <el-button type="primary" @click="handleCreateCase">
            <el-icon><Plus /></el-icon>
            创建测试用例
          </el-button>
        </div>
        
        <el-table :data="testCases" v-loading="loading" style="margin-top: 20px">
          <el-table-column prop="id" label="编号" width="80" />
          <el-table-column prop="name" label="用例名称" min-width="150" />
          <el-table-column prop="description" label="描述" min-width="150" />
          <el-table-column prop="execution_count" label="执行次数" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="warning" size="small">{{ row.execution_count || 0 }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="pass_rate" label="成功率" width="100" align="center">
            <template #default="{ row }">
              <el-tag 
                :type="row.pass_rate >= 80 ? 'success' : row.pass_rate >= 60 ? 'warning' : 'danger'" 
                size="small"
              >
                {{ row.pass_rate || 0 }}%
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="420" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleViewCase(scope.row)">
                查看
              </el-button>
              <el-button size="small" type="primary" @click="handleExecute(scope.row)">
                执行
              </el-button>
              <el-button size="small" @click="handleViewHistory(scope.row)">
                历史
              </el-button>
              <el-button 
                size="small" 
                type="warning"
                @click="handleEditCase(scope.row)"
              >
                编辑
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="handleDelete(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <el-tab-pane label="项目配置" name="config">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">{{ project?.name }}</el-descriptions-item>
          <el-descriptions-item label="测试站点">{{ project?.base_url }}</el-descriptions-item>
          <el-descriptions-item label="LLM提供商">{{ project?.llm_provider }}</el-descriptions-item>
          <el-descriptions-item label="LLM模型">{{ project?.llm_model }}</el-descriptions-item>
          <el-descriptions-item label="LLM Base URL" v-if="project?.llm_base_url">
            {{ project?.llm_base_url }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 登录状态管理 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <div style="display: flex; align-items: center; justify-content: space-between;">
              <span>🔐 登录状态管理</span>
              <el-tag v-if="authStateInfo.exists" type="success" size="small">已保存</el-tag>
              <el-tag v-else type="info" size="small">未配置</el-tag>
            </div>
          </template>
          
          <!-- 已有认证状态 -->
          <div v-if="authStateInfo.exists">
            <el-descriptions :column="2" size="small" border>
              <el-descriptions-item label="Cookies 数量">
                {{ authStateInfo.cookies_count }}
              </el-descriptions-item>
              <el-descriptions-item label="域名数量">
                {{ authStateInfo.origins_count }}
              </el-descriptions-item>
              <el-descriptions-item label="文件大小">
                {{ (authStateInfo.file_size / 1024).toFixed(2) }} KB
              </el-descriptions-item>
              <el-descriptions-item label="更新时间">
                {{ formatTime(authStateInfo.modified_time) }}
              </el-descriptions-item>
            </el-descriptions>
            
            <div style="margin-top: 15px; display: flex; gap: 10px;">
              <el-button 
                type="warning" 
                size="small"
                @click="handleUpdateAuthState"
                :loading="authStateLoading"
              >
                🔄 更新登录状态
              </el-button>
              <el-button 
                type="danger" 
                size="small"
                @click="handleDeleteAuthState"
                :loading="authStateLoading"
              >
                🗑️ 删除登录状态
              </el-button>
            </div>
          </div>
          
          <!-- 未有认证状态 -->
          <div v-else>
            <el-alert
              title="提示"
              type="info"
              :closable="false"
              style="margin-bottom: 15px"
            >
              保存登录状态后，测试用例执行时将自动加载登录信息，无需每次都重新登录。
            </el-alert>
            
            <el-button 
              type="primary" 
              @click="handleCreateAuthState"
              :loading="authStateLoading"
            >
              🔑 创建登录状态
            </el-button>
          </div>
          
          <!-- 浏览器会话状态 -->
          <div v-if="browserSessionActive" style="margin-top: 15px;">
            <el-alert
              title="浏览器已打开"
              type="success"
              :closable="false"
            >
              请在浏览器中完成登录操作，然后点击下方的“保存登录状态”按钮。
            </el-alert>
            
            <div style="margin-top: 10px; display: flex; gap: 10px;">
              <el-button 
                type="success" 
                @click="handleSaveSession"
                :loading="authStateLoading"
              >
                💾 保存登录状态
              </el-button>
              <el-button 
                @click="handleCancelSession"
                :loading="authStateLoading"
              >
                ❌ 取消
              </el-button>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 创建测试用例页面 -->
    <TestCaseDialog 
      v-if="createDialogVisible"
      v-model="createDialogVisible"
      :project-id="projectId"
      @success="handleCreateSuccess"
    />
    
    <!-- 编辑测试用例弹窗 -->
    <TestCaseEditDialog 
      v-model="editDialogVisible"
      :case-data="editingCase"
      :project-id="projectId"
      @success="handleEditSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useProjectStore } from '../stores/project'
import { useAuthStore } from '../stores/auth'
import { testCaseAPI, testRunAPI, authStateAPI } from '../api'
import TestCaseEditDialog from '../components/TestCaseEditDialog.vue'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const authStore = useAuthStore()

const loading = ref(false)
const activeTab = ref('cases')
const project = ref(null)
const testCases = ref([])

const projectId = route.params.id

// 编辑相关状态
const editDialogVisible = ref(false)
const editingCase = ref(null)

// 认证状态管理
const authStateInfo = ref({
  exists: false,
  file_path: '',
  cookies_count: 0,
  origins_count: 0,
  file_size: 0,
  modified_time: 0
})
const authStateLoading = ref(false)
const browserSessionActive = ref(false)
let sessionCheckInterval = null

const loadProject = async () => {
  try {
    project.value = await projectStore.fetchProject(projectId)
  } catch (error) {
    ElMessage.error('加载项目失败')
  }
}

const loadTestCases = async () => {
  loading.value = true
  try {
    testCases.value = await testCaseAPI.listByProject(projectId)
  } catch (error) {
    ElMessage.error('加载测试用例失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const handleCreateCase = () => {
  router.push(`/projects/${projectId}/cases/create`)
}

const handleViewCase = (row) => {
  router.push(`/cases/${row.id}`)
}

const handleExecute = async (row) => {
  try {
    const result = await testRunAPI.execute(row.id)
    ElMessage.success('测试已开始执行')
    router.push(`/runs/${result.id}`)
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

const handleEditProject = () => {
  // 跳转到项目列表页，触发编辑
  router.push(`/projects?edit=${projectId}`)
}

const handleViewHistory = (row) => {
  // 跳转到测试历史页面
  router.push(`/cases/${row.id}/history`)
}

const handleEditCase = (row) => {
  editingCase.value = row
  editDialogVisible.value = true
}

const handleEditSuccess = async () => {
  editDialogVisible.value = false
  await loadTestCases()
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例"${row.name}"吗？删除后将无法恢复！`,
      '警告',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )
    
    await testCaseAPI.delete(row.id)
    ElMessage.success('删除成功')
    await loadTestCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 认证状态管理函数
const loadAuthStateInfo = async () => {
  try {
    const info = await authStateAPI.getInfo(projectId)
    authStateInfo.value = info
  } catch (error) {
    console.error('加载认证状态失败:', error)
  }
}

const checkSessionStatus = async () => {
  try {
    const status = await authStateAPI.getSessionStatus(projectId)
    browserSessionActive.value = status.has_session
  } catch (error) {
    console.error('检查会话状态失败:', error)
  }
}

const handleCreateAuthState = async () => {
  // 使用项目的 base_url 作为默认登录 URL
  const loginUrl = project.value?.base_url || ''
  
  if (!loginUrl) {
    ElMessage.error('请先配置项目的测试站点 URL')
    return
  }
  
  authStateLoading.value = true
  try {
    const result = await authStateAPI.createSession(projectId, loginUrl)
    
    if (result.success) {
      ElMessage.success(result.message)
      // 开始轮询会话状态
      startSessionCheck()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '启动失败')
  } finally {
    authStateLoading.value = false
  }
}

const handleUpdateAuthState = async () => {
  // 更新与创建用同样的逻辑
  await handleCreateAuthState()
}

const handleSaveSession = async () => {
  authStateLoading.value = true
  try {
    console.log('🔵 开始保存登录状态，项目ID:', projectId)
    const result = await authStateAPI.saveSession(projectId)
    console.log('🔵 保存结果:', result)
    
    if (result.success) {
      ElMessage.success(result.message)
      browserSessionActive.value = false
      stopSessionCheck()
      await loadAuthStateInfo()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('❌ 保存登录状态失败:', error)
    console.error('❌ 错误详情:', {
      message: error.message,
      response: error.response,
      status: error.response?.status,
      data: error.response?.data
    })
    
    // 显示更详细的错误信息
    const errorMsg = error.response?.data?.detail || error.message || '保存失败'
    ElMessage.error({
      message: `保存失败: ${errorMsg}`,
      duration: 5000,
      showClose: true
    })
  } finally {
    authStateLoading.value = false
  }
}

const handleCancelSession = async () => {
  authStateLoading.value = true
  try {
    const result = await authStateAPI.cancelSession(projectId)
    
    if (result.success) {
      ElMessage.success(result.message)
      browserSessionActive.value = false
      stopSessionCheck()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '取消失败')
  } finally {
    authStateLoading.value = false
  }
}

const handleDeleteAuthState = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除保存的登录状态吗？删除后需要重新登录。',
      '警告',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )
    
    authStateLoading.value = true
    const result = await authStateAPI.delete(projectId)
    
    if (result.success) {
      ElMessage.success(result.message)
      await loadAuthStateInfo()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  } finally {
    authStateLoading.value = false
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

const startSessionCheck = () => {
  // 每 2 秒检查一次会话状态
  sessionCheckInterval = setInterval(checkSessionStatus, 2000)
}

const stopSessionCheck = () => {
  if (sessionCheckInterval) {
    clearInterval(sessionCheckInterval)
    sessionCheckInterval = null
  }
}

onMounted(() => {
  loadProject()
  loadTestCases()
  loadAuthStateInfo()
  checkSessionStatus()
})

onUnmounted(() => {
  stopSessionCheck()
})
</script>

<style scoped>
.tab-header {
  display: flex;
  justify-content: flex-end;
}
</style>
