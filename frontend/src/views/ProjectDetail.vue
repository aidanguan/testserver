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
          <el-table-column label="操作" width="350" fixed="right">
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
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjectStore } from '../stores/project'
import { useAuthStore } from '../stores/auth'
import { testCaseAPI, testRunAPI } from '../api'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const authStore = useAuthStore()

const loading = ref(false)
const activeTab = ref('cases')
const project = ref(null)
const testCases = ref([])

const projectId = route.params.id

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

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例“${row.name}”吗？删除后将无法恢复！`,
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

onMounted(() => {
  loadProject()
  loadTestCases()
})
</script>

<style scoped>
.tab-header {
  display: flex;
  justify-content: flex-end;
}
</style>
