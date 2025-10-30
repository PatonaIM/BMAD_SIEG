"use client"

export interface InputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
}

export function Input({ value, onChange, placeholder, disabled }: InputProps) {
  return (
    <input value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} disabled={disabled} />
  )
}
