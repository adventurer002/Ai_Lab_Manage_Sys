import request from '@/utils/request'

/** 获取当前用户信息 */
export function getUserInfoApi() {
  return request({
    url: '/v1/user/info',
    method: 'get'
  })
}

/** 修改个人信息 */
export function updateUserInfoApi(data) {
  return request({
    url: '/v1/user/update',
    method: 'put',
    data
  })
}

/** 修改密码 */
export function updatePasswordApi(data) {
  return request({
    url: '/v1/user/password',
    method: 'put',
    data
  })
}

/**
 * 分页模糊查询用户列表
 */
export function getUserPageList(params) {
  return request({
    url: '/v1/user/list',
    method: 'get',
    params
  })
}

/**
 * 管理员新增用户
 */
export function createUserApi(data) {
  return request({
    url: '/v1/user',
    method: 'post',
    data
  })
}

/**
 * 管理员更新用户
 */
export function updateUserApi(userId, data) {
  return request({
    url: `/v1/user/${userId}`,
    method: 'put',
    data
  })
}

/**
 * 管理员删除用户
 */
export function deleteUserApi(userId) {
  return request({
    url: `/v1/user/${userId}`,
    method: 'delete'
  })
}
