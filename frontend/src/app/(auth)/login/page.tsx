import type { Metadata } from "next"
import { LoginForm } from "@/components/auth/login-form"

export const metadata: Metadata = {
  title: "Sign In | TSBL Marketplace",
  description: "Sign in to your TSBL Marketplace account",
}

export default function LoginPage() {
  return (
    <>
      <div className="text-center">
        <h1 className="text-3xl font-bold">Welcome back</h1>
        <p className="mt-2 text-sm text-gray-500">Sign in to your account to continue</p>
      </div>
      <LoginForm />
    </>
  )
}
