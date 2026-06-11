<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span class="title">周课表</span>
          <div class="filters">
            <el-select v-model="appStore.currentVersionId" placeholder="选择版本" style="width: 180px">
              <el-option v-for="v in versions" :key="v.id" :label="v.version_name" :value="v.id" />
            </el-select>
            <el-select v-model="filterType" style="width: 120px">
              <el-option label="按班级" value="class" />
              <el-option label="按教师" value="teacher" />
            </el-select>
            <el-select v-if="filterType === 'class'" v-model="selectedClass" filterable placeholder="选择班级" style="width: 180px">
              <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
            <el-select v-else v-model="selectedTeacher" filterable placeholder="选择教师" style="width: 180px">
              <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
            <el-button type="primary" @click="load">刷新</el-button>
            <el-button @click="exportCSV">导出 CSV</el-button>
          </div>
        </div>
      </template>

      <div class="timetable-wrap" v-if="slots.length">
        <table class="tt-table">
          <thead>
            <tr>
              <th class="time-col">时段</th>
              <th v-for="d in days" :key="d">{{ d }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="slot in slots" :key="slot.id">
              <td class="time-col">
                <div class="slot-name">{{ slot.period_name }}</div>
                <div class="slot-time">{{ slot.start_time }}-{{ slot.end_time }}</div>
              </td>
              <td v-for="(day, i) in days" :key="i">
                <div v-for="entry in cellEntries(slot.id, i + 1)" :key="entry.id" class="tt-card" :style="{ borderColor: subjectColorMap[entry.subject_id] || '#409EFF' }">
                  <div class="tt-subject" :style="{ background: subjectColorMap[entry.subject_id] || '#409EFF' }">{{ entry.subject_name }}</div>
                  <div class="tt-body">
                    <div class="tt-row" v-if="filterType !== 'teacher'"><el-icon><User /></el-icon>{{ entry.teacher_name }}</div>
                    <div class="tt-row" v-if="filterType !== 'class'"><el-icon><Reading /></el-icon>{{ entry.class_name }}</div>
                    <div class="tt-row"><el-icon><Location /></el-icon>{{ entry.classroom_name }}</div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <el-empty v-else description="暂无课表数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { User, Reading, Location } from '@element-plus/icons-vue'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const appStore = useAppStore()
const auth = useAuthStore()
const days = ['周一', '周二', '周三', '周四', '周五']
const versions = ref<any[]>([])
const classes = ref<any[]>([])
const teachers = ref<any[]>([])
const subjects = ref<any[]>([])
const entries = ref<any[]>([])
const planSlots = ref<any[]>([])
const filterType = ref('class')
const selectedClass = ref<number | null>(null)
const selectedTeacher = ref<number | null>(null)

const subjectColorMap = computed(() => Object.fromEntries((subjects.value || []).map((s: any) => [s.id, s.color])))
const slots = computed(() => (planSlots.value || []).filter((s: any) => !s.is_break).sort((a: any, b: any) => a.sort_order - b.sort_order))

function cellEntries(slotId: number, day: number) {
  return entries.value.filter((e: any) => e.time_slot_id === slotId && e.day_of_week === day)
}

async function load() {
  if (!appStore.currentYearId) await appStore.loadYears()
  if (!appStore.currentSemesterId) await appStore.loadSemesters()
  const [v, cls, tch, subj, plans]: any = await Promise.all([
    api.timetable.versions.list({ academic_year_id: appStore.currentYearId, semester_id: appStore.currentSemesterId }),
    api.classes.list({ academic_year_id: appStore.currentYearId }),
    api.teachers.list({ page_size: 200 }),
    api.subjects.list(),
    api.schedulePlans.list()
  ])
  versions.value = v || []
  classes.value = cls || []
  teachers.value = tch?.items || tch || []
  subjects.value = subj || []
  if (plans?.length) planSlots.value = plans[0].slots || []
  if (!appStore.currentVersionId && versions.value.length) appStore.currentVersionId = versions.value[0].id

  if (!selectedClass.value && classes.value.length) selectedClass.value = classes.value[0].id
  if (auth.isTeacher && auth.user?.teacher_id) {
    filterType.value = 'teacher'
    selectedTeacher.value = auth.user.teacher_id
  }

  const params: any = { version_id: appStore.currentVersionId }
  if (filterType.value === 'class' && selectedClass.value) params.class_id = selectedClass.value
  if (filterType.value === 'teacher' && selectedTeacher.value) params.teacher_id = selectedTeacher.value

  entries.value = (await api.timetable.entries.list(params)) || []
}

function exportCSV() {
  const header = ['时段', ...days]
  const rows = slots.value.map((s: any) => {
    const row = [`${s.period_name} (${s.start_time}-${s.end_time})`]
    for (let d = 1; d <= 5; d++) {
      const list = cellEntries(s.id, d)
      row.push(list.map((e: any) => `${e.subject_name} ${e.teacher_name}/${e.classroom_name}`).join(' | '))
    }
    return row
  })
  const csv = [header, ...rows].map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `timetable_${Date.now()}.csv`
  link.click()
}

onMounted(load)
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.title { font-weight: 600; }
.filters { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.page { padding: 16px; }
.timetable-wrap { overflow-x: auto; }
.tt-table { border-collapse: collapse; width: 100%; min-width: 900px; }
.tt-table th, .tt-table td { border: 1px solid #e4e7ed; padding: 6px; vertical-align: top; font-size: 13px; }
.tt-table th { background: #fafafa; }
.time-col { width: 120px; text-align: center; background: #fafafa; }
.slot-name { font-weight: 600; }
.slot-time { color: #909399; font-size: 12px; }
.tt-card { border: 2px solid #409EFF; border-radius: 6px; margin-bottom: 4px; overflow: hidden; font-size: 12px; background: #fff; }
.tt-subject { color: #fff; padding: 4px 6px; font-weight: 600; font-size: 12px; }
.tt-body { padding: 4px 6px; }
.tt-row { display: flex; align-items: center; gap: 4px; color: #303133; margin: 2px 0; }
</style>
