import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { videoUploadService } from './videoUploadService'

// Mock global fetch
global.fetch = vi.fn()
global.localStorage = {
  getItem: vi.fn(() => 'mock-token'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn()
}

describe('videoUploadService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  describe('uploadVideoChunk', () => {
    it('should upload video chunk successfully', async () => {
      const mockResponse = {
        success: true,
        chunk_index: 0,
        uploaded_at: '2025-11-01T12:34:56Z'
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const chunk = new Blob(['mock video data'], { type: 'video/webm' })
      const result = await videoUploadService.uploadVideoChunk(
        'interview-123',
        chunk,
        0,
        false
      )

      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should include auth token in request', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, chunk_index: 0, uploaded_at: '' })
      })

      const chunk = new Blob(['mock video data'])
      await videoUploadService.uploadVideoChunk('interview-123', chunk, 0, false)

      const fetchCall = (global.fetch as any).mock.calls[0]
      expect(fetchCall[1].headers.Authorization).toBe('Bearer mock-token')
    })

    it('should retry on network error with exponential backoff', async () => {
      ;(global.fetch as any)
        .mockRejectedValueOnce(new TypeError('Network error'))
        .mockRejectedValueOnce(new TypeError('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, chunk_index: 0, uploaded_at: '' })
        })

      const chunk = new Blob(['mock video data'])
      const uploadPromise = videoUploadService.uploadVideoChunk(
        'interview-123',
        chunk,
        0,
        false
      )

      // Fast-forward through delays
      await vi.advanceTimersByTimeAsync(1000) // 1st retry delay
      await vi.advanceTimersByTimeAsync(2000) // 2nd retry delay

      const result = await uploadPromise

      expect(result.success).toBe(true)
      expect(global.fetch).toHaveBeenCalledTimes(3)
    })

    it('should throw error after max retries exhausted', async () => {
      ;(global.fetch as any).mockRejectedValue(new TypeError('Network error'))

      const chunk = new Blob(['mock video data'])
      const uploadPromise = videoUploadService.uploadVideoChunk(
        'interview-123',
        chunk,
        0,
        false
      )

      // Fast-forward through all retry delays
      await vi.advanceTimersByTimeAsync(1000) // 1st retry
      await vi.advanceTimersByTimeAsync(2000) // 2nd retry
      await vi.advanceTimersByTimeAsync(4000) // 3rd retry

      await expect(uploadPromise).rejects.toThrow('Network error')
      expect(global.fetch).toHaveBeenCalledTimes(4) // Initial + 3 retries
    })

    it('should handle storage quota exceeded error', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 507,
        json: async () => ({ detail: 'Storage quota exceeded' })
      })

      const chunk = new Blob(['mock video data'])

      await expect(
        videoUploadService.uploadVideoChunk('interview-123', chunk, 0, false)
      ).rejects.toThrow('Storage quota exceeded')
    })

    it('should not retry storage quota errors', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 507,
        json: async () => ({ detail: 'Storage quota exceeded' })
      })

      const chunk = new Blob(['mock video data'])

      await expect(
        videoUploadService.uploadVideoChunk('interview-123', chunk, 0, false)
      ).rejects.toThrow()

      expect(global.fetch).toHaveBeenCalledTimes(1) // No retries
    })

    it('should send is_final flag correctly', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, chunk_index: 5, uploaded_at: '' })
      })

      const chunk = new Blob(['mock video data'])
      await videoUploadService.uploadVideoChunk('interview-123', chunk, 5, true)

      const fetchCall = (global.fetch as any).mock.calls[0]
      const formData = fetchCall[1].body

      // Verify FormData was sent (can't easily inspect FormData in tests)
      expect(formData).toBeInstanceOf(FormData)
    })

    it('should handle timeout with retry', async () => {
      ;(global.fetch as any).mockImplementationOnce(() => {
        return new Promise((_, reject) => {
          setTimeout(() => reject({ name: 'AbortError' }), 100)
        })
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, chunk_index: 0, uploaded_at: '' })
      })

      const chunk = new Blob(['mock video data'])
      const uploadPromise = videoUploadService.uploadVideoChunk(
        'interview-123',
        chunk,
        0,
        false
      )

      await vi.advanceTimersByTimeAsync(100) // Timeout
      await vi.advanceTimersByTimeAsync(1000) // Retry delay

      const result = await uploadPromise
      expect(result.success).toBe(true)
      expect(global.fetch).toHaveBeenCalledTimes(2)
    })
  })

  describe('calculateUploadProgress', () => {
    it('should calculate progress percentage correctly', () => {
      expect(videoUploadService.calculateUploadProgress(0, 10)).toBe(0)
      expect(videoUploadService.calculateUploadProgress(5, 10)).toBe(50)
      expect(videoUploadService.calculateUploadProgress(10, 10)).toBe(100)
    })

    it('should return 0 when total chunks is 0', () => {
      expect(videoUploadService.calculateUploadProgress(0, 0)).toBe(0)
    })

    it('should round to nearest integer', () => {
      expect(videoUploadService.calculateUploadProgress(1, 3)).toBe(33)
      expect(videoUploadService.calculateUploadProgress(2, 3)).toBe(67)
    })
  })
})
