"use client"

import { useState, useCallback } from "react"

export type PermissionStatus = "idle" | "requesting" | "granted" | "denied"

interface UseMicrophonePermissionReturn {
  status: PermissionStatus
  error: string | null
  requestPermission: () => Promise<MediaStream | null>
  stream: MediaStream | null
}

export function useMicrophonePermission(): UseMicrophonePermissionReturn {
  const [status, setStatus] = useState<PermissionStatus>("idle")
  const [error, setError] = useState<string | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)

  const requestPermission = useCallback(async () => {
    setStatus("requesting")
    setError(null)

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })

      setStream(mediaStream)
      setStatus("granted")
      return mediaStream
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Microphone access denied"
      setError(errorMessage)
      setStatus("denied")
      return null
    }
  }, [])

  return { status, error, requestPermission, stream }
}
