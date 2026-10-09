import request from '@/utils/request'

/** 分页查询实验室 */
export function getLabPageList(params) {
  return request({
    url: '/v1/lab/list',
    method: 'get',
    params
  })
}

/** 新增实验室 */
export function createLabApi(data) {
  return request({
    url: '/v1/lab',
    method: 'post',
    data
  })
}

/** 修改实验室 */
export function updateLabApi(labId, data) {
  return request({
    url: `/v1/lab/${labId}`,
    method: 'put',
    data
  })
}

/** 删除实验室 */
export function deleteLabApi(labId) {
  return request({
    url: `/v1/lab/${labId}`,
    method: 'delete'
  })
}
/**
 * 根据ID查询实验室详情
 * @param {Number} lab_id
 * @returns
 */
export function getLab(lab_id) {
  return request({
    url: `/v1/lab/${lab_id}`,
    method: 'get'
  })
}
