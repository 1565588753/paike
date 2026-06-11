import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPersist from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './utils/request'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPersist)

for (const [key, component] of Object.entries(ElementPlusIcons)) {
  app.component(key, component as any)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.mount('#app')
