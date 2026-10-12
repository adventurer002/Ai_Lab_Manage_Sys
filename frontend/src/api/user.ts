import request from '@/utils/http'

// 用户状态：0-禁用 1-启用
export const USER_STATUS: Record<number, { text: string; type: 'danger' | 'success' }> = {
  0: { text: '禁用', type: 'danger' },
  1: { text: '启用', type: 'success' }
}

// 角色枚举
export const ROLE_OPTIONS = [
  { label: '学生', value: '学生' },
  { label: '教师', value: '教师' },
  { label: '管理员', value: '管理员' }
]

export interface UserItem {
  id: number
  username: string
  name: string
  role: string
  status: number
  email: string | null
  phone: string | null
  avatar: string | null
  create_time: string
  update_time: string
}

export interface UserCreateParams {
  username: string
  password?: string
  name?: string | null
  email?: string | null
  phone?: string | null
  avatar?: string | null
  role?: string
  status?: number
}

export interface UserUpdateParams {
  name?: string | null
  email?: string | null
  phone?: string | null
  avatar?: string | null
  role?: string | null
  status?: number
}

export interface UserListParams {
  page?: number
  page_size?: number
  keyword?: string
}

// 用户列表
export function fetchUserList(params: UserListParams) {
  return request.get<{ items: UserItem[]; total: number }>({
    url: '/api/user/list',
    params
  })
}

// 创建用户
export function fetchCreateUser(data: UserCreateParams) {
  return request.post<UserItem>({
    url: '/api/user',
    data
  })
}

// 更新用户
export function fetchUpdateUser(userId: number, data: UserUpdateParams) {
  return request.put<UserItem>({
    url: `/api/user/${userId}`,
    data
  })
}

// 删除用户
export function fetchDeleteUser(userId: number) {
  return request.del({
    url: `/api/user/${userId}`
  })
}

// 更新当前用户信息
export function fetchUpdateProfile(data: UserUpdateParams) {
  return request.put<UserItem>({
    url: '/api/user/update',
    data
  })
}

// 修改密码
export function fetchUpdatePassword(data: { old_password: string; new_password: string }) {
  return request.put({
    url: '/api/user/password',
    data
  })
}
