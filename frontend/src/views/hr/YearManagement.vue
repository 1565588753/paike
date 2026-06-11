<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>学年与学期管理</span>
          <el-button v-if="auth.canEdit" type="success" @click="yearDialogVisible = true">新增学年</el-button>
        </div>
      </template>

      <el-table :data="years" border stripe>
        <el-table-column prop="name" label="学年名称" width="180" />
        <el-table-column prop="start_date" label="开始" width="120" />
        <el-table-column prop="end_date" label="结束" width="120" />
        <el-table-column label="当前" width="90">
          <template #default="s"><el-tag v-if="s.row.is_current" type="success">当前</el-tag></template>
        </el-table-column>
        <el-table-column label="已归档" width="90">
          <template #default="s"><el-tag v-if="s.row.is_archived" type="info">已归档</el-tag></template>
        </el-table-column>
        <el-table-column label="学期" min-width="400">
          <template #default="s">
            <el-tag v-for="sem in semesterMap[s.row.id] || []" :key="sem.id" style="margin: 2px">
              {{ sem.name }} ({{ sem.total_weeks }}周)
              <el-tag v-if="sem.is_current" type="success" size="small" style="margin-left: 4px">当前</el-tag>
            </el-tag>
            <el-button link type="primary" @click="openSemesterDialog(s.row)">+ 添加学期</el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="s">
            <el-button link type="primary" @click="setCurrent(s.row)">设为当前学年</el-button>
            <el-button link type="warning" @click="archiveYear(s.row)">归档</el-button>
            <el-button v-if="s.row.is_archived" link type="success" @click="openUpgradeDialog(s.row)">升级到新学年</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="yearDialogVisible" title="新增学年" width="540px">
      <el-form :model="yearForm" label-width="110px">
        <el-form-item label="学年名称"><el-input v-model="yearForm.name" placeholder="例如 2025-2026" /></el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="yearForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="yearForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="设为当前"><el-switch v-model="yearForm.is_current" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="yearDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveYear">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="semesterDialogVisible" title="新增学期" width="540px">
      <el-form :model="semesterForm" label-width="110px">
        <el-form-item label="学期名称"><el-input v-model="semesterForm.name" placeholder="例如 上学期" /></el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="semesterForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="semesterForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="周数"><el-input-number v-model="semesterForm.total_weeks" :min="1" :max="30" style="width: 100%" /></el-form-item>
        <el-form-item label="设为当前"><el-switch v-model="semesterForm.is_current" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="semesterDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSemester">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="upgradeDialogVisible" title="升级到新学年" width="460px">
      <el-form label-width="120px">
        <el-form-item label="来源学年"><el-tag type="info">{{ upgradeYear?.name }}</el-tag></el-form-item>
        <el-form-item label="目标学年">
          <el-select v-model="upgradeTargetId" filterable style="width: 100%">
            <el-option v-for="y in years.filter((x: any) => !x.is_archived && x.id !== upgradeYear?.id)" :key="y.id" :label="y.name" :value="y.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="upgradeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doUpgrade">执行升级</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const years = ref<any[]>([])
const semesterMap = reactive<Record<number, any[]>>({})
const yearDialogVisible = ref(false)
const semesterDialogVisible = ref(false)
const upgradeDialogVisible = ref(false)
const upgradeYear = ref<any>(null)
const upgradeTargetId = ref<number | null>(null)
const activeYearId = ref<number | null>(null)

const emptyYear = () => ({ name: '', start_date: '', end_date: '', is_current: false })
const yearForm = reactive(emptyYear())
const emptySemester = () => ({ name: '', start_date: '', end_date: '', total_weeks: 20, is_current: false })
const semesterForm = reactive(emptySemester())

async function load() {
  years.value = (await api.years.list()) || []
  for (const y of years.value) {
    semesterMap[y.id] = (await api.years.semesters(y.id)) || []
  }
}

async function saveYear() {
  if (!yearForm.name) return ElMessage.warning('请填写名称')
  await api.years.create(yearForm)
  ElMessage.success('已创建')
  yearDialogVisible.value = false
  Object.assign(yearForm, emptyYear())
  load()
}

async function setCurrent(row: any) {
  await api.years.setCurrent(row.id)
  ElMessage.success('已设为当前学年')
  load()
}

async function archiveYear(row: any) {
  await api.years.archive(row.id)
  ElMessage.success('已归档')
  load()
}

function openSemesterDialog(row: any) {
  activeYearId.value = row.id
  Object.assign(semesterForm, emptySemester())
  semesterDialogVisible.value = true
}

async function saveSemester() {
  if (!activeYearId.value || !semesterForm.name) return ElMessage.warning('请完整填写')
  await api.years.createSemester(activeYearId.value, semesterForm)
  ElMessage.success('已创建')
  semesterDialogVisible.value = false
  if (semesterForm.is_current) {
    // reload semester list for that year
    semesterMap[activeYearId.value] = (await api.years.semesters(activeYearId.value)) || []
  } else {
    load()
  }
}

function openUpgradeDialog(row: any) {
  upgradeYear.value = row
  upgradeTargetId.value = null
  upgradeDialogVisible.value = true
}

async function doUpgrade() {
  if (!upgradeTargetId.value || !upgradeYear.value) return
  await api.years.upgrade(upgradeYear.value.id, upgradeTargetId.value)
  ElMessage.success('升级完成')
  upgradeDialogVisible.value = false
  load()
}

onMounted(load)
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.page { padding: 16px; }
</style>
