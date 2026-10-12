import request from '@/utils/http'

/**
 * 登录
 * @param params 登录参数 { username, password }
 * @returns 登录响应 { token, user }
 */
export function fetchLogin(params: Api.Auth.LoginParams) {
  return request.post<Api.Auth.LoginResponse>({
    url: '/api/auth/login',
    params
  })
}

/**
 * 获取用户信息
 * @returns 用户信息
 */
export function fetchGetUserInfo() {
  return request.get<Api.Auth.UserInfo>({
    url: '/api/user/info'
  })
}

/**
 * 注册
 * @param params 注册参数
 */
export function fetchRegister(params: Api.Auth.RegisterParams) {
  return request.post({
    url: '/api/auth/register',
    params
  })
}
