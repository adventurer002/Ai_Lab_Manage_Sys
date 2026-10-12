<template>
  <div class="lab-equipment-page p-4">
    <ElPageHeader :title="labName" @back="$router.back()" class="mb-4">
      <template #content>
        <span class="text-g-500">设备列表</span>
      </template>
    </ElPageHeader>

    <ElCard shadow="hover" v-loading="loading">
      <ElEmpty v-if="!list.length" description="该实验室暂无设备" />
      <ElTable v-else :data="list" stripe>
        <ElTableColumn type="index" width="60" label="序号" />
        <ElTableColumn prop="name" label="设备名称" min-width="160" />
        <ElTableColumn prop="spec" label="规格" min-width="140" />
        <ElTableColumn prop="quantity" label="数量" width="100" />
        <ElTableColumn label="状态" width="100">
          <template #default="{ row }">
            <ElTag :type="row.status === 1 ? 'success' : 'warning'">
              {{ row.status === 1 ? '正常' : '维修中' }}
            </ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="description" label="描述" min-width="200" />
        <ElTableColumn label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <ElButton
              type="primary"
              size="small"
              :disabled="row.status !== 1"
              @click="openReserve(row)"
            >
              {{ row.status === 1 ? '预约' : '维修中' }}
            </ElButton>
          </template>
        </ElTableColumn>
      </ElTable>
    </ElCard>

    <!-- 预约弹窗 -->
    <ReserveDialog
      v-model="reserveVisible"
      :lab-id="labId"
      :lab-name="labName"
      :equipment-id="reserveEquipmentId"
    />
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, computed } from 'vue'
  import { useRoute } from 'vue-router'
  import { fetchEquipmentList, type EquipmentItem } from '@/api/equipment'
  import { fetchLabDetail } from '@/api/lab'
  import ReserveDialog from '../lab-list/ReserveDialog.vue'

  defineOptions({ name: 'LabEquipment' })

  const route = useRoute()
  const labId = computed(() => Number(route.params.labId))
  const labName = ref('')
  const list = ref<EquipmentItem[]>([])
  const loading = ref(false)

  // 预约弹窗状态：预约某台设备时记录其 id，弹窗打开后自动选中
  const reserveVisible = ref(false)
  const reserveEquipmentId = ref<number | undefined>(undefined)

  const openReserve = (row: EquipmentItem) => {
    reserveEquipmentId.value = row.id
    reserveVisible.value = true
  }

  onMounted(async () => {
    loading.value = true
    try {
      const [lab, res] = await Promise.all([
        fetchLabDetail(labId.value),
        fetchEquipmentList({ lab_id: labId.value, page_size: 100 })
      ])
      labName.value = lab?.name || ''
      list.value = res.items
    } catch (e) {
      console.error(e)
    } finally {
      loading.value = false
    }
  })
</script>
