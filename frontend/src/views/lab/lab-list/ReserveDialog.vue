<template>
  <ElDialog
    v-model="visible"
    :title="`预约 - ${labName}`"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <ElForm ref="formRef" :model="form" :rules="rules" label-width="90px">
      <ElFormItem label="实验室" prop="lab_id">
        <ElInput :model-value="labName" disabled />
      </ElFormItem>
      <ElFormItem label="设备" prop="equipment_id">
        <ElSelect v-model="form.equipment_id" placeholder="不指定设备（预约实验室）" clearable>
          <ElOption
            v-for="eq in equipments"
            :key="eq.id"
            :label="`${eq.name}（${eq.spec || ''}）`"
            :value="eq.id"
          />
        </ElSelect>
      </ElFormItem>
      <ElFormItem label="日期" prop="date">
        <ElDatePicker
          v-model="form.date"
          type="date"
          placeholder="选择日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </ElFormItem>
      <ElFormItem label="开始时间" prop="start_time">
        <ElTimePicker
          v-model="form.start_time"
          placeholder="开始时间"
          style="width: 100%"
          value-format="HH:mm"
        />
      </ElFormItem>
      <ElFormItem label="结束时间" prop="end_time">
        <ElTimePicker
          v-model="form.end_time"
          placeholder="结束时间"
          style="width: 100%"
          value-format="HH:mm"
        />
      </ElFormItem>
      <ElFormItem label="备注" prop="remark">
        <ElInput v-model="form.remark" type="textarea" :rows="2" placeholder="选填" />
      </ElFormItem>
    </ElForm>
    <template #footer>
      <ElButton @click="visible = false">取消</ElButton>
      <ElButton type="primary" :loading="loading" @click="handleSubmit">提交预约</ElButton>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
  import { ref, reactive, watch } from 'vue'
  import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
  import { fetchCreateReservation } from '@/api/reservation'
  import { fetchEquipmentList, type EquipmentItem } from '@/api/equipment'

  const props = defineProps<{
    modelValue: boolean
    labId: number
    labName: string
    equipmentId?: number
  }>()

  const emit = defineEmits<{
    (e: 'update:modelValue', v: boolean): void
    (e: 'success'): void
  }>()

  const visible = computed({
    get: () => props.modelValue,
    set: (v) => emit('update:modelValue', v)
  })

  const formRef = ref<FormInstance>()
  const loading = ref(false)
  const equipments = ref<EquipmentItem[]>([])

  const form = reactive({
    lab_id: props.labId,
    equipment_id: undefined as number | undefined,
    date: '',
    start_time: '',
    end_time: '',
    remark: ''
  })

  const rules: FormRules = {
    date: [{ required: true, message: '请选择日期', trigger: 'change' }],
    start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
    end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
  }

  watch(
    () => props.modelValue,
    async (val) => {
      if (val) {
        form.lab_id = props.labId
        form.equipment_id = props.equipmentId ?? undefined
        form.date = ''
        form.start_time = ''
        form.end_time = ''
        form.remark = ''
        // 加载该实验室的设备
        try {
          const res = await fetchEquipmentList({ lab_id: props.labId, page_size: 100 })
          equipments.value = res.items
        } catch (e) {
          console.error(e)
        }
      }
    }
  )

  const handleSubmit = async () => {
    if (!formRef.value) return
    try {
      await formRef.value.validate()
      loading.value = true
      await fetchCreateReservation({
        lab_id: form.lab_id,
        equipment_id: form.equipment_id ?? null,
        date: form.date,
        start_time: form.start_time,
        end_time: form.end_time,
        remark: form.remark
      })
      ElMessage.success('预约提交成功，等待审核')
      emit('success')
      visible.value = false
    } catch (e) {
      // 表单验证或接口错误
    } finally {
      loading.value = false
    }
  }

  const handleClose = () => {
    formRef.value?.resetFields()
  }
</script>
