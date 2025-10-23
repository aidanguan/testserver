<template>
  <div class="test-case-history">
    <el-page-header @back="goBack" title="测试执行历史" />

    <el-card v-loading="loading" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <div>
            <span>编号: {{ testCase?.id }} | {{ testCase?.name }} - 历史记录</span>
          </div>
          <el-button type="primary" @click="handleExecute">执行新测试</el-button>
        </div>
      </template>

      <el-table :data="runs" style="width: 100%">
        <el-table-column prop="id" label="运行ID" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="LLM判定" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.llm_verdict" :type="getVerdictType(scope.row.llm_verdict)">
              {{ getVerdictText(scope.row.llm_verdict) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_by" label="触发人" width="100" />
        <el-table-column label="开始时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="结束时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.end_time) || '运行中...' }}
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="scope">
            {{ getDuration(scope.row) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="handleView(scope.row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="runs.length === 0 && !loading" style="text-align: center; padding: 40px; color: #909399;">
        暂无执行记录
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { testCaseAPI, testRunAPI } from '../api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const testCase = ref(null)
const runs = ref([])

const caseId = route.params.id

const loadTestCase = async () => {
  try {
    testCase.value = await testCaseAPI.get(caseId)
  } catch (error) {
    ElMessage.error('加载测试用例失败')
  }
}

const loadRuns = async () => {
  loading.value = true
  try {
    runs.value = await testRunAPI.list({ case_id: caseId })
  } catch (error) {
    ElMessage.error('加载执行历史失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getDuration = (run) => {
  if (!run.start_time) return '-'
  const start = new Date(run.start_time)
  const end = run.end_time ? new Date(run.end_time) : new Date()
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

const handleView = (row) => {
  router.push(`/runs/${row.id}`)
}

const handleExecute = async () => {
  try {
    const result = await testRunAPI.execute(caseId)
    ElMessage.success('测试已开始执行')
    router.push(`/runs/${result.id}`)
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

onMounted(() => {
  loadTestCase()
  loadRuns()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
