<template>
  <div class="ai-chat-page flex flex-col h-full">
    <div class="chat-header px-4 py-3 border-b">
      <h3 class="text-lg font-semibold">AI 智能助手</h3>
      <p class="text-xs text-g-500 mt-1">基于实验室知识库，为您解答实验室预约、设备使用等问题</p>
    </div>

    <div ref="scrollRef" class="chat-messages flex-1 overflow-y-auto p-4">
      <div v-if="!messages.length" class="empty-tip text-center text-g-400 mt-20">
        <ElIcon :size="48"><Robot2Line /></ElIcon>
        <p class="mt-2">您好，我是实验室 AI 助手，有什么可以帮您？</p>
      </div>

      <div v-for="(msg, idx) in messages" :key="idx" class="message-row mb-4" :class="msg.role">
        <div class="avatar">
          <ElIcon v-if="msg.role === 'user'" :size="20"><UserLine /></ElIcon>
          <ElIcon v-else :size="20"><Robot2Line /></ElIcon>
        </div>
        <div class="bubble">{{ msg.content }}</div>
      </div>
    </div>

    <div class="chat-input p-4 border-t">
      <ElInput
        v-model="input"
        type="textarea"
        :rows="2"
        placeholder="输入您的问题..."
        @keydown.enter.exact.prevent="send"
      />
      <div class="flex justify-end mt-2">
        <ElButton type="primary" :loading="sending" @click="send">发送</ElButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, nextTick, onMounted } from 'vue'
  import { fetchChatStream, type ChatMessage } from '@/api/ai'
  import { useUserStore } from '@/store/modules/user'

  defineOptions({ name: 'AIChat' })

  const userStore = useUserStore()
  const scrollRef = ref<HTMLElement>()
  const input = ref('')
  const sending = ref(false)
  const messages = ref<ChatMessage[]>([])

  const scrollToBottom = () => {
    nextTick(() => {
      if (scrollRef.value) {
        scrollRef.value.scrollTop = scrollRef.value.scrollHeight
      }
    })
  }

  const send = async () => {
    const text = input.value.trim()
    if (!text || sending.value) return

    messages.value.push({ role: 'user', content: text })
    input.value = ''
    sending.value = true

    // 添加助手占位消息
    const assistantMsg: ChatMessage = { role: 'assistant', content: '' }
    messages.value.push(assistantMsg)
    scrollToBottom()

    try {
      await fetchChatStream(
        { messages: messages.value },
        (chunk) => {
          assistantMsg.content += chunk
          scrollToBottom()
        },
        userStore.accessToken
      )
      if (!assistantMsg.content) {
        assistantMsg.content = '（无响应）'
      }
    } catch (e: any) {
      assistantMsg.content = `请求失败：${e?.message || '未知错误'}`
    } finally {
      sending.value = false
      scrollToBottom()
    }
  }

  onMounted(() => {
    scrollToBottom()
  })
</script>

<style scoped lang="scss">
  .ai-chat-page {
    height: 100%;
    min-height: 0;
  }
  .chat-messages {
    background: #fafafa;
  }
  .message-row {
    display: flex;
    gap: 10px;
    &.user {
      flex-direction: row-reverse;
    }
    .avatar {
      flex-shrink: 0;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #409eff;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    &.assistant .avatar {
      background: #67c23a;
    }
    .bubble {
      max-width: 70%;
      padding: 10px 14px;
      border-radius: 8px;
      background: #fff;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-word;
    }
    &.user .bubble {
      background: #409eff;
      color: #fff;
    }
  }
</style>
