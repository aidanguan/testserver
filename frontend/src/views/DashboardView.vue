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
            <span>快速开始</span>
          </template>
          <div class="quick-start">
            <el-button type="primary" @click="gotoProjects">
              <el-icon><Plus /></el-icon>
              创建项目
            </el-button>
            <el-button @click="gotoProjects">
              <el-icon><Document /></el-icon>
              查看项目
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const stats = ref({
  projects: 0,
  testCases: 0,
  totalRuns: 0,
  passRate: 0
})

const gotoProjects = () => {
  router.push('/projects')
}

onMounted(() => {
  // 可以在这里加载实际统计数据
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

.quick-start {
  display: flex;
  gap: 12px;
}
</style>
