import request from '@/utils/request'

/**
 * 创建预约
 */
export function createReservationApi(data) {
  return request({
    url: '/v1/reservation',
    method: 'post',
    data
  })
}

/**
 * 查询预约记录
 */
export function getReservationPageList(params) {
  return request({
    url: '/v1/reservation/list',
    method: 'get',
    params
  })
}
/**
 * 取消预约
 */
export function cancelReservationApi(id) {
  return request({
    url: `/v1/reservation/${id}/cancel`,
    method: 'put'
  })
}
/**
 * 审核预约
 */
export function auditReservationApi(id, status) {
  return request({
    url: `/v1/reservation/${id}/audit`,
    method: 'put',
    data: { status }
  })
}
