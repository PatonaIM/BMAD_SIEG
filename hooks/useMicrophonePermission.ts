"use client"

import { useState, useEffect } from "react"

export function useMicrophonePermission() {
  const [permission, setPermission] = useState<"granted" | "denied" | "prompt">("prompt")
  const [isChecking, setIsChecking] = useState(false)

  const checkPermission = async () => {
    setIsChecking(true)
    try {
      const result = await navigator.permissions.query({ name: "microphone" as PermissionName })
      setPermission(result.state as "granted" | "denied" | "prompt")

      result.addEventListener("change", () => {
        setPermission(result.state as "granted" | "denied" | "prompt")
      })
    } catch (error) {
      console.error("Error checking microphone permission:", error)
    } finally {
      setIsChecking(false)
    }
  }

  const requestPermission = async () => {
    setIsChecking(true)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach((track) => track.stop())
      setPermission("granted")
      return true
    } catch (error) {
      console.error("Error requesting microphone permission:", error)
      setPermission("denied")
      return false
    } finally {
      setIsChecking(false)
    }
  }

  useEffect(() => {
    checkPermission()
  }, [])

  return {
    permission,
    isChecking,
    requestPermission,
  }
}
