import { RegisterForm } from "@/src/features/auth/components/RegisterForm/RegisterForm"
import { Card } from "@/components/ui/card"

export default function RegisterPage() {
  return (
    <div className="container max-w-md mx-auto">
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="p-8 w-full shadow-lg">
          <RegisterForm />
        </Card>
      </div>
    </div>
  )
}
