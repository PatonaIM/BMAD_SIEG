import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useMediaPermissions } from './useMediaPermissions';

// Mock navigator.mediaDevices
const mockGetUserMedia = vi.fn();

beforeEach(() => {
  vi.clearAllMocks();
  
  Object.defineProperty(global.navigator, 'mediaDevices', {
    value: { getUserMedia: mockGetUserMedia },
    writable: true,
    configurable: true,
  });
});

describe('useMediaPermissions', () => {
  describe('Microphone', () => {
    it('should start with idle status', () => {
      const { result } = renderHook(() => useMediaPermissions());
      
      expect(result.current.microphoneStatus).toBe('idle');
      expect(result.current.microphoneStream).toBeNull();
      expect(result.current.microphoneError).toBeNull();
    });

    it('should request microphone permission successfully', async () => {
      const mockStream = {
        getTracks: () => [{ stop: vi.fn() }],
      } as unknown as MediaStream;
      
      mockGetUserMedia.mockResolvedValue(mockStream);
      
      const { result } = renderHook(() => useMediaPermissions());
      
      act(() => {
        result.current.requestMicrophone();
      });
      
      expect(result.current.microphoneStatus).toBe('requesting');
      
      await waitFor(() => {
        expect(result.current.microphoneStatus).toBe('granted');
        expect(result.current.microphoneStream).toBe(mockStream);
        expect(result.current.microphoneError).toBeNull();
      });
    });

    it('should handle permission denied error', async () => {
      const error = new DOMException('Permission denied', 'NotAllowedError');
      mockGetUserMedia.mockRejectedValue(error);
      
      const { result } = renderHook(() => useMediaPermissions());
      
      act(() => {
        result.current.requestMicrophone();
      });
      
      await waitFor(() => {
        expect(result.current.microphoneStatus).toBe('denied');
        expect(result.current.microphoneError).toContain('denied');
      });
    });

    it('should handle device not found error', async () => {
      const error = new DOMException('Device not found', 'NotFoundError');
      mockGetUserMedia.mockRejectedValue(error);
      
      const { result } = renderHook(() => useMediaPermissions());
      
      act(() => {
        result.current.requestMicrophone();
      });
      
      await waitFor(() => {
        expect(result.current.microphoneStatus).toBe('error');
        expect(result.current.microphoneError).toContain('No microphone found');
      });
    });

    it('should release microphone stream', async () => {
      const mockTrack = { stop: vi.fn() };
      const mockStream = {
        getTracks: () => [mockTrack],
      } as unknown as MediaStream;
      
      mockGetUserMedia.mockResolvedValue(mockStream);
      
      const { result } = renderHook(() => useMediaPermissions());
      
      await act(async () => {
        await result.current.requestMicrophone();
      });
      
      await waitFor(() => {
        expect(result.current.microphoneStatus).toBe('granted');
      });
      
      act(() => {
        result.current.releaseMicrophone();
      });
      
      expect(mockTrack.stop).toHaveBeenCalled();
      expect(result.current.microphoneStream).toBeNull();
      expect(result.current.microphoneStatus).toBe('idle');
    });
  });

  describe('Camera', () => {
    it('should request camera permission successfully', async () => {
      const mockVideoTrack = {
        getSettings: () => ({ width: 1280, height: 720, deviceId: 'camera-1' }),
        stop: vi.fn(),
      };
      const mockStream = {
        getTracks: () => [mockVideoTrack],
        getVideoTracks: () => [mockVideoTrack],
      } as unknown as MediaStream;
      
      mockGetUserMedia.mockResolvedValue(mockStream);
      
      const { result } = renderHook(() => useMediaPermissions());
      
      await act(async () => {
        await result.current.requestCamera();
      });
      
      await waitFor(() => {
        expect(result.current.cameraStatus).toBe('granted');
        expect(result.current.cameraStream).toBe(mockStream);
        expect(result.current.videoResolution).toEqual({ width: 1280, height: 720 });
      });
    });

    it('should reject resolution below 480p', async () => {
      const mockVideoTrack = {
        getSettings: () => ({ width: 320, height: 240 }),
      };
      const mockStream = {
        getTracks: () => [{ stop: vi.fn() }],
        getVideoTracks: () => [mockVideoTrack],
      } as unknown as MediaStream;
      
      mockGetUserMedia.mockResolvedValue(mockStream);
      
      const { result } = renderHook(() => useMediaPermissions());
      
      await act(async () => {
        await result.current.requestCamera();
      });
      
      await waitFor(() => {
        expect(result.current.cameraStatus).toBe('error');
        expect(result.current.cameraError).toContain('resolution too low');
      });
    });

    it('should handle camera permission denied', async () => {
      const error = new DOMException('Permission denied', 'NotAllowedError');
      mockGetUserMedia.mockRejectedValue(error);
      
      const { result } = renderHook(() => useMediaPermissions());
      
      await act(async () => {
        await result.current.requestCamera();
      });
      
      await waitFor(() => {
        expect(result.current.cameraStatus).toBe('denied');
        expect(result.current.cameraError).toContain('denied');
      });
    });
  });
});
