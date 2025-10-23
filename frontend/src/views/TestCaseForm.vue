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

      <!-- 步骤3: 查看生成的脚本 -->
      <div v-if="currentStep === 2">
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
          <el-button @click="currentStep = 1">上一步</el-button>
          <el-button type="primary" :loading="saving" @click="saveTestCase">
            保存用例
          </el-button>
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
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { testCaseAPI, testRunAPI } from '../api'

const route = useRoute()
const router = useRouter()

const projectId = route.params.projectId

const currentStep = ref(0)
const generating = ref(false)
const saving = ref(false)
const savedCaseId = ref(null)

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
  generating.value = true
  try {
    // 先创建一个临时用例（包含空脚本）
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

    // 生成脚本
    const scriptResult = await testCaseAPI.generateScript(tempCase.id)
    Object.assign(generatedScript, scriptResult.playwright_script)
    
    currentStep.value = 2
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成脚本失败')
  } finally {
    generating.value = false
  }
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
