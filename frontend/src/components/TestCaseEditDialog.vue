<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="编辑测试用例"
    width="900px"
    :close-on-click-modal="false"
  >
    <el-steps :active="currentStep" align-center style="margin-bottom: 30px">
      <el-step title="编辑描述" />
      <el-step title="编辑步骤" />
      <el-step title="编辑脚本" />
    </el-steps>

    <!-- 步骤1：编辑描述 -->
    <div v-show="currentStep === 0">
      <el-form :model="formData" label-width="120px">
        <el-form-item label="用例名称" required>
          <el-input v-model="formData.name" placeholder="请输入用例名称" />
        </el-form-item>
        
        <el-form-item label="用例描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入用例描述"
          />
        </el-form-item>
        
        <el-form-item label="预期结果">
          <el-input
            v-model="formData.expected_result"
            type="textarea"
            :rows="3"
            placeholder="请输入预期结果"
          />
        </el-form-item>
      </el-form>
    </div>

    <!-- 步骤2：编辑步骤 -->
    <div v-show="currentStep === 1">
      <div style="margin-bottom: 15px">
        <el-button type="primary" size="small" @click="addStep">
          <el-icon><Plus /></el-icon>
          添加步骤
        </el-button>
      </div>
      
      <div v-for="(step, index) in formData.standard_steps" :key="index" class="step-item">
        <div class="step-header">
          <span class="step-number">步骤 {{ index + 1 }}</span>
          <el-button
            type="danger"
            size="small"
            text
            @click="removeStep(index)"
            :disabled="formData.standard_steps.length === 1"
          >
            删除
          </el-button>
        </div>
        
        <el-form :model="step" label-width="100px" class="step-form">
          <el-form-item label="操作类型">
            <el-select v-model="step.action" placeholder="请选择操作类型">
              <el-option label="导航" value="navigate" />
              <el-option label="点击" value="click" />
              <el-option label="输入" value="input" />
              <el-option label="等待" value="wait" />
              <el-option label="验证" value="assert" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="目标元素">
            <el-input v-model="step.selector" placeholder="请输入目标元素选择器" />
          </el-form-item>
          
          <el-form-item label="操作值">
            <el-input v-model="step.value" placeholder="请输入操作值" />
          </el-form-item>
          
          <el-form-item label="描述">
            <el-input
              v-model="step.description"
              type="textarea"
              :rows="2"
              placeholder="请输入步骤描述"
            />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 步骤3：编辑脚本 -->
    <div v-show="currentStep === 2">
      <div class="script-editor-container">
        <div class="editor-header">
          <div style="display: flex; align-items: center; gap: 10px;">
            <el-tag :type="formData.executor_type === 'midscene' ? 'success' : 'primary'">
              {{ formData.executor_type === 'midscene' ? 'Midscene 脚本' : 'Playwright 脚本' }}
            </el-tag>
            <span class="editor-hint">
              {{ formData.executor_type === 'midscene' ? '编辑 JSON 格式的 Midscene 脚本' : '编辑 Python 格式的 Playwright 脚本' }}
            </span>
          </div>
          <el-button 
            type="primary" 
            size="small" 
            :loading="regenerating"
            @click="regenerateScript"
          >
            <el-icon><MagicStick /></el-icon>
            使用 LLM 重新生成
          </el-button>
        </div>
        
        <!-- Midscene 脚本编辑器 -->
        <div v-if="formData.executor_type === 'midscene'" class="script-editor">
          <el-input
            v-model="formData.midscene_script"
            type="textarea"
            :rows="20"
            placeholder="请输入 Midscene 脚本（JSON 格式）"
          />
        </div>
        
        <!-- Playwright 脚本编辑器 -->
        <div v-else class="script-editor">
          <el-input
            v-model="formData.playwright_script"
            type="textarea"
            :rows="20"
            placeholder="请输入 Playwright 脚本（Python 格式）"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
        <el-button v-if="currentStep < 2" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-if="currentStep === 2" type="primary" @click="handleSubmit" :loading="saving">
          保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, MagicStick } from '@element-plus/icons-vue'
import { testCaseAPI } from '../api'

const props = defineProps({
  modelValue: Boolean,
  caseData: Object,
  projectId: [String, Number]
})

const emit = defineEmits(['update:modelValue', 'success'])

const currentStep = ref(0)
const saving = ref(false)
const regenerating = ref(false)  // 重新生成脚本状态

const formData = ref({
  name: '',
  description: '',
  expected_result: '',
  standard_steps: [],  // 使用 standard_steps 而不是 steps
  executor_type: 'playwright',
  playwright_script: '',
  midscene_script: ''
})

// 监听弹窗打开，初始化表单数据
watch(() => props.modelValue, (visible) => {
  if (visible && props.caseData) {
    initFormData()
  }
})

