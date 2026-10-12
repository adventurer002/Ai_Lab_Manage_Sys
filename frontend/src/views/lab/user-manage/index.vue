<template>
  <div class="user-manage-page p-4">
    <ElCard class="mb-4">
      <ElForm :inline="true" :model="search">
        <ElFormItem label="关键字">
          <ElInput
            v-model="search.keyword"
            placeholder="用户名/姓名"
            clearable
            @keyup.enter="getData"
          />
        </ElFormItem>
        <ElFormItem>
          <ElButton type="primary" @click="handleSearch">查询</ElButton>
          <ElButton @click="resetSearchParams">重置</ElButton>
        </ElFormItem>
      </ElForm>
    </ElCard>

    <ElCard class="art-table-card">
      <ArtTableHeader v-model:columns="columnChecks" :loading="loading" @refresh="refreshData">
        <template #left>
          <ElButton type="primary" @click="showDialog('add')">新增用户</ElButton>
        </template>
      </ArtTableHeader>

      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />
    </ElCard>

    <ElDialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增用户' : '编辑用户'"
      width="560px"
      :close-on-click-modal="false"
    >
      <ElForm ref="formRef" :model="form" :rules="rules" label-width="90px">
        <ElFormItem label="用户名" prop="username">
          <ElInput v-model="form.username" :disabled="dialogType === 'edit'" />
        </ElFormItem>
        <ElFormItem v-if="dialogType === 'add'" label="密码" prop="password">
          <ElInput v-model="form.password" type="password" show-password />
        </ElFormItem>
        <ElFormItem label="姓名" prop="name">
          <ElInput v-model="form.name" />
        </ElFormItem>
        <ElFormItem label="角色" prop="role">
          <ElSelect v-model="form.role" style="width: 100%">
            <ElOption v-for="r in ROLE_OPTIONS" :key="r.value" :label="r.label" :value="r.value" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="邮箱" prop="email">
          <ElInput v-model="form.email" />
        </ElFormItem>
        <ElFormItem label="手机号" prop="phone">
          <ElInput v-model="form.phone" />
        </ElFormItem>
        <ElFormItem label="状态" prop="status">
          <ElRadioGroup v-model="form.status">
            <ElRadio :value="1">启用</ElRadio>
            <ElRadio :value="0">禁用</ElRadio>
          </ElRadioGroup>
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="dialogVisible = false">取消</ElButton>
        <ElButton type="primary" :loading="submitting" @click="handleSubmit">确定</ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<script setup lang="ts">
  import { useTable } from '@/hooks/core/useTable'
  import {
    fetchUserList,
    fetchCreateUser,
    fetchUpdateUser,
    fetchDeleteUser,
    ROLE_OPTIONS,
    type UserItem
  } from '@/api/user'
  import { h, ref, reactive, nextTick } from 'vue'
  import { ElTag, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

  defineOptions({ name: 'UserManage' })

  const search = reactive({ keyword: '' })

  const dialogType = ref<'add' | 'edit'>('add')
  const dialogVisible = ref(false)
  const submitting = ref(false)
  const formRef = ref<FormInstance>()
  const current = ref<UserItem | null>(null)

  const form = reactive({
    username: '',
    password: '123',
    name: '',
    role: '学生',
    email: '',
    phone: '',
    status: 1
  })

  const rules: FormRules = {
    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
    name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
    role: [{ required: true, message: '请选择角色', trigger: 'change' }]
  }

  const {
    columns,
    columnChecks,
    data,
    loading,
    pagination,
    getData,
    replaceSearchParams,
    resetSearchParams,
    handleSizeChange,
    handleCurrentChange,
    refreshData
  } = useTable({
    core: {
      apiFn: fetchUserList,
      apiParams: { page: 1, page_size: 20, ...search },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'username', label: '用户名', width: 140 },
        { prop: 'name', label: '姓名', width: 120 },
        { prop: 'role', label: '角色', width: 100 },
        { prop: 'email', label: '邮箱', minWidth: 160 },
        { prop: 'phone', label: '手机号', width: 130 },
        {
          prop: 'status',
          label: '状态',
          width: 90,
          formatter: (row: UserItem) =>
            h(
              ElTag,
              { type: row.status === 1 ? 'success' : 'danger' },
              () => (row.status === 1 ? '启用' : '禁用')
            )
        },
        { prop: 'create_time', label: '创建时间', width: 170 },
        {
          prop: 'operation',
          label: '操作',
          width: 160,
          fixed: 'right',
          formatter: (row: UserItem) =>
            h('div', [
              h('button', { class: 'el-button el-button--text', onClick: () => showDialog('edit', row) }, '编辑'),
              h(
                'button',
                {
                  class: 'el-button el-button--text el-button--danger',
                  onClick: () => deleteUser(row)
                },
                '删除'
              )
            ])
        }
      ]
    }
  })

  const handleSearch = () => {
    replaceSearchParams(search)
    getData()
  }

  const showDialog = (type: 'add' | 'edit', row?: UserItem) => {
    dialogType.value = type
    current.value = row || null
    if (row) {
      Object.assign(form, {
        username: row.username,
        password: '123',
        name: row.name,
        role: row.role,
        email: row.email || '',
        phone: row.phone || '',
        status: row.status
      })
    } else {
      Object.assign(form, {
        username: '',
        password: '123',
        name: '',
        role: '学生',
        email: '',
        phone: '',
        status: 1
      })
    }
    nextTick(() => {
      dialogVisible.value = true
    })
  }

  const deleteUser = (row: UserItem) => {
    ElMessageBox.confirm(`确定删除用户「${row.name}」吗？`, '删除确认', { type: 'warning' }).then(
      async () => {
        await fetchDeleteUser(row.id)
        ElMessage.success('删除成功')
        refreshData()
      }
    )
  }

  const handleSubmit = async () => {
    if (!formRef.value) return
    try {
      await formRef.value.validate()
      submitting.value = true
      const payload = {
        username: form.username,
        password: form.password,
        name: form.name,
        role: form.role,
        email: form.email || null,
        phone: form.phone || null,
        status: form.status
      }
      if (dialogType.value === 'add') {
        await fetchCreateUser(payload)
      } else if (current.value) {
        await fetchUpdateUser(current.value.id, payload)
      }
      ElMessage.success(dialogType.value === 'add' ? '创建成功' : '更新成功')
      dialogVisible.value = false
      refreshData()
    } catch (e) {
      // ignore
    } finally {
      submitting.value = false
    }
  }
</script>
