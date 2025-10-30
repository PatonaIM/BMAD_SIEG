import { apiClient } from "@/lib/api/client"
import type { RegisterData, LoginData, AuthTokenResponse } from "./types"

export const authService = {
  async registerCandidate(data: RegisterData): Promise<AuthTokenResponse> {
    return apiClient.post<AuthTokenResponse>("/candidates/register", data)
  },

  async loginCandidate(data: LoginData): Promise<AuthTokenResponse> {
    return apiClient.post<AuthTokenResponse>("/auth/login", data)
  },
}
