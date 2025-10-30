"use client"

import { useState } from "react"

export interface UseAudioRecordingReturn {
  isRecording: boolean
  audioLevel: number
  audioUrl: string | null
  startRecording: () => void
  stopRecording: () => void
  playRecording: () => void
}

export function useAudioRecording(): UseAudioRecordingReturn {
  const [isRecording, setIsRecording] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)

  const startRecording = () => {
    setIsRecording(true)
  }

  const stopRecording = () => {
    setIsRecording(false)
  }

  const playRecording = () => {
    // Stub implementation
  }

  return {
    isRecording,
    audioLevel,
    audioUrl,
    startRecording,
    stopRecording,
    playRecording,
  }
}
