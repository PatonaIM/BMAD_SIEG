/**
 * useRealtimeInterview Hook
 * 
 * Manages WebSocket connection to OpenAI Realtime API for voice interviews.
 * Handles bidirectional audio streaming, connection lifecycle, and error recovery.
 */

import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuthStore } from '@/src/features/auth/store/authStore'

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error'

export interface RealtimeMessage {
  type: string
  [key: string]: any
}

export interface RealtimeOptions {
  onConnected?: () => void
  onDisconnected?: () => void
  onError?: (error: Error) => void
  onTranscript?: (transcript: { role: 'user' | 'assistant'; text: string; messageId: string }) => void
  onAudioChunk?: (audioData: string) => void
  reconnectAttempts?: number
  reconnectDelay?: number
}

export interface UseRealtimeInterviewReturn {
  connectionState: ConnectionState
  connect: () => Promise<void>
  disconnect: () => void
  sendAudioChunk: (audioData: ArrayBuffer) => void
  commitAudio: () => void
  latency: number | null
  error: Error | null
}

/**
 * Hook for managing OpenAI Realtime API WebSocket connection
 * 
 * @param interviewId - UUID of the interview
 * @param options - Configuration options and event handlers
 * @returns Connection state and control functions
 * 
 * @example
 * ```tsx
 * const { connectionState, connect, sendAudioChunk, disconnect } = useRealtimeInterview(
 *   interviewId,
 *   {
 *     onTranscript: (transcript) => console.log(transcript.text),
 *     onError: (error) => console.error(error)
 *   }
 * )
 * ```
 */
