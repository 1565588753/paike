import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('@/views/dashboard/Dashboard.vue'), meta: { title: '首页概览', icon: 'HomeFilled' } },
      { path: 'teachers', name: 'teachers', component: () => import('@/views/basic/Teachers.vue'), meta: { title: '教师管理', icon: 'User', roles: ['admin', 'academic'] } },
      { path: 'classes', name: 'classes', component: () => import('@/views/basic/Classes.vue'), meta: { title: '班级管理', icon: 'School', roles: ['admin', 'academic'] } },
      { path: 'subjects', name: 'subjects', component: () => import('@/views/basic/Subjects.vue'), meta: { title: '科目管理', icon: 'Reading', roles: ['admin', 'academic'] } },
      { path: 'classrooms', name: 'classrooms', component: () => import('@/views/basic/Classrooms.vue'), meta: { title: '教室管理', icon: 'OfficeBuilding', roles: ['admin', 'academic'] } },
      { path: 'hr', name: 'hr', component: () => import('@/views/hr/HRTable.vue'), meta: { title: '人事表', icon: 'Document', roles: ['admin', 'academic'] } },
      { path: 'schedule-plans', name: 'schedule-plans', component: () => import('@/views/hr/SchedulePlans.vue'), meta: { title: '作息方案', icon: 'Clock', roles: ['admin', 'academic'] } },
      { path: 'years', name: 'years', component: () => import('@/views/hr/YearManagement.vue'), meta: { title: '学年管理', icon: 'Calendar', roles: ['admin', 'academic'] } },
      { path: 'timetable', name: 'timetable', component: () => import('@/views/timetable/TimetableView.vue'), meta: { title: '课表', icon: 'Grid' } },
      { path: 'timetable/edit', name: 'timetable-edit', component: () => import('@/views/timetable/TimetableEdit.vue'), meta: { title: '排课与调课', icon: 'EditPen', roles: ['admin', 'academic'] } },
      { path: 'swaps', name: 'swaps', component: () => import('@/views/timetable/SwapRequests.vue'), meta: { title: '换课申请', icon: 'Refresh' } },
      { path: 'stats', name: 'stats', component: () => import('@/views/stats/StatsDashboard.vue'), meta: { title: '统计分析', icon: 'DataAnalysis' } },
      { path: 'notifications', name: 'notifications', component: () => import('@/views/auth/Notifications.vue'), meta: { title: '消息中心', icon: 'Bell' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _, next) => {
  const auth = useAuthStore()
  if (to.meta.public) return next()
  if (!auth.token) return next('/login')
  if (to.meta.roles && auth.user && !(to.meta.roles as string[]).includes(auth.user.role_code)) {
    return next('/dashboard')
  }
  next()
})

export default router
