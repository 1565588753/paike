<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <div class="title">课表编辑</div>
          <div class="actions">
            <el-select v-model="appStore.currentVersionId" placeholder="选择版本" style="width: 180px" @change="load">
              <el-option v-for="v in versions" :key="v.id" :label="v.version_name" :value="v.id" />
            </el-select>
            <el-button v-if="auth.canEdit" @click="newVersion()">+ 新版本</el-button>
            <el-button v-if="auth.canEdit" type="primary" @click="autoSchedule">自动排课</el-button>
            <el-button v-if="auth.canEdit" type="success" @click="publish">发布版本</el-button>
            <el-button v-if="auth.canEdit" link type="danger" @click="deleteVersion">删除</el-button>
            <el-button type="info" @click="load">刷新</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="12" class="quality-row" v-if="quality">
        <el-col :span="6">
          <el-statistic title="综合评分" :value="quality.total_score || 0" :precision="1" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="主科覆盖" :value="(quality.main_coverage_rate || 0) * 100" suffix="%" :precision="1" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="教师均衡度" :value="quality.teacher_balance_score || 0" :precision="1" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="科目均衡度" :value="quality.subject_balance_score || 0" :precision="1" />
        </el-col>
      </el-row>

      <el-divider />

      <div class="toolbar">
        <el-button v-if="auth.canEdit" type="primary" @click="openEntryDialog()">+ 手动添加课节</el-button>
        <el-select v-model="viewClass" filterable placeholder="筛选班级" clearable style="width: 180px" @change="filterEntries">
          <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="viewTeacher" filterable placeholder="筛选教师" clearable style="width: 180px" @change="filterEntries">
          <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
      </div>

      <el-table :data="filteredEntries" border stripe>
        <el-table-column label="星期" width="80">
          <template #default="s">{{ ['一','二','三','四','五','六','日'][(s.row.day_of_week || 1) - 1] }}</template>
        </el-table-column>
        <el-table-column label="时段" width="140">
          <template #default="s">{{ slotNames[s.row.time_slot_id] || s.row.time_slot_id }}</template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" width="140" />
        <el-table-column prop="subject_name" label="科目" width="120">
          <template #default="s">
            <el-tag :color="subjectColorMap[s.row.subject_id]" effect="dark">{{ s.row.subject_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="teacher_name" label="教师" width="120" />
        <el-table-column prop="classroom_name" label="教室" width="120" />
        <el-table-column label="固定" width="70">
          <template #default="s"><el-tag v-if="s.row.is_fixed" size="small" type="warning">固定</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="s">
            <el-button v-if="auth.canEdit" link type="primary" @click="openEntryDialog(s.row)">编辑</el-button>
            <el-button v-if="auth.canEdit" link type="success" @click="openMoveDialog(s.row)">移动</el-button>
            <el-button v-if="auth.canEdit" link type="warning" @click="openSwapDialog(s.row)">交换</el-button>
            <el-button v-if="auth.canEdit" link type="danger" @click="removeEntry(s.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="entryDialogVisible" :title="entryForm.id ? '编辑课节' : '添加课节'" width="560px">
      <el-form :model="entryForm" label-width="100px">
        <el-form-item label="班级"><el-select v-model="entryForm.class_id" filterable style="width: 100%"><el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" /></el-select></el-form-item>
        <el-form-item label="科目"><el-select v-model="entryForm.subject_id" style="width: 100%"><el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" /></el-select></el-form-item>
        <el-form-item label="教师"><el-select v-model="entryForm.teacher_id" filterable style="width: 100%"><el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" /></el-select></el-form-item>
        <el-form-item label="教室"><el-select v-model="entryForm.classroom_id" filterable style="width: 100%"><el-option v-for="r in classrooms" :key="r.id" :label="r.name" :value="r.id" /></el-select></el-form-item>
        <el-form-item label="星期"><el-select v-model="entryForm.day_of_week" style="width: 100%"><el-option v-for="d in [1,2,3,4,5]" :key="d" :label="'周' + ['一','二','三','四','五'][d-1]" :value="d" /></el-select></el-form-item>
        <el-form-item label="时段"><el-select v-model="entryForm.time_slot_id" style="width: 100%"><el-option v-for="s in teachingSlots" :key="s.id" :label="s.period_name" :value="s.id" /></el-select></el-form-item>
        <el-form-item label="排课计划"><el-select v-model="entryForm.schedule_plan_id" clearable style="width: 100%"><el-option v-for="p in plans" :key="p.id" :label="p.name" :value="p.id" /></el-select></el-form-item>
        <el-form-item label="固定课节"><el-switch v-model="entryForm.is_fixed" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="entryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEntry">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="moveDialogVisible" title="移动课节" width="460px">
      <el-form label-width="100px">
        <el-form-item label="目标星期"><el-select v-model="moveForm.to_day" style="width: 100%"><el-option v-for="d in [1,2,3,4,5]" :key="d" :label="'周' + ['一','二','三','四','五'][d-1]" :value="d" /></el-select></el-form-item>
        <el-form-item label="目标时段"><el-select v-model="moveForm.to_time_slot_id" style="width: 100%"><el-option v-for="s in teachingSlots" :key="s.id" :label="s.period_name" :value="s.id" /></el-select></el-form-item>
        <el-form-item label="目标教室"><el-select v-model="moveForm.to_classroom_id" filterable clearable style="width: 100%"><el-option v-for="r in classrooms" :key="r.id" :label="r.name" :value="r.id" /></el-select></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doMove">移动</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="swapDialogVisible" title="与其它课节交换" width="460px">
      <el-form label-width="120px">
        <el-form-item label="目标课节"><el-select v-model="swapTargetId" filterable style="width: 100%"><el-option v-for="e in entries" :key="e.id" :label="`${e.class_name} ${e.subject_name} 周${['一','二','三','四','五'][(e.day_of_week||1)-1]} ${slotNames[e.time_slot_id]}`" :value="e.id" /></el-select></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="swapDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doSwap">交换</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="newVersionVisible" title="创建新版本" width="460px">
      <el-form label-width="100px">
        <el-form-item label="版本名称"><el-input v-model="newVersionName" placeholder="例如 draft-1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newVersionVisible = false">取消</el-button>
        <el-button type="primary" @click="createVersion">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const appStore = useAppStore()
const auth = useAuthStore()
const versions = ref<any[]>([])
const classes = ref<any[]>([])
const teachers = ref<any[]>([])
const subjects = ref<any[]>([])
const classrooms = ref<any[]>([])
const plans = ref<any[]>([])
const entries = ref<any[]>([])
const quality = ref<any>(null)
const slotNames = reactive<Record<number, string>>({})

const viewClass = ref<number | null>(null)
const viewTeacher = ref<number | null>(null)
const filteredEntries = ref<any[]>([])

const entryDialogVisible = ref(false)
const moveDialogVisible = ref(false)
const swapDialogVisible = ref(false)
const newVersionVisible = ref(false)
const newVersionName = ref('')
const swapTargetId = ref<number | null>(null)
const movingEntry = ref<any>(null)
const swappingEntry = ref<any>(null)

const emptyEntry = () => ({
  id: null as number | null,
  class_id: null as number | null,
  subject_id: null as number | null,
  teacher_id: null as number | null,
  classroom_id: null as number | null,
  day_of_week: 1,
  time_slot_id: null as number | null,
  schedule_plan_id: null as number | null,
  is_fixed: false
})
const entryForm = reactive(emptyEntry())
const moveForm = reactive({ to_day: 1, to_time_slot_id: null as number | null, to_classroom_id: null as number | null })

const subjectColorMap = computed(() => Object.fromEntries((subjects.value || []).map((s: any) => [s.id, s.color])))
const teachingSlots = computed(() => {
  const slots = plans.value[0]?.slots || []
  const out = slots.filter((s: any) => !s.is_break)
  out.forEach((s: any) => { slotNames[s.id] = s.period_name })
  return out
})

function filterEntries() {
  filteredEntries.value = entries.value.filter((e: any) => {
    if (viewClass.value && e.class_id !== viewClass.value) return false
    if (viewTeacher.value && e.teacher_id !== viewTeacher.value) return false
    return true
  })
}

async function load() {
  const [v, cls, tch, subj, rm, pln]: any = await Promise.all([
    api.timetable.versions.list({ academic_year_id: appStore.currentYearId, semester_id: appStore.currentSemesterId }),
    api.classes.list({ academic_year_id: appStore.currentYearId }),
    api.teachers.list({ page_size: 200 }),
    api.subjects.list(),
    api.classrooms.list(),
    api.schedulePlans.list()
  ])
  versions.value = v || []
  classes.value = cls || []
  teachers.value = tch?.items || tch || []
  subjects.value = subj || []
  classrooms.value = rm || []
  plans.value = pln || []

  if (!appStore.currentVersionId && versions.value.length) appStore.currentVersionId = versions.value[0].id
  if (appStore.currentVersionId) {
    const [e, q]: any = await Promise.all([
      api.timetable.entries.list({ version_id: appStore.currentVersionId }),
      api.timetable.versions.quality(appStore.currentVersionId).catch(() => null)
    ])
    entries.value = e || []
    quality.value = q
  }
  filterEntries()
}

function openEntryDialog(row?: any) {
  Object.assign(entryForm, emptyEntry())
  if (row) Object.assign(entryForm, { id: row.id, class_id: row.class_id, subject_id: row.subject_id, teacher_id: row.teacher_id, classroom_id: row.classroom_id, day_of_week: row.day_of_week, time_slot_id: row.time_slot_id, schedule_plan_id: row.schedule_plan_id, is_fixed: !!row.is_fixed })
  entryDialogVisible.value = true
}

async function saveEntry() {
  if (!entryForm.class_id || !entryForm.subject_id || !entryForm.teacher_id || !entryForm.time_slot_id) return ElMessage.warning('请完整填写必填项')
  if (entryForm.id) {
    await api.timetable.entries.remove(entryForm.id)
    await api.timetable.entries.create(entryForm)
    ElMessage.success('已更新')
  } else {
    await api.timetable.entries.create(entryForm)
    ElMessage.success('已添加')
  }
  entryDialogVisible.value = false
  load()
}

async function removeEntry(row: any) {
  await ElMessageBox.confirm('确定删除此课节吗？', '提示', { type: 'warning' })
  await api.timetable.entries.remove(row.id)
  ElMessage.success('已删除')
  load()
}

function openMoveDialog(row: any) {
  movingEntry.value = row
  moveForm.to_day = row.day_of_week
  moveForm.to_time_slot_id = row.time_slot_id
  moveForm.to_classroom_id = row.classroom_id
  moveDialogVisible.value = true
}

async function doMove() {
  if (!movingEntry.value) return
  await api.timetable.entries.move(movingEntry.value.id, { entry_id: movingEntry.value.id, to_day: moveForm.to_day, to_time_slot_id: moveForm.to_time_slot_id, to_classroom_id: moveForm.to_classroom_id })
  ElMessage.success('已移动')
  moveDialogVisible.value = false
  load()
}

function openSwapDialog(row: any) {
  swappingEntry.value = row
  swapTargetId.value = null
  swapDialogVisible.value = true
}

async function doSwap() {
  if (!swappingEntry.value || !swapTargetId.value) return ElMessage.warning('请选择目标课节')
  await api.timetable.entries.swap({ entry_a_id: swappingEntry.value.id, entry_b_id: swapTargetId.value })
  ElMessage.success('已交换')
  swapDialogVisible.value = false
  load()
}

function newVersion() { newVersionName.value = `v${(versions.value.length || 0) + 1}`; newVersionVisible.value = true }
async function createVersion() {
  if (!newVersionName.value) return ElMessage.warning('请输入名称')
  await api.timetable.versions.create({ academic_year_id: appStore.currentYearId, semester_id: appStore.currentSemesterId, version_name: newVersionName.value })
  ElMessage.success('已创建')
  newVersionVisible.value = false
  load()
}

async function autoSchedule() {
  if (!appStore.currentVersionId) return ElMessage.warning('请先选择或创建版本')
  await api.timetable.versions.autoSchedule(appStore.currentVersionId)
  ElMessage.success('自动排课完成')
  load()
}

async function publish() {
  if (!appStore.currentVersionId) return
  await ElMessageBox.confirm('发布后将作为正式课表，确定继续？', '提示', { type: 'warning' })
  await api.timetable.versions.publish(appStore.currentVersionId)
  ElMessage.success('已发布')
  load()
}

async function deleteVersion() {
  if (!appStore.currentVersionId) return
  await ElMessageBox.confirm('确定删除当前版本？', '提示', { type: 'warning' })
  await api.timetable.versions.remove(appStore.currentVersionId)
  appStore.currentVersionId = null
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.title { font-weight: 600; font-size: 16px; }
.actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.toolbar { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; flex-wrap: wrap; }
.quality-row { padding: 8px 4px; }
.page { padding: 16px; }
</style>
