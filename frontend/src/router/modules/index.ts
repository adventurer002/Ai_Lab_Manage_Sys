import { AppRouteRecord } from '@/types/router'
import { labRoutes } from './lab'

/**
 * 导出所有模块化路由
 * 仅保留实验室业务路由
 */
export const routeModules: AppRouteRecord[] = [labRoutes]
