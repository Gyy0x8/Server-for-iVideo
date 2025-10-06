import { defineStore } from 'pinia'
import api from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null,
    isAuthenticated: !!localStorage.getItem('access_token')
  }),

  actions: {
    async login(username, password) {
      try {
        const response = await api.login(username, password)
        this.token = response.access_token
        this.user = response.user
        this.isAuthenticated = true
        
        
        localStorage.setItem('access_token', this.token)
        localStorage.setItem('user_info', JSON.stringify(this.user))
        
        return { success: true }
      } catch (error) {
        console.error('Login error:', error)
        return { 
          success: false, 
          error: error.response?.data?.detail || '登录失败' 
        }
      }
    },

    async register(username, email, password) {
      try {
        const response = await api.register(username, email, password)
        return { success: true, data: response }
      } catch (error) {
        console.error('Register error:', error)
        return { 
          success: false, 
          error: error.response?.data?.detail || '注册失败' 
        }
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
    },

    async checkAuth() {
      if (this.token) {
        try {
          const user = await api.getCurrentUser()
          this.user = user
          this.isAuthenticated = true
          return true
        } catch (error) {
          console.error('Auth check error:', error)
          this.logout()
          return false
        }
      }
      return false
    }
  }
})