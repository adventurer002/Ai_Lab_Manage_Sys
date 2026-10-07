import request from '@/utils/request'

/**
 * 登录请求
 */
export function loginApi(data) {
  return request({
    url: '/v1/auth/login',
    method: 'post',
    data
  })
}

export function registerApi(data) {
  return request({
    url: '/v1/auth/register',
    method: 'post',
    data
  })
}
