/**
 * useCaptionSync Hook
 * 
 * Manages caption synchronization with AI speech
 * - Processes transcript events from Realtime API
 * - Handles caption timing (fade-in, persist, fade-out)
 * - Segments long captions for readability
 * - Maintains caption history
 */

import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { CaptionQueue, CaptionItem } from '../utils/captionQueue'
import { segmentCaptionText, sanitizeCaptionText } from '../utils/textSegmentation'

export type InterviewState = 'idle' | 'ai_listening' | 'candidate_speaking' | 'ai_speaking' | 'processing'

export interface TranscriptEvent {
  role: 'user' | 'assistant'
  text: string
  messageId: string
}

export interface UseCaptionSyncOptions {
  interviewState: InterviewState
  enabled?: boolean
}

export interface UseCaptionSyncReturn {
  currentCaption: string | null
  isVisible: boolean
  captionHistory: CaptionItem[]
  onTranscript: (transcript: TranscriptEvent) => void
}

const FADE_OUT_DELAY = 3000 // 3 seconds after AI stops speaking

/**
 * Hook for synchronizing captions with AI speech
 * 
 * @param options - Configuration options
 * @returns Caption state and transcript handler
 * 
 * @example
 * ```tsx
 * const { currentCaption, isVisible, onTranscript } = useCaptionSync({
 *   interviewState: 'ai_speaking',
 *   enabled: true
 * })
 * 
 * // In useRealtimeInterview hook options:
 * useRealtimeInterview(interviewId, {
 *   onTranscript
 * })
 * ```
 */
export function useCaptionSync(options: UseCaptionSyncOptions): UseCaptionSyncReturn {
  const { interviewState, enabled = true } = options

  // Caption queue instance (stable across renders)
  const queueRef = useRef(new CaptionQueue())
  
  // Current caption state
  const [currentCaption, setCurrentCaption] = useState<string | null>(null)
  const [isVisible, setIsVisible] = useState(false)
  const [captionHistory, setCaptionHistory] = useState<CaptionItem[]>([])
  
  // Fade-out timer
  const fadeOutTimerRef = useRef<NodeJS.Timeout | null>(null)
  
  // Current segment index for multi-segment captions
  const currentSegmentIndexRef = useRef(0)
  const currentSegmentsRef = useRef<string[]>([])

  /**
   * Handle transcript events from Realtime API
   */
  const onTranscript = useCallback((transcript: TranscriptEvent) => {
    if (!enabled) return

    // Filter out user transcripts - only show AI captions
    if (transcript.role === 'user') {
      return
    }

    // Sanitize and segment the caption text
    const sanitized = sanitizeCaptionText(transcript.text)
    const segments = segmentCaptionText(sanitized)

    // If we have segments, show the first one
    if (segments.length > 0) {
      // Clear any pending fade-out timer
      if (fadeOutTimerRef.current) {
        clearTimeout(fadeOutTimerRef.current)
        fadeOutTimerRef.current = null
      }

      // Store segments for potential cycling (future enhancement)
      currentSegmentsRef.current = segments
      currentSegmentIndexRef.current = 0

      // For now, just show the first segment (or combined if short)
      const captionText = segments.length === 1 ? segments[0] : segments[0]

      // Add to queue
      queueRef.current.enqueue(captionText, transcript.role)

      // Update display
      setCurrentCaption(captionText)
      setIsVisible(true)

      // Update history
      setCaptionHistory(queueRef.current.getHistory(3))

      // Mark performance
      if (typeof performance !== 'undefined') {
        performance.mark('caption-displayed')
      }
    }
  }, [enabled])

  /**
   * Handle fade-out timing based on AI speaking state
   */
  useEffect(() => {
    // Only manage fade-out if captions are enabled and visible
    if (!enabled || !isVisible) return

    // If AI is speaking, keep caption visible (cancel any pending fade-out)
    if (interviewState === 'ai_speaking') {
      if (fadeOutTimerRef.current) {
        clearTimeout(fadeOutTimerRef.current)
        fadeOutTimerRef.current = null
      }
      return
    }

    // If AI stopped speaking and we have a caption, start fade-out timer
    if (currentCaption && interviewState !== 'ai_speaking') {
      // Clear any existing timer
      if (fadeOutTimerRef.current) {
        clearTimeout(fadeOutTimerRef.current)
      }

      // Start new fade-out timer (3 seconds)
      fadeOutTimerRef.current = setTimeout(() => {
        setIsVisible(false)
        queueRef.current.setCurrentVisibility(false)
      }, FADE_OUT_DELAY)
    }

    // Cleanup on unmount
    return () => {
      if (fadeOutTimerRef.current) {
        clearTimeout(fadeOutTimerRef.current)
      }
    }
  }, [interviewState, currentCaption, isVisible, enabled])

  /**
   * Clear captions when disabled
   */
  useEffect(() => {
    if (!enabled) {
      setCurrentCaption(null)
      setIsVisible(false)
      queueRef.current.clear()
      setCaptionHistory([])
      if (fadeOutTimerRef.current) {
        clearTimeout(fadeOutTimerRef.current)
        fadeOutTimerRef.current = null
      }
    }
  }, [enabled])

  return {
    currentCaption,
    isVisible,
    captionHistory,
    onTranscript
  }
}