export function useRealtimeInterview(
  interviewId: string,
  options: RealtimeOptions = {}
): UseRealtimeInterviewReturn {
  const token = useAuthStore((state) => state.token)
  
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected')
  const [latency, setLatency] = useState<number | null>(null)
  const [error, setError] = useState<Error | null>(null)
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)
  const reconnectCountRef = useRef(0)
  const lastPingRef = useRef<number>(0)
  
  const {
    onConnected,
    onDisconnected,
    onError,
    onTranscript,
    onAudioChunk,
    reconnectAttempts = 5,
    reconnectDelay = 1000
  } = options

  /**
   * Handle incoming WebSocket messages
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: RealtimeMessage = JSON.parse(event.data)
      
      switch (message.type) {
        case 'connected':
          console.log('Realtime connection established:', message)
          setConnectionState('connected')
          reconnectCountRef.current = 0
          onConnected?.()
          break
          
        case 'ai_audio_chunk':
          // Forward audio chunk to playback handler
          if (message.audio && onAudioChunk) {
            onAudioChunk(message.audio)
          }
          break
          
        case 'transcript':
          // Handle complete transcript
          if (message.text && onTranscript) {
            onTranscript({
              role: message.role,
              text: message.text,
              messageId: message.message_id
            })
          }
          break
          
        case 'transcript_delta':
          // Handle partial transcript (optional - for real-time display)
          break
          
        case 'pong':
          // Calculate latency
          const latencyMs = Date.now() - lastPingRef.current
          setLatency(latencyMs)
          break
          
        case 'error':
          console.error('Realtime API error:', message)
          const apiError = new Error(message.message || 'Unknown error')
          setError(apiError)
          onError?.(apiError)
          
          if (message.error === 'RATE_LIMIT_EXCEEDED' || message.error === 'INTERVIEW_NOT_ACTIVE') {
            // Don't reconnect for these errors
            setConnectionState('error')
          }
          break
          
        default:
          console.debug('Unhandled message type:', message.type)
      }
    } catch (err) {
      console.error('Error parsing WebSocket message:', err)
    }
  }, [onConnected, onAudioChunk, onTranscript, onError])

  /**
   * Attempt to reconnect with exponential backoff
   */
  const attemptReconnect = useCallback(() => {
    if (reconnectCountRef.current >= reconnectAttempts) {
      console.error('Max reconnection attempts reached')
      setConnectionState('error')
      setError(new Error('Failed to reconnect after multiple attempts'))
      return
    }
    
    reconnectCountRef.current += 1
    const delay = reconnectDelay * Math.pow(2, reconnectCountRef.current - 1)
    
    console.log(`Reconnecting in ${delay}ms (attempt ${reconnectCountRef.current}/${reconnectAttempts})`)
    
    reconnectTimeoutRef.current = setTimeout(() => {
      connect()
    }, delay)
  }, [reconnectAttempts, reconnectDelay])

  /**
   * Connect to WebSocket server
   */
  const connect = useCallback(async () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.warn('WebSocket already connected')
      return
    }
    
    setConnectionState('connecting')
    setError(null)
    
    try {
      // Check if token exists
      if (!token) {
        throw new Error('Authentication token not found')
      }
      
      // Determine WebSocket URL based on environment
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = process.env.NEXT_PUBLIC_API_URL?.replace(/^https?:\/\//, '') || 'localhost:8000'
      
      // Add JWT token as query parameter for WebSocket authentication
      const wsUrl = `${protocol}//${host}/api/v1/interviews/${interviewId}/realtime/connect?token=${encodeURIComponent(token)}`
      
      console.log('Connecting to realtime WebSocket...')
      
      // Create WebSocket connection
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      
      ws.onopen = () => {
        console.log('WebSocket connection opened')
        // Note: Connection state set to 'connected' when we receive 'connected' message from server
      }
      
      ws.onmessage = handleMessage
      
      ws.onerror = (event) => {
        console.error('WebSocket error:', event)
        const wsError = new Error('WebSocket connection error')
        setError(wsError)
        setConnectionState('error')
        onError?.(wsError)
      }
      
      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        wsRef.current = null
        setConnectionState('disconnected')
        onDisconnected?.()
        
        // Attempt reconnect if not a clean close
        if (event.code !== 1000 && connectionState === 'connected') {
          attemptReconnect()
        }
      }
      
    } catch (err) {
      console.error('Failed to connect:', err)
      const connectError = err instanceof Error ? err : new Error('Connection failed')
      setError(connectError)
      setConnectionState('error')
      onError?.(connectError)
    }
  }, [interviewId, token, handleMessage, onError, onDisconnected, attemptReconnect, connectionState])

  /**
   * Disconnect from WebSocket server
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect')
      wsRef.current = null
    }
    
    setConnectionState('disconnected')
    reconnectCountRef.current = 0
  }, [])

  /**
   * Send audio chunk to server
   */
  const sendAudioChunk = useCallback((audioData: ArrayBuffer) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      // Convert ArrayBuffer to base64
      const uint8Array = new Uint8Array(audioData)
      let binary = ''
      for (let i = 0; i < uint8Array.length; i++) {
        binary += String.fromCharCode(uint8Array[i])
      }
      const base64Audio = btoa(binary)
      
      wsRef.current.send(JSON.stringify({
        type: 'audio_chunk',
        audio: base64Audio,
        timestamp: Date.now()
      }))
    } else {
      console.warn('Cannot send audio: WebSocket not connected')
    }
  }, [])

  /**
   * Commit audio buffer (signal end of audio input)
   */
  const commitAudio = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'audio_commit'
      }))
    }
  }, [])

  /**
   * Send periodic ping to measure latency
   */
  useEffect(() => {
    if (connectionState === 'connected') {
      const pingInterval = setInterval(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          lastPingRef.current = Date.now()
          wsRef.current.send(JSON.stringify({ type: 'ping' }))
        }
      }, 5000) // Ping every 5 seconds
      
      return () => clearInterval(pingInterval)
    }
  }, [connectionState])

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    connectionState,
    connect,
    disconnect,
    sendAudioChunk,
    commitAudio,
    latency,
    error
  }
}
