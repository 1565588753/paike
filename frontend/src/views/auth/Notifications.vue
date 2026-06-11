<template>
  <div class="notification-view">
    <el-card shadow="never">
      <template #header>消息中心</template>
      <el-empty v-if="!list.length" description="暂无消息" />
      <el-timeline v-else>
        <el-timeline-item
          v-for="n in list"
          :key="n.id"
          :type="n.is_read ? 'info' : 'primary'"
          :timestamp="n.created_at"
          placement="top"
        >
          <el-card>
            <h4>{{ n.title }}</h4>
            <p>{{ n.content }}</p>
            <el-tag size="small">{{ n.type }}</el-tag>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const list = ref<any[]>([])

onMounted(async () => {
  const res: any = await request.get('/notifications')
  list.value = res.data || []
})
</script>

<style scoped>
.notification-view h4 { margin: 0 0 6px; }
.notification-view p { color: #606266; margin: 0 0 10px; }
</style>
