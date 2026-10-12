<template>
  <div class="my-reservation-page p-4">
    <ElCard class="mb-4">
      <ElForm :inline="true" :model="search">
        <ElFormItem label="状态">
          <ElSelect v-model="search.status" placeholder="全部" clearable style="width: 140px">
            <ElOption label="待审核" :value="0" />
            <ElOption label="已通过" :value="1" />
            <ElOption label="已拒绝" :value="2" />
            <ElOption label="已取消" :value="3" />
            <ElOption label="已过期" :value="4" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem>
          <ElButton type="primary" @click="handleSearch">查询</ElButton>
          <ElButton @click="resetSearchParams">重置</ElButton>
        </ElFormItem>
      </ElForm>
    </ElCard>

    <ElCard class="art-table-card">
      <ArtTableHeader v-model:columns="columnChecks" :loading="loading" @refresh="refreshData" />

      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { useTable } from '@/hooks/core/useTable'
  import {
    fetchReservationList,
    fetchCancelReservation,
    fetchDeleteReservation,
    RESERVATION_STATUS,
    type ReservationItem
  } from '@/api/reservation'
  import { h, reactive } from 'vue'
  import { ElTag, ElMessageBox } from 'element-plus'

  defineOptions({ name: 'MyReservation' })

  const search = reactive({ status: undefined as number | undefined })

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
      apiFn: fetchReservationList,
      apiParams: { page: 1, page_size: 20, ...search },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'lab_name', label: '实验室', minWidth: 140 },
        { prop: 'equipment_name', label: '设备', minWidth: 140 },
        { prop: 'date', label: '日期', width: 120 },
        {
          prop: 'time',
          label: '时间段',
          width: 140,
          formatter: (row: ReservationItem) => `${row.start_time} - ${row.end_time}`
        },
        {
          prop: 'status',
          label: '状态',
          width: 100,
          formatter: (row: ReservationItem) => {
            const cfg = RESERVATION_STATUS[row.status] || { text: '未知', type: 'info' }
            return h(ElTag, { type: cfg.type }, () => cfg.text)
          }
        },
        { prop: 'remark', label: '备注', minWidth: 160 },
        {
          prop: 'operation',
          label: '操作',
          width: 120,
          fixed: 'right',
          formatter: (row: ReservationItem) => {
            if (row.status === 0 || row.status === 1) {
              return h(
                'button',
                {
                  class: 'el-button el-button--text el-button--danger',
                  onClick: () => cancelReservation(row)
                },
                '取消预约'
              )
            }
            if (row.status === 3 || row.status === 4) {
              return h(
                'button',
                {
                  class: 'el-button el-button--text el-button--danger',
                  onClick: () => deleteReservation(row)
                },
                '删除'
              )
            }
            return '-'
          }
        }
      ]
    }
  })

  const handleSearch = () => {
    replaceSearchParams(search)
    getData()
  }

  const cancelReservation = (row: ReservationItem) => {
    ElMessageBox.confirm('确定取消该预约吗？', '取消预约', { type: 'warning' }).then(async () => {
      await fetchCancelReservation(row.id)
      ElMessage.success('已取消')
      refreshData()
    })
  }

  const deleteReservation = (row: ReservationItem) => {
    ElMessageBox.confirm('确定删除该预约记录吗？删除后不可恢复', '删除预约', {
      type: 'warning'
    }).then(async () => {
      await fetchDeleteReservation(row.id)
      ElMessage.success('已删除')
      refreshData()
    })
  }
</script>
