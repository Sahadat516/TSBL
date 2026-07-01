export interface User {
  id: string
  email: string
  username: string
  role: "guest" | "buyer" | "seller" | "moderator" | "admin" | "super_admin"
  status: "pending" | "active" | "suspended" | "banned"
  is_verified: boolean
  profile_photo_url: string | null
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface AuthResponse {
  user: User
  tokens: AuthTokens
}

export interface RegisterInput {
  email: string
  username: string
  password: string
  confirm_password: string
}

export interface LoginInput {
  email: string
  password: string
}

export interface ForgotPasswordInput {
  email: string
}

export interface ResetPasswordInput {
  token: string
  password: string
  confirm_password: string
}
