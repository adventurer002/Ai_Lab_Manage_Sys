/**
 * 快速入口配置
 * 包含：应用列表、快速链接等配置
 * 通过 roles 字段控制可见角色，不填则所有角色可见
 */
import type { FastEnterConfig } from '@/types/config'

const fastEnterConfig: FastEnterConfig = {
  // 显示条件（屏幕宽度）
  minWidth: 1200,
  // 应用列表
  applications: [
    {
      name: '系统首页',
      description: '实验室概览与快捷入口',
      icon: 'ri:pie-chart-line',
      iconColor: '#377dff',
      enabled: true,
      order: 1,
      routeName: 'Home'
    },
    {
      name: '实验室列表',
      description: '浏览与预约实验室',
      icon: 'ri:building-2-line',
      iconColor: '#13DEB9',
      enabled: true,
      order: 2,
      routeName: 'LabList'
    },
    {
      name: 'AI 智能助手',
      description: '实验室智能问答',
      icon: 'ri:robot-2-line',
      iconColor: '#7A7FFF',
      enabled: true,
      order: 3,
      routeName: 'AIChat'
    },
    {
      name: '人员管理',
      description: '用户与权限管理',
      icon: 'ri:team-line',
      iconColor: '#fa896b',
      enabled: true,
      order: 4,
      routeName: 'UserManage',
      roles: ['管理员']
    },
    {
      name: '实验室管理',
      description: '实验室信息维护',
      icon: 'ri:settings-3-line',
      iconColor: '#ffb100',
      enabled: true,
      order: 5,
      routeName: 'LabManage',
      roles: ['管理员']
    },
    {
      name: '设备管理',
      description: '设备信息与状态管理',
      icon: 'ri:tools-line',
      iconColor: '#20c997',
      enabled: true,
      order: 6,
      routeName: 'Equipment',
      roles: ['管理员']
    },
    {
      name: '预约审核',
      description: '审核用户预约申请',
      icon: 'ri:checkbox-circle-line',
      iconColor: '#377dff',
      enabled: true,
      order: 7,
      routeName: 'AuditReservation',
      roles: ['管理员']
    }
  ],
  // 快速链接
  quickLinks: [
    {
      name: '我的预约',
      enabled: true,
      order: 1,
      routeName: 'MyReservation'
    },
    {
      name: '个人中心',
      enabled: true,
      order: 2,
      routeName: 'Profile'
    },
    {
      name: '修改密码',
      enabled: true,
      order: 3,
      routeName: 'Password'
    },
    {
      name: '登录',
      enabled: true,
      order: 4,
      routeName: 'Login'
    },
    {
      name: '注册',
      enabled: true,
      order: 5,
      routeName: 'Register'
    }
  ]
}

export default Object.freeze(fastEnterConfig)
