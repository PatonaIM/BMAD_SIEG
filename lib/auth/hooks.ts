"use client"

import { useMutation } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { authService } from "./service"
import { useAuthStore } from "./store"
import type { RegisterData, LoginData } from "./types"

export const useRegister = () => {
  const router = useRouter()
  const setAuth = useAuthStore((state) => state.setAuth)

  return useMutation({
    mutationFn: (data: RegisterData) => authService.registerCandidate(data),
    onSuccess: (response) => {
      const user = {
        id: response.candidate_id,
        email: response.email,
        full_name: "", // Will be populated from candidate profile if needed
      }
      setAuth(user, response.token)
      router.push("/interview/start")
    },
  })
}

export const useLogin = () => {
  const router = useRouter()
  const setAuth = useAuthStore((state) => state.setAuth)

  return useMutation({
    mutationFn: (data: LoginData) => authService.loginCandidate(data),
    onSuccess: (response) => {
      const user = {
        id: response.candidate_id,
        email: response.email,
        full_name: "", // Will be populated from candidate profile if needed
      }
      setAuth(user, response.token)
      router.push("/interview/start")
    },
  })
}

export const useLogout = () => {
  const router = useRouter()
  const clearAuth = useAuthStore((state) => state.clearAuth)

  return () => {
    clearAuth()
    router.push("/login")
  }
}
