<template>
  <div class="test-run-detail">
    <el-page-header @back="goBack" title="测试运行详情" />

    <el-card v-loading="loading" style="margin-top: 20px">
      <!-- 运行基本信息 -->
      <div class="run-header">
        <div class="run-info">
          <h2>{{ runDetail.test_case?.name }}</h2>
          <p>{{ runDetail.test_case?.description }}</p>
        </div>
        <div class="run-status">
          <el-tag :type="getStatusType(runDetail.status)" size="large">
            {{ getStatusText(runDetail.status) }}
          </el-tag>
        </div>
      </div>

      <el-descriptions :column="3" border style="margin-top: 20px">
        <el-descriptions-item label="运行ID">{{ runDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="触发人">{{ runDetail.trigger_by }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">
          {{ formatDate(runDetail.start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间">
          {{ formatDate(runDetail.end_time) || '运行中...' }}
        </el-descriptions-item>
        <el-descriptions-item label="执行时长">
          {{ getDuration() }}
        </el-descriptions-item>
        <el-descriptions-item label="LLM判定" v-if="runDetail.llm_verdict">
          <el-tag :type="getVerdictType(runDetail.llm_verdict)">
            {{ getVerdictText(runDetail.llm_verdict) }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- LLM判定理由 -->
      <el-alert
        v-if="runDetail.llm_reason"
        :title="`LLM判定理由`"
        :type="getVerdictType(runDetail.llm_verdict)"
        :closable="false"
        style="margin-top: 20px"
      >
        <template #default>
          <p style="white-space: pre-wrap">{{ runDetail.llm_reason }}</p>
        </template>
      </el-alert>

      <!-- 错误信息 -->
      <el-alert
        v-if="runDetail.error_message"
        title="错误信息"
        type="error"
        :closable="false"
        style="margin-top: 20px"
      >
        <template #default>
          <pre>{{ runDetail.error_message }}</pre>
        </template>
      </el-alert>

      <!-- 步骤执行时间线 -->
      <div style="margin-top: 30px">
        <h3>执行步骤</h3>
        <el-timeline style="margin-top: 20px">
          <el-timeline-item
            v-for="step in runDetail.steps"
            :key="step.id"
            :color="getStepColor(step.status)"
            :timestamp="formatDate(step.start_time)"
          >
            <el-card>
              <div class="step-header">
                <div>
                  <span class="step-index">步骤 {{ step.step_index }}</span>
                  <span class="step-desc">{{ step.step_description }}</span>
                </div>
                <el-tag :type="getStepStatusType(step.status)" size="small">
                  {{ getStepStatusText(step.status) }}
                </el-tag>
              </div>

              <!-- 截图 -->
              <div v-if="step.screenshot_path" class="screenshot-container">
                <img :src="getScreenshotUrl(step.screenshot_path)" alt="步骤截图" />
              </div>

              <!-- 错误信息 -->
              <el-alert
                v-if="step.error_message"
                type="error"
                :closable="false"
                style="margin-top: 10px"
              >
                <pre>{{ step.error_message }}</pre>
              </el-alert>

              <div class="step-footer">
                <span>耗时: {{ getStepDuration(step) }}</span>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { testRunAPI } from '../api'

const route = useRoute()
const router = useRouter()

const runId = route.params.id
const loading = ref(false)
const runDetail = ref({
  test_case: {},
  steps: []
})

const goBack = () => {
  router.back()
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getDuration = () => {
  if (!runDetail.value.start_time) return '-'
  const start = new Date(runDetail.value.start_time)
  const end = runDetail.value.end_time
    ? new Date(runDetail.value.end_time)
    : new Date()
  const diff = Math.floor((end - start) / 1000)
  return `${diff}秒`
}

const getStepDuration = (step) => {
  if (!step.start_time || !step.end_time) return '-'
  const start = new Date(step.start_time)
  const end = new Date(step.end_time)
  const diff = Math.floor((end - start) / 1000)
  return `${diff}秒`
}

const getStatusType = (status) => {
  const typeMap = {
    running: 'info',
    success: 'success',
    failed: 'warning',
    error: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    running: '运行中',
    success: '成功',
    failed: '失败',
    error: '错误'
  }
  return textMap[status] || status
}

const getVerdictType = (verdict) => {
  const typeMap = {
    passed: 'success',
    failed: 'error',
    unknown: 'warning'
  }
  return typeMap[verdict] || 'info'
}

const getVerdictText = (verdict) => {
  const textMap = {
    passed: '通过',
    failed: '失败',
    unknown: '未知'
  }
  return textMap[verdict] || verdict
}

const getStepColor = (status) => {
  const colorMap = {
    success: '#67C23A',
    failed: '#F56C6C',
    skipped: '#909399'
  }
  return colorMap[status] || '#409EFF'
}

const getStepStatusType = (status) => {
  const typeMap = {
    success: 'success',
    failed: 'danger',
    skipped: 'info'
  }
  return typeMap[status] || 'info'
}

const getStepStatusText = (status) => {
  const textMap = {
    success: '成功',
    failed: '失败',
    skipped: '跳过'
  }
  return textMap[status] || status
}

const getScreenshotUrl = (path) => {
  if (!path) return ''
  
  // 处理路径：移除 ../artifacts 前缀，将反斜杠改为正斜杠
  let cleanPath = path.replace(/\\/g, '/')  // 将反斜杠改为正斜杠
  cleanPath = cleanPath.replace('../artifacts/', '')  // 移除 ../artifacts/ 前缀
  cleanPath = cleanPath.replace(/^\//, '')  // 移除开头的斜杠
  
  // 返回完整的 URL
  return `http://localhost:8000/artifacts/${cleanPath}`
}

const loadRunDetail = async () => {
  loading.value = true
  try {
    runDetail.value = await testRunAPI.get(runId)
  } catch (error) {
    ElMessage.error('加载运行详情失败')
  } finally {
    loading.value = false
  }
}

// 轮询检查运行状态
let pollTimer = null
const startPolling = () => {
  pollTimer = setInterval(async () => {
    if (runDetail.value.status === 'running') {
      await loadRunDetail()
    } else {
      stopPolling()
    }
  }, 3000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onMounted(async () => {
  await loadRunDetail()
  if (runDetail.value.status === 'running') {
    startPolling()
  }
})

// 组件卸载时停止轮询
import { onUnmounted } from 'vue'
onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.run-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.run-info h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.run-info p {
  margin: 0;
  color: #606266;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.step-index {
  font-weight: bold;
  margin-right: 10px;
  color: #409EFF;
}

.step-desc {
  color: #303133;
}

.screenshot-container {
  margin-top: 15px;
  text-align: center;
}

.screenshot-container img {
  max-width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.step-footer {
  margin-top: 10px;
  color: #909399;
  font-size: 12px;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
