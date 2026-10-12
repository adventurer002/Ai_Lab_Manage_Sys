<template>
  <div class="lab-list-page p-4">
    <!-- 搜索栏 -->
    <ElCard class="mb-4">
      <ElForm :inline="true" :model="search">
        <ElFormItem label="关键字">
          <ElInput
            v-model="search.keyword"
            placeholder="名称/位置"
            clearable
            @keyup.enter="loadData"
          />
        </ElFormItem>
        <ElFormItem label="状态">
          <ElSelect v-model="search.status" placeholder="全部" clearable style="width: 120px">
            <ElOption label="开放" :value="1" />
            <ElOption label="关闭" :value="0" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem>
          <ElButton type="primary" @click="loadData">查询</ElButton>
          <ElButton @click="resetSearch">重置</ElButton>
        </ElFormItem>
      </ElForm>
    </ElCard>

    <!-- 实验室卡片 -->
    <ElRow :gutter="16" v-loading="loading">
      <ElCol :span="8" v-for="lab in list" :key="lab.id" class="mb-4">
        <ElCard shadow="hover" class="lab-card">
          <div class="lab-img">
            <img :src="getLabImgUrl(lab.img)" :alt="lab.name" />
            <ElTag class="status-tag" :type="lab.status === 1 ? 'success' : 'danger'" effect="dark">
              {{ lab.status === 1 ? '开放' : '关闭' }}
            </ElTag>
          </div>
          <h3 class="lab-name">{{ lab.name }}</h3>
          <p class="lab-meta">
            <ElIcon><MapPinLine /></ElIcon> {{ lab.location || '未设置' }}
          </p>
          <p class="lab-meta">
            <ElIcon><TeamLine /></ElIcon> 容纳 {{ lab.capacity }} 人
          </p>
          <p class="lab-meta" v-if="lab.open_time">
            <ElIcon><TimeLine /></ElIcon> {{ lab.open_time }} - {{ lab.close_time }}
          </p>
          <p class="lab-desc">{{ lab.description || '暂无描述' }}</p>
          <div class="lab-actions mt-3">
            <ElButton
              type="primary"
              size="small"
              :disabled="lab.status !== 1"
              @click="openReserve(lab)"
            >
              预约
            </ElButton>
            <ElButton size="small" @click="goEquipment(lab.id)">查看设备</ElButton>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <ElEmpty v-if="!loading && !list.length" description="暂无实验室" />

    <!-- 分页 -->
    <div class="flex justify-end mt-4">
      <ElPagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[6, 12, 24]"
        layout="total, sizes, prev, pager, next"
        @current-change="loadData"
        @size-change="loadData"
      />
    </div>

    <!-- 预约弹窗 -->
    <ReserveDialog
      v-model="reserveVisible"
      :lab-id="currentLab?.id || 0"
      :lab-name="currentLab?.name || ''"
      @success="loadData"
    />
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { fetchLabList, type LabItem } from '@/api/lab'
  import ReserveDialog from './ReserveDialog.vue'
  import defaultLabImg from '@/assets/images/lab/lab.png'

  defineOptions({ name: 'LabList' })

  const router = useRouter()

  const list = ref<LabItem[]>([])
  const total = ref(0)
  const loading = ref(false)
  const page = ref(1)
  const pageSize = ref(12)

  const search = reactive({
    keyword: '',
    status: undefined as number | undefined
  })

  const reserveVisible = ref(false)
  const currentLab = ref<LabItem | null>(null)

  // 获取实验室图片 URL，无图时使用默认图片
  const getLabImgUrl = (img?: string | null): string => {
    if (!img) return defaultLabImg
    return img.startsWith('http') ? img : `/uploads/${img}`
  }

  const loadData = async () => {
    loading.value = true
    try {
      const res = await fetchLabList({
        page: page.value,
        page_size: pageSize.value,
        keyword: search.keyword || undefined,
        status: search.status
      })
      list.value = res.items
      total.value = res.total
    } catch (e) {
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  const resetSearch = () => {
    search.keyword = ''
    search.status = undefined
    page.value = 1
    loadData()
  }

  const openReserve = (lab: LabItem) => {
    currentLab.value = lab
    reserveVisible.value = true
  }

  const goEquipment = (labId: number) => {
    router.push(`/lab/equipment/${labId}`)
  }

  onMounted(loadData)
</script>

<style scoped lang="scss">
  .lab-card {
    height: 100%;
  }
  .lab-img {
    position: relative;
    width: 100%;
    height: 160px;
    background: #f5f7fa;
    overflow: hidden;
    border-radius: 4px;
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .placeholder {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #c0c4cc;
    }
    .status-tag {
      position: absolute;
      top: 8px;
      right: 8px;
    }
  }
  .lab-name {
    font-size: 16px;
    font-weight: 600;
    margin: 8px 0 6px;
  }
  .lab-meta {
    font-size: 13px;
    color: #909399;
    margin: 2px 0;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .lab-desc {
    font-size: 13px;
    color: #606266;
    margin-top: 6px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
