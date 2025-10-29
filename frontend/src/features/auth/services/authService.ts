import { apiClient } from '../../../services/api/client';
import type { RegisterData, LoginData, AuthTokenResponse } from '../types/auth.types';

export const authService = {
  async registerCandidate(data: RegisterData): Promise<AuthTokenResponse> {
    return apiClient.post<AuthTokenResponse>('/auth/register', data);
  },

  async loginCandidate(data: LoginData): Promise<AuthTokenResponse> {
    return apiClient.post<AuthTokenResponse>('/auth/login', data);
  },
};
