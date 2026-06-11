import request from '@/utils/request'

async function get(path: string, params?: any) {
  const res: any = await request.get(path, { params })
  return res?.data
}

async function post(path: string, data?: any, params?: any) {
  const res: any = await request.post(path, data, { params })
  return res?.data
}

async function put(path: string, data?: any) {
  const res: any = await request.put(path, data)
  return res?.data
}

async function del(path: string) {
  const res: any = await request.delete(path)
  return res?.data
}

export const api = {
  teachers: {
    list: (params?: any) => get('/teachers', params),
    create: (data: any) => post('/teachers', data),
    update: (id: number, data: any) => put(`/teachers/${id}`, data),
    remove: (id: number) => del(`/teachers/${id}`)
  },
  subjects: {
    list: (params?: any) => get('/subjects', params),
    create: (data: any) => post('/subjects', data),
    update: (id: number, data: any) => put(`/subjects/${id}`, data),
    remove: (id: number) => del(`/subjects/${id}`)
  },
  classes: {
    list: (params?: any) => get('/classes', params),
    create: (data: any) => post('/classes', data),
    update: (id: number, data: any) => put(`/classes/${id}`, data),
    remove: (id: number) => del(`/classes/${id}`)
  },
  grades: {
    list: () => get('/grades')
  },
  classrooms: {
    list: (params?: any) => get('/classrooms', params),
    create: (data: any) => post('/classrooms', data),
    update: (id: number, data: any) => put(`/classrooms/${id}`, data),
    remove: (id: number) => del(`/classrooms/${id}`)
  },
  schedulePlans: {
    list: () => get('/schedule-plans'),
    create: (data: any) => post('/schedule-plans', data),
    update: (id: number, data: any) => put(`/schedule-plans/${id}`, data),
    remove: (id: number) => del(`/schedule-plans/${id}`)
  },
  cycles: {
    list: () => get('/cycles')
  },
  hrRecords: {
    list: (params?: any) => get('/hr-records', params),
    create: (data: any) => post('/hr-records', data),
    update: (id: number, data: any) => put(`/hr-records/${id}`, data),
    remove: (id: number) => del(`/hr-records/${id}`)
  },
  weeklyHours: {
    list: (params?: any) => get('/weekly-hours', params),
    create: (data: any) => post('/weekly-hours', data),
    update: (id: number, data: any) => put(`/weekly-hours/${id}`, data),
    remove: (id: number) => del(`/weekly-hours/${id}`)
  },
  years: {
    list: () => get('/years'),
    create: (data: any) => post('/years', data),
    setCurrent: (id: number) => post(`/years/${id}/set-current`),
    archive: (id: number) => post(`/years/${id}/archive`),
    upgrade: (id: number, target_year_id: number) => post(`/years/${id}/upgrade`, { target_year_id }),
    semesters: (id: number) => get(`/years/${id}/semesters`),
    createSemester: (id: number, data: any) => post(`/years/${id}/semesters`, data),
    setSemesterCurrent: (id: number) => post(`/years/semesters/${id}/set-current`)
  },
  timetable: {
    versions: {
      list: (params?: any) => get('/timetable/versions', params),
      create: (params?: any) => post('/timetable/versions', null, params),
      publish: (id: number) => post(`/timetable/versions/${id}/publish`),
      remove: (id: number) => del(`/timetable/versions/${id}`),
      autoSchedule: (id: number) => post(`/timetable/versions/${id}/auto-schedule`),
      quality: (id: number) => get(`/timetable/versions/${id}/quality`)
    },
    entries: {
      list: (params?: any) => get('/timetable/entries', params),
      create: (data: any) => post('/timetable/entries', data),
      move: (id: number, data: any) => post(`/timetable/entries/${id}/move`, data),
      swap: (data: any) => post('/timetable/entries/swap', data),
      remove: (id: number) => del(`/timetable/entries/${id}`)
    }
  },
  swaps: {
    list: (params?: any) => get('/swaps', params),
    create: (data: any) => post('/swaps', data),
    confirm: (id: number) => post(`/swaps/${id}/confirm`),
    reject: (id: number) => post(`/swaps/${id}/reject`),
    approve: (id: number) => post(`/swaps/${id}/approve`)
  },
  stats: {
    teacherWorkload: (params?: any) => get('/stats/teacher-workload', params),
    subjectDistribution: (params?: any) => get('/stats/subject-distribution', params),
    classroomUtilization: (params?: any) => get('/stats/classroom-utilization', params)
  },
  specialDates: {
    list: (params?: any) => get('/special-dates', params),
    create: (data: any) => post('/special-dates', data),
    remove: (id: number) => del(`/special-dates/${id}`)
  }
}

export default api
