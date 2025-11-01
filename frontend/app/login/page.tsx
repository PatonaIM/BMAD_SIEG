import { LoginForm } from "@/src/features/auth/components/LoginForm/LoginForm"
import { MockModeIndicator } from "@/src/components/shared/MockModeIndicator"
import { Card } from "@/components/ui/card"

export default function LoginPage() {
  return (
    <div className="container max-w-md mx-auto">
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="p-8 w-full shadow-lg">
          <MockModeIndicator />
          <LoginForm />
        </Card>
      </div>
    </div>
  )
}
