<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>排课时段计划</span>
          <el-button v-if="auth.canEdit" type="success" @click="openDialog()">新增计划</el-button>
        </div>
      </template>
      <el-table :data="items" border stripe>
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="默认" width="80">
          <template #default="s"><el-tag v-if="s.row.is_default" type="success">默认</el-tag></template>
        </el-table-column>
        <el-table-column label="时段明细" min-width="400">
          <template #default="s">
            <div class="slot-list">
              <el-tag v-for="slot in s.row.slots || []" :key="slot.id" size="small" :type="slot.is_break ? 'info' : ''" style="margin: 2px">
                {{ slot.period_no }}. {{ slot.period_name }} ({{ slot.start_time }}-{{ slot.end_time }})
              </el-tag>
            </div>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑计划' : '新增计划'" width="720px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="设为默认"><el-switch v-model="form.is_default" /></el-form-item>
        <el-form-item label="时段表">
          <el-table :data="form.slots" border size="small" style="width: 100%">
            <el-table-column label="节次" width="90">
              <template #default="s"><el-input-number v-model="form.slots[s.$index].period_no" :min="1" controls-position="right" style="width: 80px" /></template>
            </el-table-column>
            <el-table-column label="名称" width="140">
              <template #default="s"><el-input v-model="form.slots[s.$index].period_name" /></template>
            </el-table-column>
            <el-table-column label="开始" width="140">
              <template #default="s"><el-time-picker v-model="form.slots[s.$index].start_time" format="HH:mm" value-format="HH:mm" style="width: 100%" /></template>
            </el-table-column>
            <el-table-column label="结束" width="140">
              <template #default="s"><el-time-picker v-model="form.slots[s.$index].end_time" format="HH:mm" value-format="HH:mm" style="width: 100%" /></template>
            </el-table-column>
            <el-table-column label="课间" width="80">
              <template #default="s"><el-checkbox v-model="form.slots[s.$index].is_break" /></template>
            </el-table-column>
            <el-table-column label="排序" width="110">
              <template #default="s"><el-input-number v-model="form.slots[s.$index].sort_order" :min="0" controls-position="right" style="width: 80px" /></template>
            </el-table-column>
            <el-table-column label="操作" width="90">
              <template #default="s"><el-button link type="danger" @click="removeSlot(s.$index)">删除</el-button></template>
            </el-table-column>
          </el-table>
          <el-button style="margin-top: 8px" @click="addSlot()">+ 添加时段</el-button>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const items = ref<any[]>([])
const dialogVisible = ref(false)

const emptySlot = () => ({ id: null, period_no: 1, period_name: '第一节', start_time: '08:00', end_time: '08:45', is_break: false, sort_order: 1 })
const emptyForm = () => ({ id: null, name: '', description: '', is_default: false, slots: [emptySlot()] })
const form = reactive(emptyForm())

function addSlot() {
  const last = form.slots[form.slots.length - 1] || { period_no: 0, sort_order: 0 }
  form.slots.push({ ...emptySlot(), period_no: last.period_no + 1, sort_order: last.sort_order + 1 })
}
function removeSlot(idx: number) {
  form.slots.splice(idx, 1)
}

async function load() {
  items.value = (await api.schedulePlans.list()) || []
}

function openDialog(row?: any) {
  Object.assign(form, emptyForm())
  if (row) {
    Object.assign(form, row, { slots: (row.slots || []).map((s: any) => ({ ...s })) })
  }
  dialogVisible.value = true
}

async function save() {
  if (!form.name) return ElMessage.warning('请填写名称')
  if (form.id) await api.schedulePlans.update(form.id, form)
  else await api.schedulePlans.create(form)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  load()
}

async function removeItem(row: any) {
  await ElMessageBox.confirm(`确定删除 ${row.name} 吗？`, '提示', { type: 'warning' })
  await api.schedulePlans.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; }
.page { padding: 16px; }
.slot-list { line-height: 1.8; }
</style>
