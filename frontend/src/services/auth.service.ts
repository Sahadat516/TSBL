import api from "./api"
import type {
  AuthResponse,
  ForgotPasswordInput,
  LoginInput,
  RegisterInput,
  ResetPasswordInput,
  User,
} from "@/types/auth"

export const authService = {
  async register(data: RegisterInput): Promise<AuthResponse> {
    const response = await api.post("/api/v1/auth/register", data)
    return response.data
  },

  async login(data: LoginInput): Promise<AuthResponse> {
    const response = await api.post("/api/v1/auth/login", data)
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<{ access_token: string; refresh_token: string }> {
    const response = await api.post("/api/v1/auth/refresh", { refresh_token: refreshToken })
    return response.data
  },

  async logout(): Promise<void> {
    await api.post("/api/v1/auth/logout")
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get("/api/v1/auth/me")
    return response.data
  },

  async forgotPassword(data: ForgotPasswordInput): Promise<void> {
    await api.post("/api/v1/auth/forgot-password", data)
  },

  async resetPassword(data: ResetPasswordInput): Promise<void> {
    await api.post("/api/v1/auth/reset-password", data)
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post("/api/v1/auth/change-password", { current_password: currentPassword, new_password: newPassword })
  },
}
