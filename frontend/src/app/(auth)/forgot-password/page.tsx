import type { Metadata } from "next"
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form"

export const metadata: Metadata = {
  title: "Forgot Password | TSBL Marketplace",
  description: "Reset your TSBL Marketplace password",
}

export default function ForgotPasswordPage() {
  return (
    <>
      <div className="text-center">
        <h1 className="text-3xl font-bold">Forgot password?</h1>
        <p className="mt-2 text-sm text-gray-500">
          Enter your email and we&apos;ll send you a reset link
        </p>
      </div>
      <ForgotPasswordForm />
    </>
  )
}
