<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <el-input v-model="keyword" placeholder="搜索教师编号/姓名/电话" clearable style="width: 260px" @clear="load" @keyup.enter="load" />
          <el-button type="primary" @click="load">查询</el-button>
          <el-button v-if="auth.canEdit" type="success" @click="openDialog()">新增教师</el-button>
        </div>
      </template>
      <el-table :data="items" border stripe>
        <el-table-column prop="teacher_no" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="110" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="s">{{ s.row.gender === 'male' ? '男' : '女' }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="title" label="职称" width="110" />
        <el-table-column label="主授科目" width="140">
          <template #default="s">
            <el-tag v-if="subjectMap[s.row.main_subject_id]" :color="subjectMap[s.row.main_subject_id]?.color" effect="light">
              {{ subjectMap[s.row.main_subject_id]?.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="可授科目" min-width="200">
          <template #default="s">
            <el-tag v-for="sid in s.row.subject_ids || []" :key="sid" size="small" style="margin: 2px">{{ subjectMap[sid]?.name || sid }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="max_weekly_hours" label="周上限" width="90" />
        <el-table-column prop="max_daily_hours" label="日上限" width="90" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="s">
            <el-tag :type="s.row.status === 'active' ? 'success' : 'info'">{{ s.row.status === 'active' ? '在职' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="s">
            <el-button v-if="auth.canEdit" link type="primary" @click="openDialog(s.row)">编辑</el-button>
            <el-button v-if="auth.canEdit" link type="danger" @click="removeItem(s.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        background
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="load"
        @current-change="load"
        style="margin-top: 12px; justify-content: flex-end; display: flex"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑教师' : '新增教师'" width="640px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="工号"><el-input v-model="form.teacher_no" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="性别"><el-select v-model="form.gender" style="width: 100%"><el-option label="男" value="male" /><el-option label="女" value="female" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="职称"><el-input v-model="form.title" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="主授科目"><el-select v-model="form.main_subject_id" clearable style="width: 100%"><el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" /></el-select></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="可授科目"><el-select v-model="form.subject_ids" multiple collapse-tags style="width: 100%"><el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="周课时上限"><el-input-number v-model="form.max_weekly_hours" :min="0" :max="40" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="日课时上限"><el-input-number v-model="form.max_daily_hours" :min="0" :max="12" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="状态"><el-select v-model="form.status" style="width: 100%"><el-option label="在职" value="active" /><el-option label="停用" value="inactive" /></el-select></el-form-item></el-col>
        </el-row>
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

const auth = useAuthStore()
const items = ref<any[]>([])
const subjects = ref<any[]>([])
const subjectMap = computed(() => Object.fromEntries((subjects.value || []).map((s: any) => [s.id, s])))
const keyword = ref('')
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const dialogVisible = ref(false)

const emptyForm = () => ({
  id: null as number | null,
  teacher_no: '',
  name: '',
  gender: 'male',
  phone: '',
  title: '',
  main_subject_id: null as number | null,
  subject_ids: [] as number[],
  max_weekly_hours: 20,
  max_daily_hours: 4,
  status: 'active'
})
const form = reactive(emptyForm())

async function load() {
  const [t, subj]: any = await Promise.all([
    api.teachers.list({ keyword: keyword.value, page: page.value, page_size: pageSize.value }),
    api.subjects.list()
  ])
  items.value = t?.items || []
  total.value = t?.total || items.value.length
  subjects.value = subj || []
}

function openDialog(row?: any) {
  Object.assign(form, emptyForm())
  if (row) Object.assign(form, row, { subject_ids: [...(row.subject_ids || [])] })
  dialogVisible.value = true
}

async function save() {
  if (!form.name || !form.teacher_no) {
    ElMessage.warning('请填写工号和姓名')
    return
  }
  const payload = { ...form }
  if (form.id) await api.teachers.update(form.id, payload)
  else await api.teachers.create(payload)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  load()
}

async function removeItem(row: any) {
  await ElMessageBox.confirm(`确定删除 ${row.name} 吗？`, '提示', { type: 'warning' })
  await api.teachers.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.header { display: flex; gap: 8px; align-items: center; }
.page { padding: 16px; }
</style>