const initFormData = () => {
  const data = props.caseData
  
  // 初始化基础信息
  formData.value = {
    name: data.name || '',
    description: data.description || '',
    expected_result: data.expected_result || '',
    standard_steps: data.standard_steps ? JSON.parse(JSON.stringify(data.standard_steps)) : [],
    executor_type: data.executor_type || 'playwright',
    playwright_script: '',
    midscene_script: ''
  }
  
  // 处理 Playwright 脚本（将对象转为 JSON 字符串）
  if (data.playwright_script) {
    if (typeof data.playwright_script === 'string') {
      formData.value.playwright_script = data.playwright_script
    } else {
      formData.value.playwright_script = JSON.stringify(data.playwright_script, null, 2)
    }
  }
  
  // 处理 Midscene 脚本（将对象转为 JSON 字符串）
  if (data.midscene_script) {
    if (typeof data.midscene_script === 'string') {
      formData.value.midscene_script = data.midscene_script
    } else {
      formData.value.midscene_script = JSON.stringify(data.midscene_script, null, 2)
    }
  } else if (data.executor_type === 'midscene' && data.playwright_script) {
    // 兼容旧数据：如果是 midscene 类型但 midscene_script 为空，尝试从 playwright_script 读取
    if (typeof data.playwright_script === 'string') {
      formData.value.midscene_script = data.playwright_script
    } else {
      formData.value.midscene_script = JSON.stringify(data.playwright_script, null, 2)
    }
  }
  
  // 如果 standard_steps 为空，添加一个默认步骤
  if (formData.value.standard_steps.length === 0) {
    formData.value.standard_steps.push({
      index: 1,
      action: 'navigate',
      selector: '',
      value: '',
      description: ''
    })
  }
  
  currentStep.value = 0
}

const addStep = () => {
  formData.value.standard_steps.push({
    index: formData.value.standard_steps.length + 1,
    action: 'click',
    selector: '',
    value: '',
    description: ''
  })
}

const removeStep = (index) => {
  formData.value.standard_steps.splice(index, 1)
  // 重新编号
  formData.value.standard_steps.forEach((step, idx) => {
    step.index = idx + 1
  })
}

const nextStep = () => {
  if (currentStep.value === 0) {
    // 验证第一步
    if (!formData.value.name) {
      ElMessage.warning('请输入用例名称')
      return
    }
  } else if (currentStep.value === 1) {
    // 验证第二步
    if (formData.value.standard_steps.length === 0) {
      ElMessage.warning('请至少添加一个步骤')
      return
    }
  }
  
  currentStep.value++
}

const prevStep = () => {
  currentStep.value--
}

const handleCancel = () => {
  emit('update:modelValue', false)
  currentStep.value = 0
}

const handleSubmit = async () => {
  // 验证脚本
  if (formData.value.executor_type === 'midscene') {
    if (!formData.value.midscene_script) {
      ElMessage.warning('请输入 Midscene 脚本')
      return
    }
    // 验证 JSON 格式
    try {
      JSON.parse(formData.value.midscene_script)
    } catch (e) {
      ElMessage.error('Midscene 脚本格式错误，请输入有效的 JSON')
      return
    }
  } else {
    if (!formData.value.playwright_script) {
      ElMessage.warning('请输入 Playwright 脚本')
      return
    }
  }
  
  saving.value = true
  try {
    await testCaseAPI.update(props.caseData.id, formData.value)
    ElMessage.success('更新成功')
    emit('success')
    emit('update:modelValue', false)
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error(error.response?.data?.detail || '更新失败')
  } finally {
    saving.value = false
  }
}

// 重新生成脚本
const regenerateScript = async () => {
  regenerating.value = true
  try {
    let scriptResult
    if (formData.value.executor_type === 'midscene') {
      // 生成 Midscene 脚本
      scriptResult = await testCaseAPI.generateMidsceneScript(props.caseData.id)
      formData.value.midscene_script = JSON.stringify(scriptResult.playwright_script, null, 2)
      ElMessage.success('Midscene 脚本重新生成成功')
    } else {
      // 生成 Playwright 脚本
      scriptResult = await testCaseAPI.generateScript(props.caseData.id)
      formData.value.playwright_script = JSON.stringify(scriptResult.playwright_script, null, 2)
      ElMessage.success('Playwright 脚本重新生成成功')
    }
  } catch (error) {
    console.error('生成脚本失败:', error)
    ElMessage.error(error.response?.data?.detail || '生成脚本失败')
  } finally {
    regenerating.value = false
  }
}
</script>

<style scoped>
.step-item {
  background: #f5f7fa;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.step-number {
  font-weight: bold;
  color: #409eff;
}

.step-form {
  margin-top: 10px;
}

.script-editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-header {
  background: #f5f7fa;
  padding: 10px 15px;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: space-between;  /* 左右分布 */
  gap: 10px;
}

.editor-hint {
  color: #909399;
  font-size: 14px;
}

.script-editor {
  padding: 15px;
}

.script-editor :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
