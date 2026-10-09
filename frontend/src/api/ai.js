import request from '@/utils/request'

export function chatApi(data) {
  return request({
    url: '/v1/ai/chat',
    method: 'post',
    data,
    timeout: 60000
  })
}
