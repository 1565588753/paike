<template>
  <div class="page">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>统计看板</span>
          <el-select v-model="appStore.currentVersionId" placeholder="选择版本" style="width: 200px" @change="load">
            <el-option v-for="v in versions" :key="v.id" :label="v.version_name" :value="v.id" />
          </el-select>
          <el-button type="primary" @click="load">刷新</el-button>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col :span="8"><div class="stat-card c-blue"><div class="stat-label">教师总数</div><div class="stat-value">{{ teacherWorkload.length }}</div></div></el-col>
        <el-col :span="8"><div class="stat-card c-green"><div class="stat-label">课节总数</div><div class="stat-value">{{ totalEntries }}</div></div></el-col>
        <el-col :span="8"><div class="stat-card c-purple"><div class="stat-label">使用教室</div><div class="stat-value">{{ classroomUtilization.length }}</div></div></el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top: 16px">
        <el-col :span="12">
          <el-card shadow="never">
            <template #header>教师工作负载（周课时数）</template>
            <div ref="teacherChartRef" style="height: 360px"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never">
            <template #header>科目分布</template>
            <div ref="subjectChartRef" style="height: 360px"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top: 16px">
        <el-col :span="12">
          <el-card shadow="never">
            <template #header>教室使用率</template>
            <div ref="classroomChartRef" style="height: 360px"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never">
            <template #header>每日课节分布</template>
            <div ref="dayChartRef" style="height: 360px"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const versions = ref<any[]>([])
const teacherWorkload = ref<any[]>([])
const subjectDistribution = ref<any[]>([])
const classroomUtilization = ref<any[]>([])
const entries = ref<any[]>([])

const teacherChartRef = ref<HTMLElement | null>(null)
const subjectChartRef = ref<HTMLElement | null>(null)
const classroomChartRef = ref<HTMLElement | null>(null)
const dayChartRef = ref<HTMLElement | null>(null)

const totalEntries = computed(() => entries.value.length || teacherWorkload.value.reduce((a: number, b: any) => a + (b.hours || 0), 0))

function renderCharts() {
  if (teacherChartRef.value) {
    const chart = echarts.init(teacherChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 60, right: 20, top: 20, bottom: 60 },
      xAxis: { type: 'category', data: teacherWorkload.value.map((t: any) => t.teacher_name || t.name || t.teacher_id).slice(0, 30), axisLabel: { rotate: 35 } },
      yAxis: { type: 'value', name: '节数' },
      series: [{ type: 'bar', data: teacherWorkload.value.map((t: any) => t.hours || t.total || 0).slice(0, 30), itemStyle: { color: '#409EFF' }, label: { show: true, position: 'top' } }]
    })
  }
  if (subjectChartRef.value) {
    const chart = echarts.init(subjectChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['40%', '65%'],
        data: subjectDistribution.value.map((s: any) => ({ name: s.subject_name || s.name || s.subject_id, value: s.count || s.total || 1 }))
      }]
    })
  }
  if (classroomChartRef.value) {
    const chart = echarts.init(classroomChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 60, right: 20, top: 20, bottom: 60 },
      xAxis: { type: 'category', data: classroomUtilization.value.map((c: any) => c.classroom_name || c.name || c.classroom_id).slice(0, 30), axisLabel: { rotate: 35 } },
      yAxis: { type: 'value', name: '节数' },
      series: [{ type: 'bar', data: classroomUtilization.value.map((c: any) => c.count || c.total || 0).slice(0, 30), itemStyle: { color: '#67C23A' }, label: { show: true, position: 'top' } }]
    })
  }
  if (dayChartRef.value) {
    const byDay = [0, 0, 0, 0, 0, 0, 0]
    entries.value.forEach((e: any) => { if (e.day_of_week) byDay[e.day_of_week - 1]++ })
    const chart = echarts.init(dayChartRef.value)
    chart.setOption({
      tooltip: {},
      grid: { left: 50, right: 20, top: 30, bottom: 40 },
      xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
      yAxis: { type: 'value', name: '课节数' },
      series: [{ type: 'bar', data: byDay, itemStyle: { color: '#E6A23C' }, label: { show: true, position: 'top' } }]
    })
  }
}

async function load() {
  if (!appStore.currentYearId) await appStore.loadYears()
  if (!appStore.currentSemesterId) await appStore.loadSemesters()
  const [v, tw, sd, cu]: any = await Promise.all([
    api.timetable.versions.list({ academic_year_id: appStore.currentYearId, semester_id: appStore.currentSemesterId }),
    appStore.currentVersionId ? api.stats.teacherWorkload({ version_id: appStore.currentVersionId }) : [],
    appStore.currentVersionId ? api.stats.subjectDistribution({ version_id: appStore.currentVersionId }) : [],
    appStore.currentVersionId ? api.stats.classroomUtilization({ version_id: appStore.currentVersionId }) : []
  ])
  versions.value = v || []
  if (!appStore.currentVersionId && versions.value.length) appStore.currentVersionId = versions.value[0].id
  teacherWorkload.value = tw || []
  subjectDistribution.value = sd || []
  classroomUtilization.value = cu || []
  entries.value = (appStore.currentVersionId ? (await api.timetable.entries.list({ version_id: appStore.currentVersionId })) : []) || []
  await nextTick()
  renderCharts()
}

onMounted(load)
</script>

<style scoped>
.header { display: flex; gap: 10px; align-items: center; font-weight: 600; }
.page { padding: 16px; }
.stat-card { color: #fff; padding: 20px; border-radius: 10px; }
.stat-card .stat-label { opacity: .85; font-size: 13px; }
.stat-card .stat-value { font-size: 28px; font-weight: 700; margin-top: 6px; }
.c-blue { background: linear-gradient(135deg, #36a1ff, #0e61b4); }
.c-green { background: linear-gradient(135deg, #48c774, #2b7d45); }
.c-purple { background: linear-gradient(135deg, #9b59b6, #6c3483); }
</style>
