<!-- 系统聊天窗口 -->
<template>
  <div>
    <ElDrawer v-model="isDrawerVisible" :size="isMobile ? '100%' : '480px'" :with-header="false">
      <div class="mb-5 flex-cb">
        <div>
          <span class="text-base font-medium">AI 智能助手</span>
          <div class="mt-1.5 flex-c gap-1">
            <div
              class="h-2 w-2 rounded-full"
              :class="isOnline ? 'bg-success/100' : 'bg-danger/100'"
            ></div>
            <span class="text-xs text-g-600">{{ isOnline ? '在线' : '离线' }}</span>
          </div>
        </div>
        <div>
          <ElIcon class="c-p" :size="20" @click="closeChat">
            <Close />
          </ElIcon>
        </div>
      </div>
      <div class="flex h-[calc(100%-70px)] flex-col">
        <!-- 聊天消息区域 -->
        <div
          class="flex-1 overflow-y-auto border-t-d px-4 py-7.5 [&::-webkit-scrollbar]:!w-1"
          ref="messageContainer"
        >
          <template v-for="(message, index) in messages" :key="index">
            <div
              :class="[
                'mb-7.5 flex w-full items-start gap-2',
                message.isMe ? 'flex-row-reverse' : 'flex-row'
              ]"
            >
              <ElAvatar :size="32" :src="message.avatar" class="shrink-0" />
              <div
                :class="['flex max-w-[70%] flex-col', message.isMe ? 'items-end' : 'items-start']"
              >
                <div
                  :class="[
                    'mb-1 flex gap-2 text-xs',
                    message.isMe ? 'flex-row-reverse' : 'flex-row'
                  ]"
                >
                  <span class="font-medium">{{ message.sender }}</span>
                  <span class="text-g-600">{{ message.time }}</span>
                </div>
                <div
                  :class="[
                    'rounded-md px-3.5 py-2.5 text-sm leading-[1.4] text-g-900',
                    message.isMe ? 'message-right bg-theme/15' : 'message-left bg-g-300/50'
                  ]"
                >
                  {{ message.content || (message.isMe ? '' : '思考中...') }}
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- 聊天输入区域 -->
        <div class="px-4 pt-4">
          <ElInput
            v-model="messageText"
            type="textarea"
            :rows="3"
            placeholder="输入您的问题..."
            resize="none"
            :disabled="sending"
            @keyup.enter.prevent="sendMessage"
          >
            <template #append>
              <div class="flex gap-2 py-2">
                <ElButton :icon="Paperclip" circle plain :disabled="sending" />
                <ElButton :icon="Picture" circle plain :disabled="sending" />
                <ElButton type="primary" :loading="sending" @click="sendMessage" v-ripple>
                  发送
                </ElButton>
              </div>
            </template>
          </ElInput>
          <div class="mt-3 flex-cb">
            <div class="flex-c">
              <ArtSvgIcon icon="ri:image-line" class="mr-5 c-p text-g-600 text-lg" />
              <ArtSvgIcon icon="ri:emotion-happy-line" class="mr-5 c-p text-g-600 text-lg" />
            </div>
            <ElButton
              type="primary"
              :loading="sending"
              @click="sendMessage"
              v-ripple
              class="min-w-20"
            >
              发送
            </ElButton>
          </div>
        </div>
      </div>
    </ElDrawer>
  </div>
</template>

<script setup lang="ts">
  import { Picture, Paperclip, Close } from '@element-plus/icons-vue'
  import { mittBus } from '@/utils/sys'
  import { fetchChatStream, type ChatMessage as ApiChatMessage } from '@/api/ai'
  import { useUserStore } from '@/store/modules/user'
  import defaultMeAvatar from '@/assets/images/avatar/avatar5.webp'
  import aiAvatar from '@/assets/images/avatar/avatar10.webp'

  defineOptions({ name: 'ArtChatWindow' })

  // 类型定义
  interface ChatMessage {
    id: number
    sender: string
    content: string
    time: string
    isMe: boolean
    avatar: string
  }

  // 常量定义
  const MOBILE_BREAKPOINT = 640
  const SCROLL_DELAY = 100
  const BOT_NAME = 'AI 助手'

  const userStore = useUserStore()
  const userName = computed(() => userStore.info?.userName || '我')

  // 用户头像：优先使用上传的头像，否则使用默认头像
  const meAvatar = computed(() => {
    const avatar = userStore.info?.avatar
    if (!avatar) return defaultMeAvatar
    return avatar.startsWith('http') ? avatar : `/uploads/${avatar}`
  })

  // 响应式布局
  const { width } = useWindowSize()
  const isMobile = computed(() => width.value < MOBILE_BREAKPOINT)

  // 组件状态
  const isDrawerVisible = ref(false)
  const isOnline = ref(true)
  const sending = ref(false)

  // 消息相关状态
  const messageText = ref('')
  const messageId = ref(1)
  const messageContainer = ref<HTMLElement | null>(null)

  // 初始化聊天消息：仅一条 AI 问候语
  const messages = ref<ChatMessage[]>([
    {
      id: messageId.value++,
      sender: BOT_NAME,
      content:
        '您好！我是实验室 AI 助手，可以为您解答实验室预约、设备使用等问题，请问有什么可以帮您？',
      time: formatCurrentTime(),
      isMe: false,
      avatar: aiAvatar
    }
  ])

  // 工具函数
  function formatCurrentTime(): string {
    return new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const scrollToBottom = (): void => {
    nextTick(() => {
      setTimeout(() => {
        if (messageContainer.value) {
          messageContainer.value.scrollTop = messageContainer.value.scrollHeight
        }
      }, SCROLL_DELAY)
    })
  }

  // 将 UI 消息转换为 API 所需格式（取最近对话，避免上下文过长）
  const buildApiMessages = (): ApiChatMessage[] => {
    return messages.value.map((m) => ({
      role: m.isMe ? 'user' : 'assistant',
      content: m.content
    }))
  }

  // 消息处理方法：调用后端 AI 流式接口
  const sendMessage = async (): Promise<void> => {
    const text = messageText.value.trim()
    if (!text || sending.value) return

    // 追加用户消息
    messages.value.push({
      id: messageId.value++,
      sender: userName.value,
      content: text,
      time: formatCurrentTime(),
      isMe: true,
      avatar: meAvatar.value
    })
    messageText.value = ''
    scrollToBottom()

    // 占位 AI 消息，用于流式累积
    const assistantMsg: ChatMessage = {
      id: messageId.value++,
      sender: BOT_NAME,
      content: '',
      time: formatCurrentTime(),
      isMe: false,
      avatar: aiAvatar
    }
    messages.value.push(assistantMsg)
    scrollToBottom()

    sending.value = true
    try {
      await fetchChatStream(
        { messages: buildApiMessages() },
        (chunk) => {
          assistantMsg.content += chunk
          scrollToBottom()
        },
        userStore.accessToken
      )
      if (!assistantMsg.content) {
        assistantMsg.content = '（暂无响应）'
      }
    } catch (e: any) {
      assistantMsg.content = `请求失败：${e?.message || '未知错误'}`
    } finally {
      sending.value = false
      scrollToBottom()
    }
  }

  // 聊天窗口控制方法
  const openChat = (): void => {
    isDrawerVisible.value = true
    scrollToBottom()
  }

  const closeChat = (): void => {
    isDrawerVisible.value = false
  }

  // 生命周期
  onMounted(() => {
    scrollToBottom()
    mittBus.on('openChat', openChat)
  })

  onUnmounted(() => {
    mittBus.off('openChat', openChat)
  })
</script>
