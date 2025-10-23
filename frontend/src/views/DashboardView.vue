<template>
  <div class="dashboard">
    <h1>欢迎使用自然语言驱动UI测试平台</h1>
    
    <el-row :gutter="20" style="margin-top: 40px">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <el-icon class="stat-icon" color="#409EFF"><Folder /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.projects }}</div>
              <div class="stat-label">项目总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <el-icon class="stat-icon" color="#67C23A"><Document /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.testCases }}</div>
              <div class="stat-label">测试用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <el-icon class="stat-icon" color="#E6A23C"><VideoPlay /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalRuns }}</div>
              <div class="stat-label">执行次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <el-icon class="stat-icon" color="#F56C6C"><CircleCheck /></el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ stats.passRate }}%</div>
              <div class="stat-label">通过率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>我的项目</span>
              <el-button type="primary" size="small" @click="gotoProjects">
                <el-icon><Plus /></el-icon>
                创建项目
              </el-button>
            </div>
          </template>
          <div v-loading="loading">
            <el-table :data="projects" style="width: 100%" @row-click="handleProjectClick">
              <el-table-column prop="name" label="项目名称" width="180" />
              <el-table-column prop="description" label="描述" min-width="150" />
              <el-table-column prop="base_url" label="基础URL" width="200" show-overflow-tooltip />
              <el-table-column prop="llm_provider" label="LLM提供商" width="120" />
              <el-table-column prop="test_case_count" label="测试用例数" width="110" align="center">
                <template #default="{ row }">
                  <el-tag type="info" size="small">{{ row.test_case_count }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="execution_count" label="执行次数" width="100" align="center">
                <template #default="{ row }">
                  <el-tag type="warning" size="small">{{ row.execution_count }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="pass_rate" label="通过率" width="100" align="center">
                <template #default="{ row }">
                  <el-tag 
                    :type="row.pass_rate >= 80 ? 'success' : row.pass_rate >= 60 ? 'warning' : 'danger'" 
                    size="small"
                  >
                    {{ row.pass_rate }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="创建时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link @click.stop="handleProjectClick(row)">
                    查看
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="!loading && projects.length === 0" description="还没有项目，赶快创建一个吧！" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { projectAPI } from '@/api'

const router = useRouter()

const stats = ref({
  projects: 0,
  testCases: 0,
  totalRuns: 0,
  passRate: 0
})

const projects = ref([])
const loading = ref(false)

const gotoProjects = () => {
  router.push('/projects')
}

const handleProjectClick = (row) => {
  router.push(`/projects/${row.id}`)
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadDashboardData = async () => {
  loading.value = true
  try {
    // 加载统计数据
    const statsRes = await projectAPI.getDashboardStats()
    console.log('统计数据响应:', statsRes)
    stats.value = statsRes
    
    // 加载项目列表
    const projectsRes = await projectAPI.list()
    console.log('项目列表响应:', projectsRes)
    projects.value = projectsRes
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard h1 {
  color: #303133;
  margin: 0 0 20px 0;
}

.stat-card {
  cursor: default;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row):hover {
  background-color: #f5f7fa;
}
</style>
