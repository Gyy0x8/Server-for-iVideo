<template>
  <div id="app">
    <el-container v-if="$route.name !== 'login' && $route.name !== 'register'">
      <!-- 顶部导航 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <h1>🎬 iVideo VLog制作工具</h1>
          </div>
          <div class="nav-links">
            <router-link to="/">仪表盘</router-link>
            <router-link to="/projects">项目管理</router-link>
            <el-button @click="logout" type="danger" size="small">退出登录</el-button>
          </div>
        </div>
      </el-header>

      
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>

    
    <router-view v-else />
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AppContainer',
  setup() {
    const authStore = useAuthStore()
    
    const logout = () => {
      authStore.logout()
      window.location.href = '/login'
    }

    return {
      logout
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  min-height: 100vh;
  background: #f5f7fa;
}

.app-header {
  background: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e6e6e6;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.logo h1 {
  color: #409EFF;
  font-size: 24px;
  font-weight: 600;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-links a {
  text-decoration: none;
  color: #606266;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 4px;
  transition: all 0.3s;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: #409EFF;
  background: #ecf5ff;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 60px);
}
</style>