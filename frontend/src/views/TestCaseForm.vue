<template>
  <div class="test-case-form">
    <el-page-header @back="goBack" title="创建测试用例" />

    <el-card style="margin-top: 20px">
      <el-steps :active="currentStep" finish-status="success" style="margin-bottom: 30px">
        <el-step title="输入描述" />
        <el-step title="生成用例" />
        <el-step title="生成脚本" />
        <el-step title="完成" />
      </el-steps>

      <!-- 步骤1: 自然语言输入 -->
      <div v-if="currentStep === 0">
        <h3>使用自然语言描述你的测试场景</h3>
        <el-form :model="form" label-width="120px" style="margin-top: 20px">
          <el-form-item label="测试描述">
            <el-input
              v-model="form.naturalLanguage"
              type="textarea"
              :rows="6"
              placeholder="例如：访问登录页面，输入用户名admin和密码admin，点击登录按钮，验证成功跳转到主页"
            />
          </el-form-item>
        </el-form>

        <div style="text-align: right">
          <el-button @click="goBack">取消</el-button>
          <el-button
            type="primary"
            :loading="generating"
            :disabled="!form.naturalLanguage"
            @click="generateTestCase"
          >
            下一步：生成用例
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 查看和编辑生成的用例 -->
      <div v-if="currentStep === 1">
        <h3>生成的测试用例</h3>
        <el-form :model="generatedCase" label-width="120px" style="margin-top: 20px">
          <el-form-item label="用例名称">
            <el-input v-model="generatedCase.name" />
          </el-form-item>

          <el-form-item label="用例描述">
            <el-input v-model="generatedCase.description" type="textarea" :rows="2" />
          </el-form-item>

          <el-form-item label="预期结果">
            <el-input v-model="generatedCase.expected_result" type="textarea" :rows="2" />
          </el-form-item>

          <el-form-item label="测试步骤">
            <el-table :data="generatedCase.standard_steps" border>
              <el-table-column prop="index" label="序号" width="80" />
              <el-table-column prop="action" label="操作" width="120" />
              <el-table-column prop="description" label="描述" />
              <el-table-column prop="selector" label="选择器" width="150" />
              <el-table-column prop="value" label="值" width="120" />
            </el-table>
          </el-form-item>
        </el-form>

        <div style="text-align: right">
          <el-button @click="currentStep = 0">上一步</el-button>
          <el-button type="primary" :loading="generating" @click="generateScript">
            下一步：生成脚本
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 生成脚本 -->
      <div v-if="currentStep === 2">
        <div v-if="!scriptGenerated">
          <h3>选择生成方式</h3>
          <div style="margin-top: 20px; display: flex; gap: 20px; justify-content: center;">
            <el-card shadow="hover" style="width: 300px; cursor: pointer;" @click="generateScriptByLLM">
              <template #header>
                <div style="text-align: center;">
                  <el-icon :size="40" color="#409EFF"><MagicStick /></el-icon>
                </div>
              </template>
              <div style="text-align: center;">
                <h4>自动生成</h4>
                <p style="color: #909399; font-size: 14px;">使用AI根据测试步骤自动生成脚本</p>
                <el-button type="primary" :loading="generating" style="margin-top: 10px;">
                  开始生成
                </el-button>
              </div>
            </el-card>

            <el-card shadow="hover" style="width: 300px; cursor: pointer;" @click="handleShowRecordDialog">
              <template #header>
                <div style="text-align: center;">
                  <el-icon :size="40" color="#67C23A"><VideoCamera /></el-icon>
                </div>
              </template>
              <div style="text-align: center;">
                <h4>手工录制</h4>
                <p style="color: #909399; font-size: 14px;">通过实际操作网站来录制脚本</p>
                <el-button type="success" style="margin-top: 10px;">
                  开始录制
                </el-button>
              </div>
            </el-card>
          </div>
        </div>

        <div v-else>
          <h3>生成的Playwright脚本</h3>
          <el-form label-width="120px" style="margin-top: 20px">
            <el-form-item label="浏览器类型">
              <el-input v-model="generatedScript.browser" disabled />
            </el-form-item>

            <el-form-item label="视口尺寸">
              <el-input
                :value="`${generatedScript.viewport?.width} x ${generatedScript.viewport?.height}`"
                disabled
              />
            </el-form-item>

            <el-form-item label="执行步骤">
              <el-table :data="generatedScript.steps" border>
                <el-table-column prop="index" label="序号" width="80" />
                <el-table-column prop="action" label="操作" width="120" />
                <el-table-column prop="description" label="描述" />
                <el-table-column prop="selector" label="选择器" width="150" />
                <el-table-column prop="value" label="值" width="120" />
                <el-table-column prop="screenshot" label="截屏" width="80">
                  <template #default="scope">
                    <el-tag :type="scope.row.screenshot ? 'success' : 'info'" size="small">
                      {{ scope.row.screenshot ? '是' : '否' }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>
          </el-form>

          <div style="text-align: right">
            <el-button @click="resetScriptGeneration">重新选择</el-button>
            <el-button @click="currentStep = 1">上一步</el-button>
            <el-button type="primary" :loading="saving" @click="saveTestCase">
              保存用例
            </el-button>
          </div>
        </div>
      </div>

      <!-- 步骤4: 完成 -->
      <div v-if="currentStep === 3" style="text-align: center; padding: 40px">
        <el-result icon="success" title="测试用例创建成功">
          <template #extra>
            <el-button type="primary" @click="executeTest">立即执行</el-button>
            <el-button @click="goBack">返回项目</el-button>
          </template>
        </el-result>
      </div>
    </el-card>

    <!-- 录制对话框 -->
    <el-dialog
      v-model="showRecordDialog"
      title="录制Playwright脚本"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="!recordingSessionId">
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
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick, VideoCamera } from '@element-plus/icons-vue'
import { testCaseAPI, testRunAPI, projectAPI } from '../api'

