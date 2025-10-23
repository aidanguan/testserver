<template>
  <div class="project-list">
    <div class="page-header">
      <h2>项目管理</h2>
      <el-button
        v-if="authStore.isAdmin"
        type="primary"
        @click="showCreateDialog = true"
      >
        <el-icon><Plus /></el-icon>
        创建项目
      </el-button>
    </div>
    
    <el-table
      :data="projects"
      v-loading="loading"
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="name" label="项目名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="base_url" label="测试站点" />
      <el-table-column prop="llm_provider" label="LLM提供商" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button
            size="small"
            @click="handleView(scope.row)"
          >
            查看
          </el-button>
          <el-button
            v-if="authStore.isAdmin"
            size="small"
            type="danger"
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建项目"
      width="600px"
    >
      <el-form
        ref="projectFormRef"
        :model="projectForm"
        label-width="120px"
      >
        <el-form-item label="项目名称" required>
          <el-input v-model="projectForm.name" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input v-model="projectForm.description" type="textarea" />
        </el-form-item>
        
        <el-form-item label="测试站点URL" required>
          <el-input v-model="projectForm.base_url" placeholder="https://example.com" />
        </el-form-item>
        
        <el-form-item label="LLM提供商" required>
          <el-select v-model="projectForm.llm_provider" style="width: 100%">
            <el-option label="OpenAI" value="openai" />
            <el-option label="OpenAI Completion API" value="openai-completion" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="阿里云百炼 (DashScope)" value="dashscope" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="模型名称" required>
          <el-input v-model="projectForm.llm_model" placeholder="gpt-4 / qwen-plus / claude-3" />
        </el-form-item>
        
        <el-form-item label="API密钥" required>
          <el-input v-model="projectForm.llm_api_key" type="password" show-password />
        </el-form-item>
        
        <el-form-item label="API Base URL" prop="llm_base_url">
          <el-input 
            v-model="projectForm.llm_base_url" 
            placeholder="可选，留空使用默认值（如 https://api.openai.com/v1）" 
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">
            百炼默认: https://dashscope.aliyuncs.com/compatible-mode/v1
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjectStore } from '../stores/project'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const projectStore = useProjectStore()
const authStore = useAuthStore()

const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const projectFormRef = ref()

const projects = ref([])

const projectForm = reactive({
  name: '',
  description: '',
  base_url: '',
  llm_provider: 'openai',
  llm_model: 'gpt-4',
  llm_api_key: '',
  llm_base_url: ''
})

const loadProjects = async () => {
  loading.value = true
  try {
    projects.value = await projectStore.fetchProjects()
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  creating.value = true
  try {
    await projectStore.createProject(projectForm)
    ElMessage.success('项目创建成功')
    showCreateDialog.value = false
    Object.assign(projectForm, {
      name: '',
      description: '',
      base_url: '',
      llm_provider: 'openai',
      llm_model: 'gpt-4',
      llm_api_key: '',
      llm_base_url: ''
    })
    await loadProjects()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

const handleView = (row) => {
  router.push(`/projects/${row.id}`)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除此项目吗?', '警告', {
      type: 'warning'
    })
    
    await projectStore.deleteProject(row.id)
    ElMessage.success('删除成功')
    await loadProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}
</style>
