<template>
  <div>
    <el-card>
      <template #header>
        <div style="font-size: 16px; font-weight: bold">AI智能助手</div>
      </template>

      <div
        ref="listRef"
        style="
          height: 480px;
          overflow-y: auto;
          padding: 8px 4px;
          background-color: #fafafa;
          border-radius: 6px;
        "
      >
        <div
          v-for="(item, index) in messages"
          :key="index"
          :style="{
            display: 'flex',
            justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: '12px'
          }"
        >
          <div
            :style="{
              maxWidth: '70%',
              padding: '10px 12px',
              borderRadius: '8px',
              backgroundColor: item.role === 'user' ? '#409eff' : '#fff',
              color: item.role === 'user' ? '#fff' : '#333',
              lineHeight: '1.6',
              boxShadow: '0 1px 2px rgba(0, 0, 0, 0.06)'
            }"
            v-html="parseMarkdown(item.content)"
          ></div>
        </div>
      </div>

      <div v-if="statusText" style="font-size: 13px; color: #909399; margin-top: 8px">
        {{ statusText }}
      </div>

      <div style="margin-top: 12px; display: flex; gap: 8px; align-items: flex-end">
        <el-input
          v-model="input"
          type="textarea"
          :rows="2"
          placeholder="问问实验室怎么预约、开放时间..."
          @keydown.enter.exact.prevent="handleSend"
          @keydown.enter.shift.stop
        ></el-input>
        <el-button type="primary" @click="handleSend" :loading="loading">发送</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { chatStreamApi } from '@/api/ai'
import { ref, nextTick } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify' // 过滤危险的 HTML，防止 XSS 攻击

const messages = ref([
  {
    role: 'assistant',
    content:
      '您好，我是实验室助手。你可以向我提问怎么预约、取消。具体实验室信息请到【实验室列表】页查看'
  }
])
const input = ref('')
const loading = ref(false)
const listRef = ref()
const statusText = ref('') // 工具调用等过程状态文案

const scrollToBottom = () => {
  nextTick(() => {
    const elem = listRef.value
    if (elem) elem.scrollTop = elem.scrollHeight
  })
}

const handleSend = async () => {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  statusText.value = ''
  // 占位的 AI 消息，流式 token 不断追加到它的 content
  messages.value.push({ role: 'assistant', content: '' })
  const aiIndex = messages.value.length - 1
  scrollToBottom()
  try {
    const history = messages.value
      .filter((item) => item.role === 'user' || item.role === 'assistant')
      .map((item) => ({ role: item.role, content: item.content }))
    await chatStreamApi({ messages: history }, (evt) => {
      switch (evt.type) {
        case 'status':
        case 'tool_start':
        case 'tool_end':
          statusText.value = evt.label || evt.message || ''
          break
        case 'token':
          messages.value[aiIndex].content += evt.content
          scrollToBottom()
          break
        case 'error':
          messages.value[aiIndex].content = `❌ ${evt.message}`
          break
        case 'done':
          statusText.value = ''
          break
      }
    })
  } catch (err) {
    messages.value[aiIndex].content = `❌ ${err.message || '请求失败'}`
  } finally {
    loading.value = false
    statusText.value = ''
  }
}

// 将 markdown 字符串转换为安全的 HTML 字符串
const parseMarkdown = (text) => {
  if (!text) return ''
  marked.setOptions({ breaks: true }) // 把 \n 转换成 <br>
  // 使用 marked 解析，然后用 DOMPurify 清理
  const rawHtml = marked.parse(text)
  return DOMPurify.sanitize(rawHtml)
}
</script>
