<template>
  <div class="equipment-page p-4">
    <ElCard class="mb-4">
      <ElForm :inline="true" :model="search">
        <ElFormItem label="关键字">
          <ElInput v-model="search.keyword" placeholder="设备名称" clearable @keyup.enter="getData" />
        </ElFormItem>
        <ElFormItem label="所属实验室">
          <ElSelect v-model="search.lab_id" placeholder="全部" clearable style="width: 180px">
            <ElOption v-for="lab in labs" :key="lab.id" :label="lab.name" :value="lab.id" />
          </ElSelect>
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
          <ElButton type="primary" @click="showDialog('add')">新增设备</ElButton>
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
      :title="dialogType === 'add' ? '新增设备' : '编辑设备'"
      width="600px"
      :close-on-click-modal="false"
    >
      <ElForm ref="formRef" :model="form" :rules="rules" label-width="90px">
        <ElFormItem label="所属实验室" prop="lab_id">
          <ElSelect v-model="form.lab_id" placeholder="选择实验室" style="width: 100%">
            <ElOption v-for="lab in labs" :key="lab.id" :label="lab.name" :value="lab.id" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="设备名称" prop="name">
          <ElInput v-model="form.name" />
        </ElFormItem>
        <ElFormItem label="规格" prop="spec">
          <ElInput v-model="form.spec" />
        </ElFormItem>
        <ElFormItem label="数量" prop="quantity">
          <ElInputNumber v-model="form.quantity" :min="1" />
        </ElFormItem>
        <ElFormItem label="图片" prop="img">
          <ElInput v-model="form.img" placeholder="图片文件名" />
        </ElFormItem>
        <ElFormItem label="状态" prop="status">
          <ElRadioGroup v-model="form.status">
            <ElRadio :value="1">正常</ElRadio>
            <ElRadio :value="0">维修中</ElRadio>
          </ElRadioGroup>
        </ElFormItem>
        <ElFormItem label="描述" prop="description">
          <ElInput v-model="form.description" type="textarea" :rows="3" />
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
    fetchEquipmentList,
    fetchCreateEquipment,
    fetchUpdateEquipment,
    fetchDeleteEquipment,
    type EquipmentItem
  } from '@/api/equipment'
  import { fetchLabList, type LabItem } from '@/api/lab'
  import { h, ref, reactive, nextTick, onMounted } from 'vue'
  import { ElTag, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

  defineOptions({ name: 'Equipment' })

  const search = reactive({ keyword: '', lab_id: undefined as number | undefined })
  const labs = ref<LabItem[]>([])

  onMounted(async () => {
    try {
      const res = await fetchLabList({ page: 1, page_size: 100 })
      labs.value = res.items
    } catch (e) {
      console.error(e)
    }
  })

  const dialogType = ref<'add' | 'edit'>('add')
  const dialogVisible = ref(false)
  const submitting = ref(false)
  const formRef = ref<FormInstance>()
  const current = ref<EquipmentItem | null>(null)

  const form = reactive({
    lab_id: undefined as number | undefined,
    name: '',
    spec: '',
    quantity: 1,
    img: '',
    status: 1,
    description: ''
  })

  const rules: FormRules = {
    lab_id: [{ required: true, message: '请选择实验室', trigger: 'change' }],
    name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }]
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
      apiFn: fetchEquipmentList,
      apiParams: { page: 1, page_size: 20, ...search },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'name', label: '设备名称', minWidth: 140 },
        { prop: 'lab_name', label: '所属实验室', minWidth: 140 },
        { prop: 'spec', label: '规格', minWidth: 120 },
        { prop: 'quantity', label: '数量', width: 80 },
        {
          prop: 'status',
          label: '状态',
          width: 100,
          formatter: (row: EquipmentItem) =>
            h(
              ElTag,
              { type: row.status === 1 ? 'success' : 'warning' },
              () => (row.status === 1 ? '正常' : '维修中')
            )
        },
        {
          prop: 'operation',
          label: '操作',
          width: 160,
          fixed: 'right',
          formatter: (row: EquipmentItem) =>
            h('div', [
              h('button', { class: 'el-button el-button--text', onClick: () => showDialog('edit', row) }, '编辑'),
              h(
                'button',
                {
                  class: 'el-button el-button--text el-button--danger',
                  onClick: () => deleteEquip(row)
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

  const showDialog = (type: 'add' | 'edit', row?: EquipmentItem) => {
    dialogType.value = type
    current.value = row || null
    if (row) {
      Object.assign(form, {
        lab_id: row.lab_id,
        name: row.name,
        spec: row.spec || '',
        quantity: row.quantity,
        img: row.img || '',
        status: row.status,
        description: row.description || ''
      })
    } else {
      Object.assign(form, {
        lab_id: undefined,
        name: '',
        spec: '',
        quantity: 1,
        img: '',
        status: 1,
        description: ''
      })
    }
    nextTick(() => {
      dialogVisible.value = true
    })
  }

  const deleteEquip = (row: EquipmentItem) => {
    ElMessageBox.confirm(`确定删除设备「${row.name}」吗？`, '删除确认', { type: 'warning' }).then(
      async () => {
        await fetchDeleteEquipment(row.id)
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
        lab_id: form.lab_id as number,
        name: form.name,
        spec: form.spec || null,
        quantity: form.quantity,
        img: form.img || null,
        status: form.status,
        description: form.description || null
      }
      if (dialogType.value === 'add') {
        await fetchCreateEquipment(payload)
      } else if (current.value) {
        await fetchUpdateEquipment(current.value.id, payload)
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
