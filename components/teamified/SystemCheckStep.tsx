import type React from "react"

export type StepStatus = "pending" | "in-progress" | "success" | "error"

export interface SystemCheckStepProps {
  title: string
  status: StepStatus
  children?: React.ReactNode
}

export function SystemCheckStep({ title, status, children }: SystemCheckStepProps) {
  return (
    <div>
      <h3>{title}</h3>
      <div>{status}</div>
      {children}
    </div>
  )
}
