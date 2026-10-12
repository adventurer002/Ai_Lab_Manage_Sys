import request from '@/utils/http'

// 设备状态：0-维修 1-正常
export const EQUIPMENT_STATUS: Record<number, { text: string; type: 'warning' | 'success' }> = {
  0: { text: '维修中', type: 'warning' },
  1: { text: '正常', type: 'success' }
}

export interface EquipmentItem {
  id: number
  lab_id: number
  lab_name: string | null
  name: string
  description: string | null
  img: string | null
  spec: string | null
  quantity: number
  status: number
}

export interface EquipmentCreateParams {
  lab_id: number
  name: string
  description?: string | null
  img?: string | null
  spec?: string | null
  quantity?: number
  status?: number
}

export interface EquipmentUpdateParams extends Partial<EquipmentCreateParams> {}

export interface EquipmentListParams {
  page?: number
  page_size?: number
  keyword?: string
  lab_id?: number
}

// 设备列表
export function fetchEquipmentList(params: EquipmentListParams) {
  return request.get<{ items: EquipmentItem[]; total: number }>({
    url: '/api/equipment/list',
    params
  })
}

// 创建设备
export function fetchCreateEquipment(data: EquipmentCreateParams) {
  return request.post<EquipmentItem>({
    url: '/api/equipment',
    data
  })
}

// 更新设备
export function fetchUpdateEquipment(equipmentId: number, data: EquipmentUpdateParams) {
  return request.put<EquipmentItem>({
    url: `/api/equipment/${equipmentId}`,
    data
  })
}

// 删除设备
export function fetchDeleteEquipment(equipmentId: number) {
  return request.del({
    url: `/api/equipment/${equipmentId}`
  })
}
