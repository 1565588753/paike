import { defineStore } from 'pinia'
import request from '@/utils/request'

interface Context {
  currentYearId: number | null
  currentSemesterId: number | null
  currentVersionId: number | null
  years: any[]
  semesters: any[]
  versions: any[]
}

export const useAppStore = defineStore('app', {
  state: (): Context => ({
    currentYearId: null,
    currentSemesterId: null,
    currentVersionId: null,
    years: [],
    semesters: [],
    versions: []
  }),
  persist: {
    key: 'app-context',
    storage: localStorage,
    paths: ['currentYearId', 'currentSemesterId', 'currentVersionId']
  },
  actions: {
    async loadYears() {
      const res: any = await request.get('/years')
      this.years = res.data || []
      if (!this.currentYearId) {
        const cur = this.years.find((y: any) => y.is_current) || this.years[0]
        if (cur) this.currentYearId = cur.id
      }
      return this.years
    },
    async loadSemesters() {
      if (!this.currentYearId) return []
      const res: any = await request.get(`/years/${this.currentYearId}/semesters`)
      this.semesters = res.data || []
      if (!this.currentSemesterId) {
        const cur = this.semesters.find((s: any) => s.is_current) || this.semesters[0]
        if (cur) this.currentSemesterId = cur.id
      }
      return this.semesters
    },
    async loadVersions() {
      if (!this.currentYearId || !this.currentSemesterId) return []
      const res: any = await request.get('/timetable/versions', {
        params: { academic_year_id: this.currentYearId, semester_id: this.currentSemesterId }
      })
      this.versions = res.data || []
      if (!this.currentVersionId) {
        const published = this.versions.find((v: any) => v.status === 'published') || this.versions[0]
        if (published) this.currentVersionId = published.id
      }
      return this.versions
    },
    setYear(id: number) {
      this.currentYearId = id
      this.currentSemesterId = null
      this.currentVersionId = null
    },
    setSemester(id: number) {
      this.currentSemesterId = id
      this.currentVersionId = null
    },
    setVersion(id: number) {
      this.currentVersionId = id
    }
  }
})
