import request from '@/utils/request'

export function uploadFileApi(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/v1/file/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
