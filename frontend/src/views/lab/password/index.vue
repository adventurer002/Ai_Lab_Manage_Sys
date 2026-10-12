<template>
  <div class="password-page p-4">
    <ElCard shadow="hover" style="max-width: 500px; margin: 40px auto;">
      <template #header>修改密码</template>
      <ElForm ref="formRef" :model="form" :rules="rules" label-width="100px">
        <ElFormItem label="原密码" prop="old_password">
          <ElInput v-model="form.old_password" type="password" show-password />
        </ElFormItem>
        <ElFormItem label="新密码" prop="new_password">
          <ElInput v-model="form.new_password" type="password" show-password />
        </ElFormItem>
        <ElFormItem label="确认密码" prop="confirm_password">
          <ElInput v-model="form.confirm_password" type="password" show-password />
        </ElFormItem>
        <ElFormItem>
          <ElButton type="primary" :loading="loading" @click="handleSubmit">确认修改</ElButton>
        </ElFormItem>
      </ElForm>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive } from 'vue'
  import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
  import { fetchUpdatePassword } from '@/api/user'
  import { useUserStore } from '@/store/modules/user'

  defineOptions({ name: 'Password' })

  const formRef = ref<FormInstance>()
  const loading = ref(false)
  const userStore = useUserStore()

  const form = reactive({
    old_password: '',
    new_password: '',
    confirm_password: ''
  })

  const validateConfirm = (_rule: any, value: string, callback: (e?: Error) => void) => {
    if (value !== form.new_password) {
      callback(new Error('两次密码不一致'))
    } else {
      callback()
    }
  }

  const rules: FormRules = {
    old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
    new_password: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      { min: 6, message: '密码至少 6 位', trigger: 'blur' }
    ],
    confirm_password: [
      { required: true, message: '请确认密码', trigger: 'blur' },
      { validator: validateConfirm, trigger: 'blur' }
    ]
  }

  const handleSubmit = async () => {
    if (!formRef.value) return
    try {
      await formRef.value.validate()
      loading.value = true
      await fetchUpdatePassword({
        old_password: form.old_password,
        new_password: form.new_password
      })
      ElMessage.success('密码修改成功，请重新登录')
      userStore.logOut()
    } catch (e) {
      // ignore
    } finally {
      loading.value = false
    }
  }
</script>
