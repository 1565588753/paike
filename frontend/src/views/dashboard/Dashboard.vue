<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col :span="6" v-for="(stat, i) in stats" :key="i">
        <el-card shadow="hover" :class="stat.color">
          <div class="stat-icon"><el-icon :size="36"><component :is="stat.icon" /></el-icon></div>
          <div class="stat-content">
            <div class="label">{{ stat.label }}</div>
            <div class="value">{{ stat.value }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>教师工作负载</template>
          <div ref="teacherChartRef" style="height: 320px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>课程分布</template>
          <div ref="subjectChartRef" style="height: 320px"></div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>最近换课申请</template>
          <el-table :data="swapList" size="small" v-if="swapList.length">
            <el-table-column prop="requester_teacher_id" label="申请人" />
            <el-table-column prop="target_teacher_id" label="对方" />
            <el-table-column prop="status" label="状态">
              <template #default="s">
                <el-tag :type="statusTag(s.row.status)">{{ s.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="requested_at" label="时间" />
          </el-table>
          <el-empty v-else description="暂无申请" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>课表版本质量</template>
          <el-table :data="versions" size="small">
            <el-table-column prop="version_no" label="版本" width="90" />
            <el-table-column prop="version_name" label="名称" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="s">
                <el-tag :type="s.row.status === 'published' ? 'success' : 'info'">{{ s.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quality_score" label="评分" width="90" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const appStore = useAppStore()
const auth = useAuthStore()
const teacherChartRef = ref<HTMLElement | null>(null)
const subjectChartRef = ref<HTMLElement | null>(null)
const teacherStats = ref<any[]>([])
const subjectStats = ref<any[]>([])
const swapList = ref<any[]>([])
const versions = ref<any[]>([])

const stats = computed(() => [
  { label: '教师总数', value: teacherStats.value.length, icon: 'User', color: 'c-blue' },
  { label: '课程条目', value: '-', icon: 'Document', color: 'c-green' },
  { label: '待审批换课', value: swapList.value.filter((s: any) => s.status === 'pending').length, icon: 'Refresh', color: 'c-orange' },
  { label: '已发布版本', value: versions.value.filter((v: any) => v.status === 'published').length, icon: 'Select', color: 'c-purple' }
])

function statusTag(s: string) {
  return { pending: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info'
}

onMounted(async () => {
  try {
    if (appStore.currentVersionId) {
      const [tw, sb, sw, v]: any = await Promise.all([
        request.get('/stats/teacher-workload', { params: { version_id: appStore.currentVersionId } }),
        request.get('/stats/subject-distribution', { params: { version_id: appStore.currentVersionId } }),
        request.get('/swaps'),
        appStore.loadVersions()
      ])
      teacherStats.value = tw.data || []
      subjectStats.value = sb.data || []
      swapList.value = (sw.data || []).slice(0, 10)
      versions.value = appStore.versions
    }
    renderCharts()
  } catch (e) {
    // silent
  }
})

function renderCharts() {
  if (teacherChartRef.value) {
    const chart = echarts.init(teacherChartRef.value)
    chart.setOption({
      tooltip: {},
      grid: { left: 50, right: 20, top: 30, bottom: 40 },
      xAxis: { type: 'category', data: teacherStats.value.map((t: any) => t.teacher_name).slice(0, 15) },
      yAxis: { type: 'value', name: '节数' },
      series: [{ type: 'bar', data: teacherStats.value.map((t: any) => t.hours).slice(0, 15), itemStyle: { color: '#409EFF' } }]
    })
  }
  if (subjectChartRef.value) {
    const chart = echarts.init(subjectChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        data: subjectStats.value.map((s: any) => ({ name: s.name, value: s.count }))
      }]
    })
  }
}
</script>

<style scoped>
.dashboard .el-card { margin-bottom: 0; }
.stat-icon { color: #fff; background: rgba(255,255,255,.25); padding: 10px; border-radius: 12px; }
.stat-content { margin-left: 14px; }
.stat-content .label { color: #fff; opacity: .85; font-size: 13px; }
.stat-content .value { color: #fff; font-size: 24px; font-weight: 600; margin-top: 4px; }
.c-blue { background: linear-gradient(135deg, #36a1ff, #0e61b4); color: #fff; }
.c-green { background: linear-gradient(135deg, #48c774, #2b7d45); color: #fff; }
.c-orange { background: linear-gradient(135deg, #ff9f43, #d1661f); color: #fff; }
.c-purple { background: linear-gradient(135deg, #9b59b6, #6c3483); color: #fff; }
.el-card :deep(.el-card__body) { display: flex; align-items: center; padding: 16px 20px; }
</style>
