<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="header-left">
        <h2>UI测试平台</h2>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ authStore.user?.username }}
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container>
      <el-aside width="200px" class="aside">
        <el-menu
          :default-active="currentRoute"
          router
          class="menu"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>仪表板</span>
          </el-menu-item>
          
          <el-menu-item index="/projects">
            <el-icon><Folder /></el-icon>
            <span>项目管理</span>
          </el-menu-item>
          
          <el-menu-item v-if="authStore.isAdmin" index="/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-main class="main">
        <router-view />
        
        <!-- 版本标记 -->
        <div class="version-badge">
          <div class="version-info">
            {{ version }}
          </div>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import packageJson from '../../package.json'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const currentRoute = computed(() => route.path)
const version = computed(() => `v${packageJson.version}`)

const handleCommand = async (command) => {
  if (command === 'logout') {
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header-left h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
  padding: 0 12px;
  height: 40px;
  line-height: 40px;
  border-radius: 4px;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.aside {
  background-color: #fff;
  border-right: 1px solid #e4e7ed;
}

.menu {
  border-right: none;
}

.main {
  background-color: #f5f7fa;
  padding: 20px;
  position: relative;
}

.version-badge {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 999;
}

.version-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25);
  font-size: 11px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  cursor: default;
  user-select: none;
}

.version-info:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35);
}
</style>
