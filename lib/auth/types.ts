export interface RegisterData {
  email: string
  password: string
  full_name: string
}

export interface LoginData {
  email: string
  password: string
}

export interface AuthTokenResponse {
  token: string
  candidate_id: string
  email: string
}

export interface CandidateResponse {
  id: string
  email: string
  full_name: string
  phone?: string
  status: string
  created_at: string
  updated_at: string
}

export interface User {
  id: string
  email: string
  full_name: string
}
