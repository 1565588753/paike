<template>
  <el-container class="layout">
    <el-aside :width="collapsed ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <el-icon :size="24"><School /></el-icon>
        <span v-if="!collapsed" class="title">智慧排课</span>
      </div>
      <el-menu :default-active="route.path" :collapse="collapsed" router background-color="#001529" text-color="#c9d1d9" active-text-color="#ffd04b">
        <template v-for="item in menuItems" :key="item.path">
          <el-menu-item :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="left">
          <el-button text @click="collapsed = !collapsed">
            <el-icon><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
          </el-button>
          <el-breadcrumb :separator="/">
            <el-breadcrumb-item>{{ route.meta.title || '首页' }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="right">
          <el-select v-model="appStore.currentYearId" style="width: 140px; margin-right: 8px" placeholder="选择学年" @change="onYearChange">
            <el-option v-for="y in appStore.years" :key="y.id" :label="y.name" :value="y.id" />
          </el-select>
          <el-select v-model="appStore.currentSemesterId" style="width: 130px; margin-right: 8px" placeholder="选择学期" @change="onSemesterChange">
            <el-option v-for="s in appStore.semesters" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
          <el-dropdown @command="onCmd">
            <span class="user">
              <el-avatar :size="32">{{ (auth.user?.real_name || '?').charAt(0) }}</el-avatar>
              <span class="name">{{ auth.user?.real_name }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pwd">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout" command-type="primary">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
  <el-dialog v-model="pwdDialog" title="修改密码" width="400px">
    <el-form :model="pwdForm" label-width="100px">
      <el-form-item label="原密码">
        <el-input v-model="pwdForm.old" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="pwdForm.new" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="pwdDialog = false">取消</el-button>
      <el-button type="primary" @click="onPwdSubmit">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const appStore = useAppStore()

const collapsed = ref(false)
const pwdDialog = ref(false)
const pwdForm = ref({ old: '', new: '' })

const menuItems = computed(() => {
  const items: any[] = []
  const routes = router.getRoutes().filter(r => r.meta?.title)
  for (const r of routes) {
    const roles = r.meta.roles as string[] | undefined
    if (roles && auth.user && !roles.includes(auth.user.role_code)) continue
    items.push({ path: r.path, title: r.meta.title, icon: r.meta.icon || 'Menu' })
  }
  return items
})

onMounted(async () => {
  await appStore.loadYears()
  await appStore.loadSemesters()
  await appStore.loadVersions()
})

async function onYearChange() {
  appStore.currentSemesterId = null
  appStore.currentVersionId = null
  await appStore.loadSemesters()
  await appStore.loadVersions()
}
async function onSemesterChange() {
  appStore.currentVersionId = null
  await appStore.loadVersions()
}

function onCmd(cmd: string) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  } else if (cmd === 'pwd') {
    pwdDialog.value = true
  }
}
async function onPwdSubmit() {
  await auth.changePassword(pwdForm.value.old, pwdForm.value.new)
  ElMessage.success('密码修改成功')
  pwdDialog.value = false
}
</script>

<style scoped>
.layout { height: 100vh; }
.sidebar { background: #001529; color: #fff; transition: width .2s; }
.logo { display: flex; align-items: center; gap: 10px; padding: 18px 16px; font-size: 18px; color: #fff; border-bottom: 1px solid #1f3a5f; }
.title { font-weight: 600; }
.header { background: #fff; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 4px rgba(0,0,0,.05); padding: 0 16px; }
.left { display: flex; align-items: center; gap: 12px; }
.right { display: flex; align-items: center; }
.user { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.name { color: #303133; font-weight: 500; }
.main { background: #f5f7fa; padding: 16px; }
.fade-enter-active, .fade-leave-active { transition: opacity .2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
