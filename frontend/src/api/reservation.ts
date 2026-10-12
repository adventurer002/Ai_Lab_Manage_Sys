import request from '@/utils/http'

// 预约状态：0待审核 1已通过 2已拒绝 3已取消 4已过期
export const RESERVATION_STATUS: Record<
  number,
  { text: string; type: 'warning' | 'success' | 'danger' | 'info' }
> = {
  0: { text: '待审核', type: 'warning' },
  1: { text: '已通过', type: 'success' },
  2: { text: '已拒绝', type: 'danger' },
  3: { text: '已取消', type: 'info' },
  4: { text: '已过期', type: 'info' }
}

export interface ReservationItem {
  id: number
  user_id: number
  user_name: string | null
  lab_id: number
  lab_name: string | null
  equipment_id: number | null
  equipment_name: string | null
  type: string | null
  date: string
  start_time: string
  end_time: string
  remark: string | null
  status: number
}

export interface ReservationCreateParams {
  lab_id: number
  equipment_id?: number | null
  date: string
  start_time: string
  end_time: string
  remark?: string | null
}

export interface ReservationListParams {
  page?: number
  page_size?: number
  status?: number
}

// 预约列表
export function fetchReservationList(params: ReservationListParams) {
  return request.get<{ items: ReservationItem[]; total: number }>({
    url: '/api/reservation/list',
    params
  })
}

// 创建预约
export function fetchCreateReservation(data: ReservationCreateParams) {
  return request.post({
    url: '/api/reservation',
    data
  })
}

// 取消预约
export function fetchCancelReservation(reservationId: number) {
  return request.put({
    url: `/api/reservation/${reservationId}/cancel`
  })
}

// 删除预约（仅已取消/已过期）
export function fetchDeleteReservation(reservationId: number) {
  return request.del({
    url: `/api/reservation/${reservationId}`
  })
}

// 审核预约 status: 1通过 2拒绝
export function fetchAuditReservation(reservationId: number, status: number) {
  return request.put({
    url: `/api/reservation/${reservationId}/audit`,
    data: { status }
  })
}
