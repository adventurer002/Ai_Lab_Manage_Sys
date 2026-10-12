<template>
  <div class="lab-manage-page p-4">
    <ElCard class="mb-4">
      <ElForm :inline="true" :model="search">
        <ElFormItem label="关键字">
          <ElInput
            v-model="search.keyword"
            placeholder="名称/位置"
            clearable
            @keyup.enter="getData"
          />
        </ElFormItem>
        <ElFormItem label="状态">
          <ElSelect v-model="search.status" placeholder="全部" clearable style="width: 120px">
            <ElOption label="开放" :value="1" />
            <ElOption label="关闭" :value="0" />
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
          <ElButton type="primary" @click="showDialog('add')">新增实验室</ElButton>
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
      :title="dialogType === 'add' ? '新增实验室' : '编辑实验室'"
      width="600px"
      :close-on-click-modal="false"
    >
      <ElForm ref="formRef" :model="form" :rules="rules" label-width="90px">
        <ElFormItem label="名称" prop="name">
          <ElInput v-model="form.name" />
        </ElFormItem>
        <ElFormItem label="位置" prop="location">
          <ElInput v-model="form.location" />
        </ElFormItem>
        <ElFormItem label="容纳人数" prop="capacity">
          <ElInputNumber v-model="form.capacity" :min="0" />
        </ElFormItem>
        <ElFormItem label="开放时间" prop="open_time">
          <ElTimePicker v-model="form.open_time" value-format="HH:mm" placeholder="开始时间" />
          <ElTimePicker v-model="form.close_time" value-format="HH:mm" placeholder="结束时间" />
        </ElFormItem>
        <ElFormItem label="图片">
          <ElUpload
            :show-file-list="false"
            :auto-upload="true"
            accept="image/*"
            :http-request="handleImgUpload"
            :before-upload="beforeImgUpload"
          >
            <img :src="previewImgUrl" class="lab-upload-preview" alt="实验室图片" />
          </ElUpload>
          <div v-if="imgUploading" class="mt-2 text-xs text-g-500">上传中...</div>
          <div v-else class="mt-2 text-xs text-g-400">点击图片上传（支持 JPG/PNG，最大 2MB）</div>
        </ElFormItem>
        <ElFormItem label="状态" prop="status">
          <ElRadioGroup v-model="form.status">
            <ElRadio :value="1">开放</ElRadio>
            <ElRadio :value="0">关闭</ElRadio>
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
    fetchLabList,
    fetchCreateLab,
    fetchUpdateLab,
    fetchDeleteLab,
    type LabItem
  } from '@/api/lab'
  import { fetchUploadFile } from '@/api/file'
  import { h, ref, reactive, nextTick, computed } from 'vue'
  import {
    ElTag,
    ElMessageBox,
    ElMessage,
    type FormInstance,
    type FormRules,
    type UploadRequestOptions
  } from 'element-plus'
  import defaultLabImg from '@/assets/images/lab/lab.png'

  defineOptions({ name: 'LabManage' })

  const search = reactive({ keyword: '', status: undefined as number | undefined })

  const dialogType = ref<'add' | 'edit'>('add')
  const dialogVisible = ref(false)
  const submitting = ref(false)
  const formRef = ref<FormInstance>()
  const current = ref<LabItem | null>(null)

  const form = reactive({
    name: '',
    location: '',
    capacity: 0,
    open_time: '',
    close_time: '',
    img: '',
    status: 1,
    description: ''
  })

  const imgUploading = ref(false)

  // 图片预览：已选图片优先，否则默认图片
  const previewImgUrl = computed(() => {
    if (!form.img) return defaultLabImg
    return form.img.startsWith('http') ? form.img : `/uploads/${form.img}`
  })

  // 上传前校验
  const beforeImgUpload = (file: File) => {
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
  const handleImgUpload = async (options: UploadRequestOptions) => {
    imgUploading.value = true
    try {
      const res = await fetchUploadFile(options.file)
      form.img = res.disk_name
      ElMessage.success('图片上传成功')
    } catch (e) {
      // 错误已由 http 层统一提示
    } finally {
      imgUploading.value = false
    }
  }

  const rules: FormRules = {
    name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
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
      apiFn: fetchLabList,
      apiParams: { page: 1, page_size: 20, ...search },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'name', label: '名称', minWidth: 140 },
        { prop: 'location', label: '位置', minWidth: 140 },
        { prop: 'capacity', label: '容纳人数', width: 100 },
        {
          prop: 'open_time',
          label: '开放时间',
          width: 160,
          formatter: (row: LabItem) =>
            row.open_time ? `${row.open_time} - ${row.close_time || ''}` : '-'
        },
        {
          prop: 'status',
          label: '状态',
          width: 90,
          formatter: (row: LabItem) =>
            h(ElTag, { type: row.status === 1 ? 'success' : 'danger' }, () =>
              row.status === 1 ? '开放' : '关闭'
            )
        },
        {
          prop: 'operation',
          label: '操作',
          width: 160,
          fixed: 'right',
          formatter: (row: LabItem) =>
            h('div', [
              h(
                'button',
                { class: 'el-button el-button--text', onClick: () => showDialog('edit', row) },
                '编辑'
              ),
              h(
                'button',
                {
                  class: 'el-button el-button--text el-button--danger',
                  onClick: () => deleteLab(row)
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

  const showDialog = (type: 'add' | 'edit', row?: LabItem) => {
    dialogType.value = type
    current.value = row || null
    if (row) {
      Object.assign(form, {
        name: row.name,
        location: row.location || '',
        capacity: row.capacity,
        open_time: row.open_time || '',
        close_time: row.close_time || '',
        img: row.img || '',
        status: row.status,
        description: row.description || ''
      })
    } else {
      Object.assign(form, {
        name: '',
        location: '',
        capacity: 0,
        open_time: '',
        close_time: '',
        img: '',
        status: 1,
        description: ''
      })
    }
    nextTick(() => {
      dialogVisible.value = true
    })
  }

  const deleteLab = (row: LabItem) => {
    ElMessageBox.confirm(`确定删除实验室「${row.name}」吗？`, '删除确认', {
      type: 'warning'
    }).then(async () => {
      await fetchDeleteLab(row.id)
      ElMessage.success('删除成功')
      refreshData()
    })
  }

  const handleSubmit = async () => {
    if (!formRef.value) return
    try {
      await formRef.value.validate()
      submitting.value = true
      const payload = {
        name: form.name,
        location: form.location || null,
        capacity: form.capacity,
        open_time: form.open_time || null,
        close_time: form.close_time || null,
        img: form.img || null,
        status: form.status,
        description: form.description || null
      }
      if (dialogType.value === 'add') {
        await fetchCreateLab(payload)
      } else if (current.value) {
        await fetchUpdateLab(current.value.id, payload)
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

<style scoped lang="scss">
  .lab-upload-preview {
    width: 160px;
    height: 100px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid var(--default-border);
    cursor: pointer;
  }
</style>
