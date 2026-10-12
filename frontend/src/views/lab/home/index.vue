<template>
  <div class="home-page p-4">
    <ElRow :gutter="16">
      <ElCol :span="6" v-for="card in statCards" :key="card.title">
        <ElCard shadow="hover" class="stat-card">
          <div class="flex items-center gap-3">
            <ElIcon :size="36" :color="card.color" class="stat-icon">
              <component :is="card.icon" />
            </ElIcon>
            <div>
              <p class="text-g-500 text-sm">{{ card.title }}</p>
              <p class="text-2xl font-semibold mt-1">{{ card.value }}</p>
            </div>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <ElRow :gutter="16" class="mt-4">
      <ElCol :span="14">
        <ElCard shadow="hover" class="h-full">
          <template #header>
            <span>实验室概览</span>
          </template>
          <ElEmpty v-if="!labStats.length" description="暂无实验室数据" />
          <ElTable v-else :data="labStats" stripe>
            <ElTableColumn prop="name" label="实验室名称" />
            <ElTableColumn prop="location" label="位置" />
            <ElTableColumn prop="capacity" label="容纳人数" width="100" />
            <ElTableColumn label="状态" width="100">
              <template #default="{ row }">
                <ElTag :type="row.status === 1 ? 'success' : 'danger'">
                  {{ row.status === 1 ? '开放' : '关闭' }}
                </ElTag>
              </template>
            </ElTableColumn>
          </ElTable>
        </ElCard>
      </ElCol>
      <ElCol :span="10">
        <ElCard shadow="hover" class="h-full">
          <template #header>
            <span>实验室设备数量分布</span>
          </template>
          <div ref="chartRef" class="chart-container"></div>
        </ElCard>
      </ElCol>
    </ElRow>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
  import * as echarts from 'echarts'
  import { OfficeBuilding, CircleCheck, User, UserFilled } from '@element-plus/icons-vue'
  import { fetchLabList, type LabItem } from '@/api/lab'
  import { fetchEquipmentList, type EquipmentItem } from '@/api/equipment'
  import { useUserStore } from '@/store/modules/user'

  defineOptions({ name: 'Home' })

  const userStore = useUserStore()
  const labs = ref<LabItem[]>([])
  const equipments = ref<EquipmentItem[]>([])
  const totalLabs = ref(0)
  const totalEquipments = ref(0)

  const chartRef = ref<HTMLElement>()
  let chartInstance: echarts.ECharts | null = null

  const labStats = computed(() => labs.value.slice(0, 8))

  const statCards = computed(() => [
    {
      title: '实验室总数',
      value: totalLabs.value,
      icon: OfficeBuilding,
      color: '#409eff'
    },
    {
      title: '设备总数',
      value: totalEquipments.value,
      icon: CircleCheck,
      color: '#67c23a'
    },
    {
      title: '当前角色',
      value: userStore.info.role || '-',
      icon: User,
      color: '#e6a23c'
    },
    {
      title: '用户名称',
      value: userStore.info.name || '-',
      icon: UserFilled,
      color: '#f56c6c'
    }
  ])

  // 初始化图表
  const initChart = () => {
    if (!chartRef.value) return
    chartInstance = echarts.init(chartRef.value)
    updateChart()
  }

  // 更新图表数据
  const updateChart = () => {
    if (!chartInstance) return

    // 按实验室统计设备数量，名称去掉"实验室"后缀
    const labEquipmentMap = new Map<string, number>()
    labs.value.forEach((lab) => {
      const shortName = lab.name.replace(/实验室$/, '')
      labEquipmentMap.set(shortName, 0)
    })
    equipments.value.forEach((eq) => {
      const name = (eq.lab_name || '未分配').replace(/实验室$/, '')
      labEquipmentMap.set(name, (labEquipmentMap.get(name) || 0) + (eq.quantity || 1))
    })

    const names = Array.from(labEquipmentMap.keys())
    const values = Array.from(labEquipmentMap.values())

    chartInstance.setOption({
      tooltip: {
        trigger: 'axis'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '10%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: names,
        boundaryGap: false,
        axisLabel: {
          rotate: names.length > 4 ? 30 : 0,
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        minInterval: 1,
        name: '实验室',
        nameTextStyle: { fontSize: 12, color: '#909399' }
      },
      series: [
        {
          name: '设备数量',
          type: 'line',
          smooth: true,
          data: values,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { width: 3, color: '#188df0' },
          itemStyle: { color: '#188df0' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(24, 141, 240, 0.3)' },
              { offset: 1, color: 'rgba(24, 141, 240, 0.02)' }
            ])
          },
          label: {
            show: true,
            position: 'top',
            fontSize: 12
          }
        }
      ]
    })
  }

  // 窗口大小变化时重绘
  const handleResize = () => {
    chartInstance?.resize()
  }

  onMounted(async () => {
    try {
      const [labRes, eqRes] = await Promise.all([
        fetchLabList({ page: 1, page_size: 100 }),
        fetchEquipmentList({ page: 1, page_size: 1000 })
      ])
      labs.value = labRes.items
      totalLabs.value = labRes.total
      equipments.value = eqRes.items
      totalEquipments.value = eqRes.items.reduce((sum, e) => sum + (e.quantity || 1), 0)
    } catch (e) {
      console.error(e)
    } finally {
      await nextTick()
      initChart()
      window.addEventListener('resize', handleResize)
    }
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
    chartInstance?.dispose()
    chartInstance = null
  })
</script>

<style scoped lang="scss">
  .stat-card {
    :deep(.el-card__body) {
      padding: 20px;
    }
  }
  .chart-container {
    width: 100%;
    height: 320px;
  }
</style>
