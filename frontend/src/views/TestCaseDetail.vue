<template>
  <div class="test-case-detail">
    <el-page-header @back="goBack" :title="testCase?.name || '测试用例详情'" />

    <el-card v-loading="loading" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>用例信息</span>
          <div>
            <el-button type="primary" @click="handleEdit">编辑</el-button>
            <el-button type="warning" @click="showRecordGuide">🎥 录制脚本</el-button>
            <el-button type="success" @click="handleExecute">执行测试</el-button>
            <el-button @click="handleViewHistory">查看历史</el-button>
            <el-button type="danger" @click="handleDelete">删除</el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="用例编号">{{ testCase?.id }}</el-descriptions-item>
        <el-descriptions-item label="用例名称">{{ testCase?.name }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ testCase?.description }}</el-descriptions-item>
        <el-descriptions-item label="自然语言描述">
          <pre style="white-space: pre-wrap; margin: 0;">{{ testCase?.natural_language }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="标准化步骤">
          <div v-if="testCase?.standard_steps">
            <div v-for="(step, index) in testCase.standard_steps" :key="index" style="margin-bottom: 10px;">
              <strong>步骤 {{ index + 1 }}:</strong>
              <ul style="margin: 5px 0 0 20px;">
                <li><strong>动作:</strong> {{ step.action }}</li>
                <li v-if="step.element"><strong>元素:</strong> {{ step.element }}</li>
                <li v-if="step.value"><strong>值:</strong> {{ step.value }}</li>
                <li v-if="step.description"><strong>描述:</strong> {{ step.description }}</li>
              </ul>
            </div>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="预期结果">
          <pre style="white-space: pre-wrap; margin: 0;">{{ testCase?.expected_result }}</pre>
        </el-descriptions-item>
      </el-descriptions>

      <div v-if="testCase?.playwright_script" style="margin-top: 20px;">
        <h3>Playwright 脚本</h3>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto;">{{ JSON.stringify(testCase.playwright_script, null, 2) }}</pre>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑测试用例" width="900px">
      <el-alert
        title="可以手动编辑步骤和脚本，或点击'重新生成脚本'按钮使用 LLM 自动生成"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <el-form :model="editForm" label-width="120px">
        <el-form-item label="用例名称" required>
          <el-input v-model="editForm.name" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        
        <el-form-item label="自然语言描述">
          <el-input v-model="editForm.natural_language" type="textarea" :rows="4" />
        </el-form-item>
        
        <el-form-item label="预期结果">
          <el-input v-model="editForm.expected_result" type="textarea" :rows="3" />
        </el-form-item>

        <el-divider />

        <el-form-item label="标准化步骤">
          <el-input 
            v-model="standardStepsJson" 
            type="textarea" 
            :rows="8"
            placeholder="JSON 格式的标准化步骤"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">
            JSON 格式数组，例如: [{"action": "goto", "value": "https://example.com", "description": "打开页面"}]
          </div>
        </el-form-item>

        <el-form-item label="Playwright 脚本">
          <el-input 
            v-model="playwrightScriptJson" 
            type="textarea" 
            :rows="10"
            placeholder="JSON 格式的 Playwright 脚本"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">
            JSON 格式对象，包含 browser、viewport、steps 等字段
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; justify-content: space-between; width: 100%;">
          <el-button @click="handleRegenerate" :loading="regenerating" type="warning">
            重新生成脚本
          </el-button>
          <div>
            <el-button @click="showEditDialog = false">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">
              {{ saving ? '保存中...' : '保存' }}
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 录制指南对话框 -->
    <el-dialog v-model="showRecordDialog" title="🎥 录制脚本" width="600px">
      <div v-if="!recordingSessionId">
        <el-alert
          title="点击'开始录制'后，系统会打开浏览器窗口"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        />

        <el-form label-width="100px">
          <el-form-item label="目标网址" required>
            <el-input
              v-model="recordTargetUrl"
              placeholder="请输入完整的网站地址（包含 http:// 或 https://）"
              clearable
            />
          </el-form-item>
        </el-form>

        <el-alert type="warning" :closable="false" style="margin-top: 10px;">
          <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
            <li>录制会在服务器上打开浏览器窗口</li>
            <li>如果是远程服务器，需要有桌面环境</li>
            <li>建议在本地环境使用此功能</li>
          </ul>
        </el-alert>
      </div>

      <div v-else>
        <el-result
          icon="success"
          title="正在录制"
          sub-title="请在弹出的浏览器窗口中进行操作"
        >
          <template #extra>
            <el-button type="danger" @click="stopRecording" :loading="stoppingRecord">
              停止录制
            </el-button>
          </template>
        </el-result>

        <el-alert type="info" :closable="false" style="margin-top: 20px;">
          <p style="margin: 0;">操作步骤：</p>
          <ol style="margin: 10px 0 0 0; padding-left: 20px;">
            <li>在浏览器中进行你的测试操作</li>
            <li>Playwright Inspector 会自动记录代码</li>
            <li>操作完成后点击上面的"停止录制"按钮</li>
            <li>系统会自动转换并填充脚本</li>
          </ol>
        </el-alert>
      </div>

      <template #footer>
        <div v-if="!recordingSessionId">
          <el-button @click="showRecordDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="startRecording" 
            :loading="startingRecord"
            :disabled="!recordTargetUrl"
          >
            开始录制
          </el-button>
        </div>
        <div v-else>
          <el-button @click="cancelRecording">取消录制</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { testCaseAPI, testRunAPI, projectAPI } from '../api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const regenerating = ref(false)
const showEditDialog = ref(false)
const showRecordDialog = ref(false)
const startingRecord = ref(false)
const stoppingRecord = ref(false)
const recordingSessionId = ref(null)
const recordTargetUrl = ref('')
const testCase = ref(null)
const project = ref(null) // 项目信息
const editForm = ref({
  name: '',
  description: '',
  natural_language: '',
  expected_result: ''
})
const standardStepsJson = ref('')
const playwrightScriptJson = ref('')

const caseId = route.params.id

const loadTestCase = async () => {
  loading.value = true
  try {
    testCase.value = await testCaseAPI.get(caseId)
    // 加载项目信息（用于获取 base_url）
    if (testCase.value.project_id) {
      project.value = await projectAPI.get(testCase.value.project_id)
    }
  } catch (error) {
    ElMessage.error('加载测试用例失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const handleEdit = (skipScriptReload = false) => {
  editForm.value = {
    name: testCase.value.name,
    description: testCase.value.description,
    natural_language: testCase.value.natural_language,
    expected_result: testCase.value.expected_result
  }
  
  // 将标准化步骤和 Playwright 脚本转为 JSON 字符串以便编辑
  standardStepsJson.value = JSON.stringify(testCase.value.standard_steps, null, 2)
  
  // 如果 skipScriptReload 为 true，不要重新读取 playwright_script（用于录制后保留新脚本）
  if (!skipScriptReload) {
    playwrightScriptJson.value = JSON.stringify(testCase.value.playwright_script, null, 2)
  }
  
  showEditDialog.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    // 解析 JSON 字符串
    let standardSteps
    let playwrightScript
    
    try {
      standardSteps = JSON.parse(standardStepsJson.value)
    } catch (e) {
      ElMessage.error('标准化步骤 JSON 格式错误，请检查')
      return
    }
    
    try {
      playwrightScript = JSON.parse(playwrightScriptJson.value)
    } catch (e) {
      ElMessage.error('Playwright 脚本 JSON 格式错误，请检查')
      return
    }
    
    // 保存所有字段
    const updateData = {
      name: editForm.value.name,
      description: editForm.value.description,
      natural_language: editForm.value.natural_language,
      expected_result: editForm.value.expected_result,
      standard_steps: standardSteps,
      playwright_script: playwrightScript
    }
    
    await testCaseAPI.update(caseId, updateData)
    
    ElMessage.success('保存成功')
    showEditDialog.value = false
    await loadTestCase()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleRegenerate = async () => {
  regenerating.value = true
  try {
    // 第一步：使用 LLM 从自然语言生成标准化步骤
    ElMessage.info('正在使用 LLM 生成测试步骤...')
    const standardCase = await testCaseAPI.generateFromNL(
      testCase.value.project_id,
      editForm.value.natural_language
    )
    
    // 更新标准化步骤到表单
    standardStepsJson.value = JSON.stringify(standardCase.standard_steps, null, 2)
    
    // 临时保存以便生成脚本（包含标准化步骤）
    await testCaseAPI.update(caseId, {
      standard_steps: standardCase.standard_steps
    })
    
    // 第二步：生成 Playwright 脚本
    ElMessage.info('正在生成 Playwright 脚本...')
    const scriptResult = await testCaseAPI.generateScript(caseId)
    
    // 更新 Playwright 脚本到表单
    playwrightScriptJson.value = JSON.stringify(scriptResult.playwright_script, null, 2)
    
    ElMessage.success('脚本重新生成成功，请检查后保存')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成失败')
  } finally {
    regenerating.value = false
  }
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

const handleViewHistory = () => {
  router.push(`/cases/${caseId}/history`)
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例“${testCase.value.name}”吗？删除后将无法恢复！`,
      '警告',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )
    
    await testCaseAPI.delete(caseId)
    ElMessage.success('删除成功')
    // 跳转回项目详情页
    router.push(`/projects/${testCase.value.project_id}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 显示录制指南
const showRecordGuide = () => {
  // 优先从项目 base_url 读取
  if (project.value?.base_url) {
    recordTargetUrl.value = project.value.base_url
  }
  // 其次从自然语言描述中提取
  else if (testCase.value?.natural_language) {
    const urlMatch = testCase.value.natural_language.match(/(https?:\/\/[^\s,、。]+)/)
    if (urlMatch) {
      recordTargetUrl.value = urlMatch[1]
    }
  }
  
  // 如果都没有，留空由用户输入
  if (!recordTargetUrl.value) {
    recordTargetUrl.value = ''
  }
  
  showRecordDialog.value = true
}

// 开始录制
const startRecording = async () => {
  if (!recordTargetUrl.value) {
    ElMessage.error('请输入目标网址')
    return
  }
  
  startingRecord.value = true
  try {
    // 直接使用URL，不再自动添加https://
    const targetUrl = recordTargetUrl.value
    
    const response = await fetch('http://localhost:8000/api/record/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        target_url: targetUrl,
        project_id: testCase.value.project_id
      })
    })
    
    if (!response.ok) {
      throw new Error('启动录制失败')
    }
    
    const data = await response.json()
    recordingSessionId.value = data.session_id
    
    ElMessage.success('录制已启动，请在浏览器窗口中操作')
  } catch (error) {
    ElMessage.error('启动录制失败: ' + error.message)
  } finally {
    startingRecord.value = false
  }
}

// 停止录制
const stopRecording = async () => {
  stoppingRecord.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/record/${recordingSessionId.value}/stop`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error('停止录制失败')
    }
    
    const data = await response.json()
    
    // 自动填充到编辑框
    playwrightScriptJson.value = JSON.stringify(data.playwright_script, null, 2)
    
    ElMessage.success('录制完成，脚本已自动生成，请检查后保存')
    
    // 关闭录制对话框
    showRecordDialog.value = false
    recordingSessionId.value = null
    
    // 自动打开编辑对话框，但不重新加载 playwright_script（保留录制的新脚本）
    handleEdit(true)
  } catch (error) {
    ElMessage.error('停止录制失败: ' + error.message)
  } finally {
    stoppingRecord.value = false
  }
}

// 取消录制
const cancelRecording = async () => {
  if (recordingSessionId.value) {
    await stopRecording()
  }
  showRecordDialog.value = false
  recordingSessionId.value = null
}

onMounted(() => {
  loadTestCase()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

pre {
  font-family: 'Courier New', monospace;
}
</style>