const route = useRoute()
const router = useRouter()

const projectId = route.params.projectId

const currentStep = ref(0)
const generating = ref(false)
const saving = ref(false)
const savedCaseId = ref(null)
const scriptGenerated = ref(false)
const project = ref(null) // 项目信息

// 录制相关
const showRecordDialog = ref(false)
const startingRecord = ref(false)
const stoppingRecord = ref(false)
const recordingSessionId = ref(null)
const recordTargetUrl = ref('')

const form = reactive({
  naturalLanguage: ''
})

const generatedCase = reactive({
  name: '',
  description: '',
  standard_steps: [],
  expected_result: ''
})

const generatedScript = reactive({
  browser: 'chromium',
  viewport: { width: 1280, height: 720 },
  steps: []
})

const goBack = () => {
  router.back()
}

const generateTestCase = async () => {
  generating.value = true
  try {
    const result = await testCaseAPI.generateFromNL(
      projectId,
      form.naturalLanguage
    )
    
    Object.assign(generatedCase, result)
    currentStep.value = 1
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成用例失败')
  } finally {
    generating.value = false
  }
}

const generateScript = async () => {
  // 先创建一个临时用例（包含空脚本）
  try {
    const tempCase = await testCaseAPI.create(projectId, {
      project_id: parseInt(projectId),
      name: generatedCase.name,
      description: generatedCase.description,
      natural_language: form.naturalLanguage,
      standard_steps: generatedCase.standard_steps,
      playwright_script: {},
      expected_result: generatedCase.expected_result
    })

    savedCaseId.value = tempCase.id
    currentStep.value = 2
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建用例失败')
  }
}

const generateScriptByLLM = async () => {
  generating.value = true
  try {
    // 使用LLM生成脚本
    const scriptResult = await testCaseAPI.generateScript(savedCaseId.value)
    Object.assign(generatedScript, scriptResult.playwright_script)
    scriptGenerated.value = true
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成脚本失败')
  } finally {
    generating.value = false
  }
}

const resetScriptGeneration = () => {
  scriptGenerated.value = false
  generatedScript.browser = 'chromium'
  generatedScript.viewport = { width: 1280, height: 720 }
  generatedScript.steps = []
}

const saveTestCase = async () => {
  saving.value = true
  try {
    // 更新用例，添加脚本
    await testCaseAPI.update(savedCaseId.value, {
      playwright_script: generatedScript
    })
    
    ElMessage.success('测试用例保存成功')
    currentStep.value = 3
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const executeTest = async () => {
  try {
    const result = await testRunAPI.execute(savedCaseId.value)
    ElMessage.success('测试已开始执行')
    router.push(`/runs/${result.id}`)
  } catch (error) {
    ElMessage.error('执行失败')
  }
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
        project_id: parseInt(projectId)
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

    // 自动填充到脚本
    Object.assign(generatedScript, data.playwright_script)
    scriptGenerated.value = true

    ElMessage.success('录制完成，脚本已自动生成')

    // 关闭录制对话框
    showRecordDialog.value = false
    recordingSessionId.value = null
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

// 加载项目信息
const loadProject = async () => {
  try {
    project.value = await projectAPI.get(projectId)
  } catch (error) {
    console.error('加载项目信息失败:', error)
  }
}

// 显示录制对话框前设置默认 URL
const handleShowRecordDialog = () => {
  // 优先从项目 base_url 读取
  if (project.value?.base_url) {
    recordTargetUrl.value = project.value.base_url
  }
  // 其次从自然语言描述中提取
  else if (form.naturalLanguage) {
    const urlMatch = form.naturalLanguage.match(/(https?:\/\/[^\s,、。]+)/)
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

onMounted(() => {
  loadProject()
})
</script>

<style scoped>
.test-case-form {
  max-width: 1200px;
}

.test-case-form h3 {
  color: #303133;
  margin-bottom: 20px;
}
</style>
