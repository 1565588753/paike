<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>科目列表</span>
          <el-button v-if="auth.canEdit" type="success" @click="openDialog()">新增科目</el-button>
        </div>
      </template>
      <el-table :data="items" border stripe>
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="name" label="名称" min-width="160">
          <template #default="s">
            <span class="color-dot" :style="{ background: s.row.color }"></span>{{ s.row.name }}
          </template>
        </el-table-column>
        <el-table-column prop="is_main" label="主科" width="80">
          <template #default="s"><el-tag v-if="s.row.is_main" type="primary">主科</el-tag></template>
        </el-table-column>
        <el-table-column prop="need_room" label="需教室" width="90">
          <template #default="s"><el-tag v-if="s.row.need_room" type="success">是</el-tag></template>
        </el-table-column>
        <el-table-column prop="color" label="颜色" width="120">
          <template #default="s"><span class="color-block" :style="{ background: s.row.color }">{{ s.row.color }}</span></template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="s">
            <el-button v-if="auth.canEdit" link type="primary" @click="openDialog(s.row)">编辑</el-button>
            <el-button v-if="auth.canEdit" link type="danger" @click="removeItem(s.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑科目' : '新增科目'" width="540px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="编码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="主科"><el-switch v-model="form.is_main" /></el-form-item>
        <el-form-item label="需教室"><el-switch v-model="form.need_room" /></el-form-item>
        <el-form-item label="颜色"><el-color-picker v-model="form.color" show-alpha /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const items = ref<any[]>([])
const dialogVisible = ref(false)

const emptyForm = () => ({
  id: null as number | null,
  code: '',
  name: '',
  is_main: false,
  need_room: true,
  color: '#409EFF',
  sort_order: 0
})
const form = reactive(emptyForm())

async function load() {
  items.value = (await api.subjects.list()) || []
}

function openDialog(row?: any) {
  Object.assign(form, emptyForm())
  if (row) Object.assign(form, row)
  dialogVisible.value = true
}

async function save() {
  if (!form.name) return ElMessage.warning('请填写名称')
  if (form.id) await api.subjects.update(form.id, form)
  else await api.subjects.create(form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  load()
}

async function removeItem(row: any) {
  await ElMessageBox.confirm(`确定删除 ${row.name} 吗？`, '提示', { type: 'warning' })
  await api.subjects.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.header { display: flex; gap: 8px; align-items: center; justify-content: space-between; }
.page { padding: 16px; }
.color-dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; vertical-align: middle; }
.color-block { display: inline-block; padding: 2px 8px; border-radius: 4px; color: #fff; font-size: 12px; }
</style>
