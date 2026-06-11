<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <el-select v-model="filter.grade_id" placeholder="全部年级" clearable style="width: 160px" @change="load">
            <el-option v-for="g in grades" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
          <el-button type="primary" @click="load">查询</el-button>
          <el-button v-if="auth.canEdit" type="success" @click="openDialog()">新增班级</el-button>
        </div>
      </template>
      <el-table :data="items" border stripe>
        <el-table-column prop="name" label="班级名称" min-width="160" />
        <el-table-column label="年级" width="120">
          <template #default="s">{{ gradeMap[s.row.grade_id]?.name }}</template>
        </el-table-column>
        <el-table-column prop="student_count" label="人数" width="90" />
        <el-table-column label="排课计划" width="160">
          <template #default="s">
            <el-tag v-if="planMap[s.row.schedule_plan_id]" type="info">{{ planMap[s.row.schedule_plan_id]?.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="所属学年" width="160">
          <template #default="s">{{ yearMap[s.row.academic_year_id]?.name }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="s">
            <el-button v-if="auth.canEdit" link type="primary" @click="openDialog(s.row)">编辑</el-button>
            <el-button v-if="auth.canEdit" link type="danger" @click="removeItem(s.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑班级' : '新增班级'" width="560px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="班级名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="所属学年">
          <el-select v-model="form.academic_year_id" style="width: 100%">
            <el-option v-for="y in years" :key="y.id" :label="y.name" :value="y.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="年级">
          <el-select v-model="form.grade_id" style="width: 100%">
            <el-option v-for="g in grades" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学生人数"><el-input-number v-model="form.student_count" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="排课计划">
          <el-select v-model="form.schedule_plan_id" clearable style="width: 100%">
            <el-option v-for="p in plans" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const auth = useAuthStore()
const appStore = useAppStore()
const items = ref<any[]>([])
const grades = ref<any[]>([])
const plans = ref<any[]>([])
const years = ref<any[]>([])
const filter = reactive({ grade_id: null as number | null })
const dialogVisible = ref(false)

const gradeMap = computed(() => Object.fromEntries(grades.value.map((g: any) => [g.id, g])))
const planMap = computed(() => Object.fromEntries(plans.value.map((p: any) => [p.id, p])))
const yearMap = computed(() => Object.fromEntries(years.value.map((y: any) => [y.id, y])))

const emptyForm = () => ({
  id: null as number | null,
  name: '',
  grade_id: null as number | null,
  student_count: 40,
  schedule_plan_id: null as number | null,
  academic_year_id: appStore.currentYearId
})
const form = reactive(emptyForm())

async function load() {
  const [cls, grd, pln, yrs]: any = await Promise.all([
    api.classes.list({ academic_year_id: appStore.currentYearId, grade_id: filter.grade_id }),
    api.grades.list(),
    api.schedulePlans.list(),
    api.years.list()
  ])
  items.value = cls || []
  grades.value = grd || []
  plans.value = pln || []
  years.value = yrs || []
}

function openDialog(row?: any) {
  Object.assign(form, emptyForm())
  if (row) Object.assign(form, row)
  dialogVisible.value = true
}

async function save() {
  if (!form.name) return ElMessage.warning('请填写班级名称')
  if (form.id) await api.classes.update(form.id, form)
  else await api.classes.create(form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  load()
}

async function removeItem(row: any) {
  await ElMessageBox.confirm(`确定删除 ${row.name} 吗？`, '提示', { type: 'warning' })
  await api.classes.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.header { display: flex; gap: 8px; align-items: center; }
.page { padding: 16px; }
</style>
