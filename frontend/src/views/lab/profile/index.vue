<template>
  <div class="profile-page p-4">
    <ElRow :gutter="16">
      <ElCol :span="8">
        <ElCard shadow="hover" class="text-center">
          <ElAvatar :size="96" :src="avatarUrl">
            {{ (info.name || info.username || '?').charAt(0) }}
          </ElAvatar>
          <h3 class="mt-3 text-lg font-semibold">{{ info.name || info.username }}</h3>
          <p class="text-g-500">{{ info.role }}</p>
          <ElTag class="mt-2" type="success">{{ info.status === 1 ? '正常' : '禁用' }}</ElTag>
        </ElCard>
      </ElCol>
      <ElCol :span="16">
        <ElCard shadow="hover">
          <template #header>个人信息</template>
          <ElForm ref="formRef" :model="form" :rules="rules" label-width="90px">
            <ElFormItem label="用户名">
              <ElInput :model-value="info.username" disabled />
            </ElFormItem>
            <ElFormItem label="姓名" prop="name">
              <ElInput v-model="form.name" />
            </ElFormItem>
            <ElFormItem label="角色">
              <ElInput :model-value="info.role" disabled />
            </ElFormItem>
            <ElFormItem label="邮箱" prop="email">
              <ElInput v-model="form.email" />
            </ElFormItem>
            <ElFormItem label="手机号" prop="phone">
              <ElInput v-model="form.phone" />
            </ElFormItem>
            <ElFormItem label="头像">
              <ElUpload
                :show-file-list="false"
                :auto-upload="true"
                accept="image/*"
                :http-request="handleAvatarUpload"
                :before-upload="beforeAvatarUpload"
              >
                <ElAvatar :size="80" :src="previewAvatarUrl" class="cursor-pointer">
                  {{ (info.name || info.username || '?').charAt(0) }}
                </ElAvatar>
              </ElUpload>
              <div v-if="uploading" class="mt-2 text-xs text-g-500">上传中...</div>
              <div v-else class="mt-2 text-xs text-g-400"
                >点击头像上传图片（支持 JPG/PNG，最大 2MB）</div
              >
            </ElFormItem>
            <ElFormItem>
              <ElButton type="primary" :loading="loading" @click="handleSubmit">保存</ElButton>
            </ElFormItem>
          </ElForm>
        </ElCard>
      </ElCol>
    </ElRow>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted } from 'vue'
  import {
    ElMessage,
    type FormInstance,
    type FormRules,
    type UploadRequestOptions
  } from 'element-plus'
  import { fetchUpdateProfile } from '@/api/user'
  import { fetchUploadFile } from '@/api/file'
  import { useUserStore } from '@/store/modules/user'

  defineOptions({ name: 'Profile' })

  const userStore = useUserStore()
  const info = computed(() => userStore.info)
  const avatarUrl = computed(() => {
    const a = info.value.avatar
    if (!a) return ''
    return a.startsWith('http') ? a : `/uploads/${a}`
  })

  const formRef = ref<FormInstance>()
  const loading = ref(false)
  const uploading = ref(false)

  const form = reactive({
    name: '',
    email: '',
    phone: '',
    avatar: ''
  })

  // 头像预览：优先显示已选头像，其次显示已保存头像
  const previewAvatarUrl = computed(() => {
    if (form.avatar) {
      return form.avatar.startsWith('http') ? form.avatar : `/uploads/${form.avatar}`
    }
    return avatarUrl.value
  })

  const rules: FormRules = {
    name: [{ required: true, message: '请输入姓名', trigger: 'blur' }]
  }

  onMounted(() => {
    form.name = info.value.name || ''
    form.email = info.value.email || ''
    form.phone = info.value.phone || ''
    form.avatar = info.value.avatar || ''
  })

  // 上传前校验
  const beforeAvatarUpload = (file: File) => {
    const isImage = file.type.startsWith('image/')
    const isLt2M = file.size / 1024 / 1024 < 2
    if (!isImage) {
      ElMessage.error('只能上传图片文件')
      return false
    }
    if (!isLt2M) {
      ElMessage.error('图片大小不能超过 2MB')
      return false
    }
    return true
  }

  // 自定义上传
  const handleAvatarUpload = async (options: UploadRequestOptions) => {
    uploading.value = true
    try {
      const res = await fetchUploadFile(options.file)
      form.avatar = res.disk_name
      ElMessage.success('头像上传成功')
    } catch (e) {
      // 错误已由 http 层统一提示
    } finally {
      uploading.value = false
    }
  }

  const handleSubmit = async () => {
    if (!formRef.value) return
    try {
      await formRef.value.validate()
      loading.value = true
      const updated = await fetchUpdateProfile({
        name: form.name,
        email: form.email || null,
        phone: form.phone || null,
        avatar: form.avatar || null
      })
      userStore.setUserInfo({ ...info.value, ...updated })
      ElMessage.success('保存成功')
    } catch (e) {
      // ignore
    } finally {
      loading.value = false
    }
  }
</script>
