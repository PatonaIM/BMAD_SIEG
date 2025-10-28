"use client"

import { useState, useCallback, useRef, useEffect } from "react"

interface UseAudioRecordingReturn {
  isRecording: boolean
  audioBlob: Blob | null
  audioUrl: string | null
  recordingTime: number
  audioLevel: number
  startRecording: (stream: MediaStream) => void
  stopRecording: () => void
  playRecording: () => void
  resetRecording: () => void
}

export function useAudioRecording(): UseAudioRecordingReturn {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [recordingTime, setRecordingTime] = useState(0)
  const [audioLevel, setAudioLevel] = useState(0)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const updateAudioLevel = useCallback(() => {
    if (!analyserRef.current) return

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
    analyserRef.current.getByteFrequencyData(dataArray)

    const average = dataArray.reduce((a, b) => a + b) / dataArray.length
    setAudioLevel(average / 255)

    animationFrameRef.current = requestAnimationFrame(updateAudioLevel)
  }, [])

  const startRecording = useCallback(
    (stream: MediaStream) => {
      chunksRef.current = []
      setAudioBlob(null)
      setAudioUrl(null)
      setRecordingTime(0)

      // Set up audio context for visualization
      audioContextRef.current = new AudioContext()
      analyserRef.current = audioContextRef.current.createAnalyser()
      analyserRef.current.fftSize = 256

      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)

      // Start recording
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" })
        setAudioBlob(blob)
        setAudioUrl(URL.createObjectURL(blob))
      }

      mediaRecorder.start()
      setIsRecording(true)

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1)
      }, 1000)

      // Start audio level monitoring
      updateAudioLevel()
    },
    [updateAudioLevel],
  )

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)

      if (timerRef.current) {
        clearInterval(timerRef.current)
      }

      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }

      if (audioContextRef.current) {
        audioContextRef.current.close()
      }

      setAudioLevel(0)
    }
  }, [isRecording])

  const playRecording = useCallback(() => {
    if (audioUrl) {
      const audio = new Audio(audioUrl)
      audio.play()
    }
  }, [audioUrl])

  const resetRecording = useCallback(() => {
    setAudioBlob(null)
    setAudioUrl(null)
    setRecordingTime(0)
    setAudioLevel(0)
    chunksRef.current = []
  }, [])

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [])

  return {
    isRecording,
    audioBlob,
    audioUrl,
    recordingTime,
    audioLevel,
    startRecording,
    stopRecording,
    playRecording,
    resetRecording,
  }
}
