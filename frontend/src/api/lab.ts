import request from '@/utils/http'

// 实验室状态：0-关闭 1-开放
export const LAB_STATUS: Record<number, { text: string; type: 'danger' | 'success' }> = {
  0: { text: '关闭', type: 'danger' },
  1: { text: '开放', type: 'success' }
}

export interface LabItem {
  id: number
  name: string
  location: string | null
  capacity: number
  open_time: string | null
  close_time: string | null
  description: string | null
  img: string | null
  status: number
}

export interface LabCreateParams {
  name: string
  location?: string | null
  capacity?: number
  open_time?: string | null
  close_time?: string | null
  description?: string | null
  img?: string | null
  status?: number
}

export interface LabUpdateParams extends Partial<LabCreateParams> {}

export interface LabListParams {
  page?: number
  page_size?: number
  keyword?: string
  status?: number
}

// 实验室列表
export function fetchLabList(params: LabListParams) {
  return request.get<{ items: LabItem[]; total: number }>({
    url: '/api/lab/list',
    params
  })
}

// 实验室详情
export function fetchLabDetail(labId: number) {
  return request.get<LabItem>({
    url: `/api/lab/${labId}`
  })
}

// 创建实验室
export function fetchCreateLab(data: LabCreateParams) {
  return request.post<LabItem>({
    url: '/api/lab',
    data
  })
}

// 更新实验室
export function fetchUpdateLab(labId: number, data: LabUpdateParams) {
  return request.put<LabItem>({
    url: `/api/lab/${labId}`,
    data
  })
}

// 删除实验室
export function fetchDeleteLab(labId: number) {
  return request.del({
    url: `/api/lab/${labId}`
  })
}
