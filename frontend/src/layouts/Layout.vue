<template>
  <div>
    <el-container style="min-height: 100vh">
      <el-header
        style="
          display: flex;
          align-items: center;
          border-bottom: 1px solid #ddd;
          background-color: #fff;
        "
      >
        <div
          style="flex: 1; display: flex; align-items: center; font-size: 24px; font-weight: bold"
        >
          <img style="width: 40px" src="@/assets/imgs/logo.png" alt="" />
          <div style="margin-left: 5px">智能实验室预约系统</div>
        </div>
        <el-dropdown @command="handleCommand">
          <div style="display: flex; align-items: center; cursor: pointer">
            <img
              v-if="userInfo?.avatar"
              :src="userInfo.avatar"
              alt=""
              style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover"
            />
            <el-avatar v-else :size="30">{{ userInfo?.name?.charAt(0) || '用' }}</el-avatar>
            <div style="margin-left: 3px">{{ userInfo?.name }}</div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="password">修改密码</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-container>
        <el-aside width="220px">
          <el-menu router style="height: 100%" :default-active="route.path">
            <el-menu-item index="/manager/home">
              <el-icon><icon-menu /></el-icon>
              系统首页
            </el-menu-item>
            <el-menu-item index="/manager/lablist">
              <el-icon><OfficeBuilding /></el-icon>
              实验室列表
            </el-menu-item>
            <el-menu-item v-if="userInfo?.role === '管理员'" index="/manager/lab">
              <el-icon><House /></el-icon>
              实验室管理
            </el-menu-item>
            <el-menu-item v-if="userInfo?.role === '管理员'" index="/manager/equipment">
              <el-icon><Setting /></el-icon>
              设备列表管理
            </el-menu-item>
            <el-menu-item v-if="userInfo?.role === '管理员'" index="/manager/user">
              <el-icon><User /></el-icon>
              用户管理
            </el-menu-item>
            <el-menu-item index="/manager/my-reservation" v-if="userInfo?.role === '学生'">
              <el-icon><Tickets /></el-icon>
              我的预约
            </el-menu-item>
            <el-menu-item index="/manager/audit-reservation" v-if="userInfo?.role === '管理员'">
              <el-icon><DocumentChecked /></el-icon>
              预约审核
            </el-menu-item>
            <el-menu-item index="/manager/ai-chat">
              <el-icon><ChatDotRound /></el-icon>
              AI智能助手
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import {
  Menu as IconMenu,
  House,
  Setting,
  User,
  OfficeBuilding,
  Tickets,
  DocumentChecked,
  ChatDotRound
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import router from '@/router'
import { logout } from '@/utils/auth'

import { useUser } from '@/utils/user'
const route = useRoute()
const { userInfo } = useUser()

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/manager/profile')
  } else if (command === 'password') {
    router.push('/manager/password')
  } else if (command === 'logout') {
    logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  }
}
</script>

<style scoped>
.example-showcase .el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}
</style>
