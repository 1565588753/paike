import { defineStore } from 'pinia'
import request from '@/utils/request'

interface User {
  id: number
  username: string
  real_name: string
  role_code: string
  teacher_id: number | null
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: '',
    user: null as User | null,
    firstLogin: false
  }),
  persist: {
    key: 'auth',
    storage: localStorage
  },
  getters: {
    isTeacher: (state) => state.user?.role_code === 'teacher',
    isAdmin: (state) => state.user?.role_code === 'admin',
    isAcademic: (state) => state.user?.role_code === 'academic',
    isLeader: (state) => state.user?.role_code === 'leader',
    canEdit: (state) => ['admin', 'academic'].includes(state.user?.role_code || '')
  },
  actions: {
    async login(username: string, password: string) {
      const res: any = await request.post('/auth/login', { username, password })
      this.token = res.data.access_token
      this.user = {
        id: res.data.user_id,
        username: res.data.username,
        real_name: res.data.real_name,
        role_code: res.data.role_code,
        teacher_id: res.data.teacher_id
      }
      this.firstLogin = res.data.first_login
      return this.user
    },
    async fetchUserInfo() {
      try {
        const res: any = await request.get('/auth/me')
        this.user = res.data
      } catch (e) {
        this.logout()
      }
    },
    async changePassword(oldPwd: string, newPwd: string) {
      return request.post('/auth/change-password', { old_password: oldPwd, new_password: newPwd })
    },
    logout() {
      this.token = ''
      this.user = null
      this.firstLogin = false
    }
  }
})
