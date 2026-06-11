<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <el-select v-model="filterType" placeholder="全部类型" clearable style="width: 160px" @change="load">
            <el-option label="普通教室" value="classroom" />
            <el-option label="实验室" value="lab" />
            <el-option label="功能室" value="special" />
            <el-option label="户外场地" value="outdoor" />
          </el-select>
          <el-button type="primary" @click="load">查询</el-button>
          <el-button v-if="auth.canEdit" type="success" @click="openDialog()">新增教室</el-button>
        </div>
      </template>
      <el-table :data="items" border stripe>
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column label="类型" width="110">
          <template #default="s"><el-tag :type="typeTag(s.row.type)">{{ s.row.type }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="capacity" label="容量" width="90" />
        <el-table-column prop="location" label="位置" width="160" />
        <el-table-column label="可用科目" min-width="200">
          <template #default="s">
            <el-tag v-for="sid in s.row.subject_ids || []" :key="sid" size="small" style="margin: 2px">{{ subjectMap[sid]?.name || sid }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="s">
            <el-button v-if="auth.canEdit" link type="primary" @click="openDialog(s.row)">编辑</el-button>
            <el-button v-if="auth.canEdit" link type="danger" @click="removeItem(s.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑教室' : '新增教室'" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="普通教室" value="classroom" />
            <el-option label="实验室" value="lab" />
            <el-option label="功能室" value="special" />
            <el-option label="户外场地" value="outdoor" />
          </el-select>
        </el-form-item>
        <el-form-item label="容量"><el-input-number v-model="form.capacity" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="位置"><el-input v-model="form.location" /></el-form-item>
        <el-form-item label="可用科目">
          <el-select v-model="form.subject_ids" multiple collapse-tags style="width: 100%">
            <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
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

const auth = useAuthStore()
const items = ref<any[]>([])
const subjects = ref<any[]>([])
const subjectMap = computed(() => Object.fromEntries(subjects.value.map((s: any) => [s.id, s])))
const filterType = ref('')
const dialogVisible = ref(false)

function typeTag(t: string) {
  return ({ lab: 'warning', special: 'success', outdoor: 'info' } as any)[t] || ''
}

const emptyForm = () => ({
  id: null as number | null,
  name: '',
  type: 'classroom',
  capacity: 40,
  location: '',
  subject_ids: [] as number[]
})
const form = reactive(emptyForm())

async function load() {
  const [cls, subj]: any = await Promise.all([
    api.classrooms.list({ type: filterType.value || undefined }),
    api.subjects.list()
  ])
  items.value = cls || []
  subjects.value = subj || []
}

function openDialog(row?: any) {
  Object.assign(form, emptyForm())
  if (row) Object.assign(form, row, { subject_ids: [...(row.subject_ids || [])] })
  dialogVisible.value = true
}

async function save() {
  if (!form.name) return ElMessage.warning('请填写名称')
  if (form.id) await api.classrooms.update(form.id, form)
  else await api.classrooms.create(form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  load()
}

async function removeItem(row: any) {
  await ElMessageBox.confirm(`确定删除 ${row.name} 吗？`, '提示', { type: 'warning' })
  await api.classrooms.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.header { display: flex; gap: 8px; align-items: center; }
.page { padding: 16px; }
</style>
