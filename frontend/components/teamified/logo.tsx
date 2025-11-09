"use client"

import Image from "next/image"
import { useTheme } from "next-themes"
import { useEffect, useState } from "react"

interface LogoProps {
  className?: string
  size?: number
}

export function TeamifiedLogo({ className, size = 32 }: LogoProps) {
  const { resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <div className={className} style={{ width: size, height: size }} />
  }

  const logoSrc = resolvedTheme === "dark" ? "/teamified-icon-dark.svg" : "/teamified-icon-light.svg"

  return (
    <Image
      src={logoSrc}
      alt="Teamified Logo"
      width={size}
      height={size}
      className={className}
      priority
    />
  )
}
