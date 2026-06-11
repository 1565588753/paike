<template>
  <div class="login-wrap">
    <el-card class="login-card" shadow="hover">
      <div class="title-area">
        <h2>智慧教务与智能排课管理平台</h2>
        <p>School Smart Scheduling System</p>
      </div>
      <el-form :model="form" label-width="80px" size="large" @submit.prevent="submit">
        <el-form-item label="账号">
          <el-input v-model="form.username" placeholder="请输入账号" prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" prefix-icon="Lock" @keyup.enter="submit" />
        </el-form-item>
        <el-button type="primary" style="width: 100%" :loading="loading" size="large" @click="submit">登 录</el-button>
      </el-form>
      <div class="tips">
        <p>默认管理员: admin / 123456</p>
      </div>
    </el-card>
    <el-dialog v-model="firstLogin" title="首次登录，请修改密码" :close-on-click-modal="false" :close-on-press-escape="false" width="420px">
      <el-form :model="pwdForm" label-width="100px">
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="pwdForm.confirm" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="changePwd">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const form = ref({ username: 'admin', password: '123456' })
const loading = ref(false)
const firstLogin = ref(false)
const pwdForm = ref({ new: '', confirm: '' })

async function submit() {
  if (!form.value.username || !form.value.password) {
    return ElMessage.warning('请输入账号和密码')
  }
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    if (auth.firstLogin && form.value.username !== 'admin') {
      firstLogin.value = true
    } else {
      router.push('/dashboard')
    }
  } finally {
    loading.value = false
  }
}

async function changePwd() {
  if (!pwdForm.value.new || pwdForm.value.new !== pwdForm.value.confirm) {
    return ElMessage.warning('两次密码不一致')
  }
  await auth.changePassword(form.value.password, pwdForm.value.new)
  ElMessage.success('密码修改成功，请重新登录')
  auth.logout()
  firstLogin.value = false
  router.push('/login')
}
</script>

<style scoped>
.login-wrap {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
}
.login-card {
  width: 420px;
  padding: 16px 28px;
}
.title-area {
  text-align: center;
  margin-bottom: 24px;
}
.title-area h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}
.title-area p {
  color: #909399;
  font-size: 13px;
  margin-top: 6px;
}
.tips {
  margin-top: 14px;
  text-align: center;
  color: #909399;
  font-size: 12px;
}
</style>
