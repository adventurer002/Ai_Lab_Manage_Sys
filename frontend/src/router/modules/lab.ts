import { AppRouteRecord } from '@/types/router'

/**
 * 实验室预约系统业务路由
 * 角色取值：学生 / 教师 / 管理员
 */
export const labRoutes: AppRouteRecord = {
  path: '/',
  name: 'LabRoot',
  component: '/index/index',
  redirect: '/home',
  meta: {
    title: '实验室',
    icon: 'ep:office-building'
  },
  children: [
    {
      path: 'home',
      name: 'Home',
      component: '/lab/home',
      meta: {
        title: '系统首页',
        icon: 'ep:home-filled',
        keepAlive: true
      }
    },
    {
      path: 'lab/list',
      name: 'LabList',
      component: '/lab/lab-list',
      meta: {
        title: '实验室列表',
        icon: 'ep:office-building',
        keepAlive: true
      }
    },
    {
      path: 'lab/equipment/:labId',
      name: 'LabEquipment',
      component: '/lab/lab-equipment',
      meta: {
        title: '实验室设备',
        icon: 'ep:cpu',
        isHide: true,
        keepAlive: true,
        activePath: '/lab/list'
      }
    },
    {
      path: 'lab/manage',
      name: 'LabManage',
      component: '/lab/lab-manage',
      meta: {
        title: '实验室管理',
        icon: 'ep:school',
        keepAlive: true,
        roles: ['管理员']
      }
    },
    {
      path: 'equipment',
      name: 'Equipment',
      component: '/lab/equipment',
      meta: {
        title: '设备管理',
        icon: 'ep:tools',
        keepAlive: true,
        roles: ['管理员']
      }
    },
    {
      path: 'user',
      name: 'UserManage',
      component: '/lab/user-manage',
      meta: {
        title: '用户管理',
        icon: 'ep:user',
        keepAlive: true,
        roles: ['管理员']
      }
    },
    {
      path: 'reservation/my',
      name: 'MyReservation',
      component: '/lab/my-reservation',
      meta: {
        title: '我的预约',
        icon: 'ep:calendar',
        keepAlive: true,
        roles: ['学生', '教师']
      }
    },
    {
      path: 'reservation/audit',
      name: 'AuditReservation',
      component: '/lab/audit-reservation',
      meta: {
        title: '预约审核',
        icon: 'ep:finished',
        keepAlive: true,
        roles: ['管理员']
      }
    },
    {
      path: 'ai-chat',
      name: 'AIChat',
      component: '/lab/ai-chat',
      meta: {
        title: 'AI 智能助手',
        icon: 'ep:chat-dot-round',
        keepAlive: true
      }
    },
    {
      path: 'profile',
      name: 'Profile',
      component: '/lab/profile',
      meta: {
        title: '个人中心',
        icon: 'ep:user-filled',
        isHide: true,
        keepAlive: true
      }
    },
    {
      path: 'password',
      name: 'Password',
      component: '/lab/password',
      meta: {
        title: '修改密码',
        icon: 'ep:lock',
        isHide: true,
        keepAlive: true
      }
    }
  ]
}