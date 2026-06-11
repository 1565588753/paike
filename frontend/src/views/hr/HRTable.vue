<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>教师分班与学科周课时配置</span>
        </div>
      </template>

      <el-alert type="info" :closable="false" style="margin-bottom: 12px">
        <div class="alert">
          <el-select v-model="appStore.currentYearId" @change="onYearChange">
            <el-option v-for="y in years" :key="y.id" :label="y.name" :value="y.id" />
          </el-select>
          <el-select v-model="appStore.currentSemesterId">
            <el-option v-for="s in semesters" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
          <el-button v-if="auth.canEdit" type="success" @click="addRow()">+ 添加班级行</el-button>
          <el-button type="primary" @click="load">刷新</el-button>
        </div>
      </el-alert>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="班主任与科目教师" name="hr">
          <el-table :data="hrRows" border stripe>
            <el-table-column label="班级" width="160">
              <template #default="s">
                <el-select v-model="hrRows[s.$index].class_id" filterable style="width: 100%" @change="ensureClassRecord(s.$index)">
                  <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="班主任" width="200">
              <template #default="s">
                <el-select v-model="hrRows[s.$index].head_teacher_id" filterable style="width: 100%">
                  <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column v-for="sub in subjects" :key="sub.id" :label="sub.name" min-width="180">
              <template #default="s">
                <el-select v-model="hrRows[s.$index].subject_teachers[sub.id]" multiple collapse-tags filterable style="width: 100%">
                  <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="备注" min-width="160">
              <template #default="s">
                <el-input v-model="hrRows[s.$index].remark" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="s">
                <el-button link type="primary" @click="saveHRRow(s.row, s.$index)">保存</el-button>
                <el-button link type="danger" @click="deleteHRRow(s.row, s.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="周课时数" name="hours">
          <el-table :data="hoursRows" border stripe>
            <el-table-column label="班级" width="160">
              <template #default="s">
                <el-select v-model="hoursRows[s.$index].class_id" filterable style="width: 100%">
                  <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column v-for="sub in subjects" :key="sub.id" :label="sub.name" width="120">
              <template #default="s">
                <el-input-number v-model="hoursRows[s.$index].hours[sub.id]" :min="0" :max="20" style="width: 100%" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="s">
                <el-button link type="primary" @click="saveHoursRow(s.row, s.$index)">保存</el-button>
                <el-button link type="danger" @click="removeHoursRow(s.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button v-if="auth.canEdit" style="margin-top: 10px" type="success" @click="addHoursRow()">+ 添加班级行</el-button>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const appStore = useAppStore()
const auth = useAuthStore()
const activeTab = ref('hr')
const years = ref<any[]>([])
const semesters = ref<any[]>([])
const classes = ref<any[]>([])
const teachers = ref<any[]>([])
const subjects = ref<any[]>([])
const hrRows = ref<any[]>([])
const hoursRows = ref<any[]>([])

async function load() {
  const [yr, sem, cls, tch, sub, hr, wh]: any = await Promise.all([
    api.years.list(),
    appStore.currentYearId ? api.years.semesters(appStore.currentYearId) : [],
    api.classes.list({ academic_year_id: appStore.currentYearId }),
    api.teachers.list({ page_size: 200 }),
    api.subjects.list(),
    api.hrRecords.list({ academic_year_id: appStore.currentYearId, semester_id: appStore.currentSemesterId }),
    api.weeklyHours.list({ academic_year_id: appStore.currentYearId, semester_id: appStore.currentSemesterId })
  ])
  years.value = yr || []
  semesters.value = sem || []
  classes.value = cls || []
  teachers.value = tch?.items || tch || []
  subjects.value = sub || []

  hrRows.value = (hr || []).map((r: any) => ({
    id: r.id, class_id: r.class_id, head_teacher_id: r.head_teacher_id,
    subject_teachers: { ...(r.subject_teachers || {}) }, remark: r.remark || ''
  }))
  if (!hrRows.value.length && classes.value.length) {
    hrRows.value = classes.value.slice(0, 3).map((c: any) => ({ id: null, class_id: c.id, head_teacher_id: null, subject_teachers: {}, remark: '' }))
  }

  const byClass = new Map()
  ;(wh || []).forEach((h: any) => {
    if (!byClass.has(h.class_id)) byClass.set(h.class_id, { id: h.id, class_id: h.class_id, hours: {} })
    byClass.get(h.class_id).hours[h.subject_id] = h.weekly_hours
  })
  hoursRows.value = Array.from(byClass.values())
  if (!hoursRows.value.length && classes.value.length) {
    hoursRows.value = classes.value.slice(0, 3).map((c: any) => ({ class_id: c.id, hours: {} }))
  }
}

function onYearChange() {
  appStore.currentSemesterId = null
  appStore.loadSemesters()
}

function addRow() {
  hrRows.value.push({ id: null, class_id: null, head_teacher_id: null, subject_teachers: {}, remark: '' })
}
function addHoursRow() {
  hoursRows.value.push({ class_id: null, hours: {} })
}
function removeHoursRow(idx: number) {
  hoursRows.value.splice(idx, 1)
}

function ensureClassRecord(idx: number) {
  if (!hrRows.value[idx].id) {
    // new record will be created on save
  }
}

async function saveHRRow(row: any) {
  if (!row.class_id) return ElMessage.warning('请选择班级')
  const payload = {
    academic_year_id: appStore.currentYearId,
    semester_id: appStore.currentSemesterId,
    class_id: row.class_id,
    head_teacher_id: row.head_teacher_id || null,
    subject_teachers: row.subject_teachers,
    remark: row.remark
  }
  if (row.id) {
    await api.hrRecords.update(row.id, payload)
  } else {
    const r: any = await api.hrRecords.create(payload)
    if (r?.id) row.id = r.id
  }
  ElMessage.success('已保存')
}
async function deleteHRRow(row: any, idx: number) {
  if (row.id) {
    await api.hrRecords.remove(row.id)
    ElMessage.success('已删除')
  }
  hrRows.value.splice(idx, 1)
}

async function saveHoursRow(row: any) {
  if (!row.class_id) return ElMessage.warning('请选择班级')
  const existing: any = await api.weeklyHours.list({
    academic_year_id: appStore.currentYearId,
    semester_id: appStore.currentSemesterId,
    class_id: row.class_id
  })
  const bySubject = new Map((existing || []).map((h: any) => [h.subject_id, h.id]))
  for (const sub of subjects.value) {
    const hours = row.hours?.[sub.id]
    if (!hours) continue
    const payload = {
      academic_year_id: appStore.currentYearId,
      semester_id: appStore.currentSemesterId,
      class_id: row.class_id,
      subject_id: sub.id,
      weekly_hours: hours
    }
    if (bySubject.has(sub.id)) await api.weeklyHours.update(bySubject.get(sub.id), payload)
    else await api.weeklyHours.create(payload)
  }
  ElMessage.success('已保存')
}

onMounted(async () => {
  if (!appStore.currentYearId) await appStore.loadYears()
  if (!appStore.currentSemesterId) await appStore.loadSemesters()
  load()
})
</script>

<style scoped>
.header { font-weight: 600; }
.page { padding: 16px; }
.alert { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
</style>
