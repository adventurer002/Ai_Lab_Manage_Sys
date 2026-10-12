import request from '@/utils/http'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
}

// 非流式对话
export function fetchChat(data: ChatRequest) {
  return request.post<ChatMessage>({
    url: '/api/ai/chat',
    data
  })
}

// 流式对话（SSE），直接用 fetch + ReadableStream
export async function fetchChatStream(
  data: ChatRequest,
  onMessage: (content: string) => void,
  token: string
): Promise<void> {
  const response = await fetch('/api/ai/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })

  if (!response.ok) {
    throw new Error(`请求失败: ${response.status}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('无法读取响应流')
  }

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    // 按 SSE 帧拆分（以 \n\n 分隔）
    const frames = buffer.split('\n\n')
    buffer = frames.pop() || ''

    for (const frame of frames) {
      const line = frame.trim()
      if (!line || !line.startsWith('data:')) continue

      const payload = line.slice(5).trim()
      if (!payload) continue

      try {
        const event = JSON.parse(payload)
        // 兼容多种事件字段：content / delta / text
        const chunk = event.content ?? event.delta ?? event.text ?? ''
        if (chunk) onMessage(chunk)
      } catch {
        // 无法解析的帧直接作为文本
        if (payload) onMessage(payload)
      }
    }
  }
}
