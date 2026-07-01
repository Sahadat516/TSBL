"use client"

import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Loader2, Lock, Eye, EyeOff, Shield } from "lucide-react"
import Link from "next/link"

import { cn } from "@/lib/utils"
import { authService } from "@/services/auth.service"

const resetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Must contain at least one uppercase letter")
      .regex(/[a-z]/, "Must contain at least one lowercase letter")
      .regex(/[0-9]/, "Must contain at least one number"),
    confirm_password: z.string().min(1, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  })

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>

interface ResetPasswordFormProps {
  className?: string
}

export function ResetPasswordForm({ className }: ResetPasswordFormProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get("token")

  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [serverError, setServerError] = useState("")
  const [isSuccess, setIsSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  })

  if (!token) {
    return (
      <div className={cn("text-center space-y-4", className)}>
        <Shield className="mx-auto h-12 w-12 text-red-500" />
        <h2 className="text-lg font-semibold">Invalid or missing reset link</h2>
        <p className="text-sm text-gray-500">This password reset link is invalid or has expired.</p>
        <Link
          href="/forgot-password"
          className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline"
        >
          Request a new reset link
        </Link>
      </div>
    )
  }

  if (isSuccess) {
    return (
      <div className={cn("text-center space-y-4", className)}>
        <Shield className="mx-auto h-12 w-12 text-green-500" />
        <h2 className="text-lg font-semibold">Password reset successful</h2>
        <p className="text-sm text-gray-500">Your password has been updated. You can now sign in with your new password.</p>
        <Link
          href="/login"
          className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
        >
          Sign in
        </Link>
      </div>
    )
  }

  async function onSubmit(data: ResetPasswordFormData) {
    setServerError("")
    try {
      await authService.resetPassword({
        token,
        password: data.password,
        confirm_password: data.confirm_password,
      })
      setIsSuccess(true)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setServerError(error.response?.data?.detail || "Failed to reset password. The link may have expired.")
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={cn("space-y-5", className)}>
      <div className="text-center">
        <Shield className="mx-auto h-10 w-10 text-blue-600" />
        <h1 className="mt-4 text-2xl font-bold">Set new password</h1>
        <p className="mt-1 text-sm text-gray-500">Must be at least 8 characters with uppercase, lowercase & number</p>
      </div>

      {serverError && (
        <div className="rounded-lg bg-red-50 dark:bg-red-950/50 p-4 text-sm text-red-600 dark:text-red-400">
          {serverError}
        </div>
      )}

      <div className="space-y-2">
        <label htmlFor="password" className="text-sm font-medium">New Password</label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            id="password"
            type={showPassword ? "text" : "password"}
            {...register("password")}
            className="w-full rounded-lg border border-gray-300 bg-white py-2.5 pl-10 pr-12 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-gray-600 dark:bg-gray-800"
            placeholder="Min 8 characters"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            tabIndex={-1}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
      </div>

      <div className="space-y-2">
        <label htmlFor="confirm_password" className="text-sm font-medium">Confirm Password</label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            id="confirm_password"
            type={showConfirm ? "text" : "password"}
            {...register("confirm_password")}
            className="w-full rounded-lg border border-gray-300 bg-white py-2.5 pl-10 pr-12 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-gray-600 dark:bg-gray-800"
            placeholder="Repeat your password"
          />
          <button
            type="button"
            onClick={() => setShowConfirm(!showConfirm)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            tabIndex={-1}
          >
            {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        {errors.confirm_password && <p className="text-xs text-red-500">{errors.confirm_password.message}</p>}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
        {isSubmitting ? "Resetting..." : "Reset password"}
      </button>

      <p className="text-center text-sm text-gray-500">
        <Link href="/login" className="text-blue-600 hover:underline">
          Back to sign in
        </Link>
      </p>
    </form>
  )
}
