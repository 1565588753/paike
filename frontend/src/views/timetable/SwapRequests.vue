<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>换课申请</span>
          <el-button type="primary" @click="openCreate()">发起换课</el-button>
          <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 140px" @change="load">
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </div>
      </template>

      <el-table :data="list" border stripe>
        <el-table-column label="申请课节" min-width="260">
          <template #default="s">{{ formatEntry(s.row.entry_a_id) }}</template>
        </el-table-column>
        <el-table-column label="目标课节" min-width="260">
          <template #default="s">{{ formatEntry(s.row.entry_b_id) }}</template>
        </el-table-column>
        <el-table-column label="申请人" width="120">
          <template #default="s">{{ teacherName(s.row.requester_teacher_id) }}</template>
        </el-table-column>
        <el-table-column label="对方教师" width="120">
          <template #default="s">{{ teacherName(s.row.target_teacher_id) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="s"><el-tag :type="statusTag(s.row.status)">{{ s.row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" min-width="180" />
        <el-table-column prop="requested_at" label="时间" width="160" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="s">
            <el-button v-if="canConfirm(s.row)" link type="success" @click="confirm(s.row)">确认</el-button>
            <el-button v-if="canApprove(s.row)" link type="primary" @click="approve(s.row)">批准</el-button>
            <el-button v-if="canReject(s.row)" link type="danger" @click="reject(s.row)">拒绝</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createVisible" title="发起换课申请" width="560px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="我的课节"><el-select v-model="form.entry_a_id" filterable style="width: 100%"><el-option v-for="e in myEntries" :key="e.id" :label="`${e.class_name} ${e.subject_name} 周${['一','二','三','四','五'][(e.day_of_week||1)-1]}`" :value="e.id" /></el-select></el-form-item>
        <el-form-item label="对方教师"><el-select v-model="form.target_teacher_id" filterable style="width: 100%"><el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" /></el-select></el-form-item>
        <el-form-item label="对方课节"><el-select v-model="form.entry_b_id" filterable style="width: 100%"><el-option v-for="e in targetEntries" :key="e.id" :label="`${e.class_name} ${e.subject_name} 周${['一','二','三','四','五'][(e.day_of_week||1)-1]}`" :value="e.id" /></el-select></el-form-item>
        <el-form-item label="原因"><el-input v-model="form.reason" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const appStore = useAppStore()
const auth = useAuthStore()
const list = ref<any[]>([])
const teachers = ref<any[]>([])
const entries = ref<any[]>([])
const statusFilter = ref<string>('')
const createVisible = ref(false)
const form = reactive({ entry_a_id: null as number | null, entry_b_id: null as number | null, target_teacher_id: null as number | null, reason: '' })

const teacherMap = computed(() => Object.fromEntries((teachers.value || []).map((t: any) => [t.id, t])))
const entryMap = computed(() => Object.fromEntries((entries.value || []).map((e: any) => [e.id, e])))

const myEntries = computed(() => entries.value.filter((e: any) => e.teacher_id === auth.user?.teacher_id))
const targetEntries = computed(() => entries.value.filter((e: any) => e.teacher_id === form.target_teacher_id))

function teacherName(id: number | null) {
  return id ? teacherMap.value[id]?.name || '-' : '-'
}
function formatEntry(id: number | null) {
  const e = entryMap.value[id]
  if (!e) return '-'
  return `${e.class_name} ${e.subject_name} 周${['一', '二', '三', '四', '五'][(e.day_of_week || 1) - 1]}`
}
function statusTag(s: string) {
  return ({ pending: 'warning', confirmed: 'info', approved: 'success', rejected: 'danger' } as any)[s] || ''
}
function canConfirm(row: any) {
  return row.status === 'pending' && row.target_teacher_id === auth.user?.teacher_id
}
function canApprove(row: any) {
  return row.status === 'confirmed' && (auth.canEdit || auth.isLeader)
}
function canReject(row: any) {
  return (row.status === 'pending' && row.target_teacher_id === auth.user?.teacher_id) || (row.status === 'confirmed' && (auth.canEdit || auth.isLeader))
}

async function load() {
  const [ls, tch, ent]: any = await Promise.all([
    api.swaps.list({ status: statusFilter.value || undefined }),
    api.teachers.list({ page_size: 200 }),
    appStore.currentVersionId ? api.timetable.entries.list({ version_id: appStore.currentVersionId }) : []
  ])
  list.value = ls || []
  teachers.value = tch?.items || tch || []
  entries.value = ent || []
}

function openCreate() {
  form.entry_a_id = null
  form.entry_b_id = null
  form.target_teacher_id = null
  form.reason = ''
  createVisible.value = true
}

async function submit() {
  if (!form.entry_a_id || !form.target_teacher_id) return ElMessage.warning('请选择自己的课节和对方教师')
  await api.swaps.create(form)
  ElMessage.success('已提交')
  createVisible.value = false
  load()
}

async function confirm(row: any) {
  await api.swaps.confirm(row.id)
  ElMessage.success('已确认')
  load()
}
async function approve(row: any) {
  await api.swaps.approve(row.id)
  ElMessage.success('已批准')
  load()
}
async function reject(row: any) {
  await api.swaps.reject(row.id)
  ElMessage.success('已拒绝')
  load()
}

onMounted(async () => {
  if (!appStore.currentVersionId) {
    await appStore.loadVersions()
  }
  load()
})
</script>

<style scoped>
.header { display: flex; gap: 8px; align-items: center; font-weight: 600; }
.page { padding: 16px; }
</style>
