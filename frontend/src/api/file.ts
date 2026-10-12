import request from '@/utils/http'

export interface UploadResult {
  original_name: string
  disk_name: string
  size: number
  url: string
}

// 上传文件
export function fetchUploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<UploadResult>({
    url: '/api/file/upload',
    data: formData
  })
}
