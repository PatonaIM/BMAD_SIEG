"use client"

import { useMutation } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { authService } from "../services/authService"
import { useAuthStore } from "../store/authStore"
import type { RegisterData, LoginData } from "../types/auth.types"

export const useRegister = () => {
  const router = useRouter()
  const setAuth = useAuthStore((state) => state.setAuth)

  return useMutation({
    mutationFn: (data: RegisterData) => authService.registerCandidate(data),
    onSuccess: (response) => {
      const user = {
        id: response.candidate_id,
        email: response.email,
        full_name: "",
      }
      setAuth(user, response.token)
      router.push("/dashboard")
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
        full_name: "",
      }
      setAuth(user, response.token)
      router.push("/dashboard")
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
