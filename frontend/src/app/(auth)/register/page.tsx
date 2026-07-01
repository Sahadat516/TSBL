import type { Metadata } from "next"
import { RegisterForm } from "@/components/auth/register-form"

export const metadata: Metadata = {
  title: "Create Account | TSBL Marketplace",
  description: "Create your TSBL Marketplace account",
}

export default function RegisterPage() {
  return (
    <>
      <div className="text-center">
        <h1 className="text-3xl font-bold">Create an account</h1>
        <p className="mt-2 text-sm text-gray-500">Join thousands of buyers and sellers on TSBL</p>
      </div>
      <RegisterForm />
    </>
  )
}
