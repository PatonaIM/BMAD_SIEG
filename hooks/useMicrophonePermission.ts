"use client"

import { useState } from "react"

export interface UseMicrophonePermissionReturn {
  status: "idle" | "requesting" | "granted" | "denied"
  error: string | null
  requestPermission: () => Promise<void>
  stream: MediaStream | null
}

export function useMicrophonePermission(): UseMicrophonePermissionReturn {
  const [status, setStatus] = useState<"idle" | "requesting" | "granted" | "denied">("idle")
  const [error, setError] = useState<string | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)

  const requestPermission = async () => {
    setStatus("requesting")
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      setStream(mediaStream)
      setStatus("granted")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Permission denied")
      setStatus("denied")
    }
  }

  return { status, error, requestPermission, stream }
}
