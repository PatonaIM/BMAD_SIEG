"use client"

import { useTheme } from "./theme-provider"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Sun, Moon, Waves, Trees, Sparkles, Sunset, Flower } from "lucide-react"

const themes = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "ocean", label: "Ocean Blue", icon: Waves },
  { value: "forest", label: "Forest Green", icon: Trees },
  { value: "purple", label: "Royal Purple", icon: Sparkles },
  { value: "sunset", label: "Sunset Orange", icon: Sunset },
  { value: "rose", label: "Rose Pink", icon: Flower },
] as const

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme()
  const currentTheme = themes.find((t) => t.value === theme) || themes[0]
  const Icon = currentTheme.icon

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Icon className="h-5 w-5" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {themes.map(({ value, label, icon: ThemeIcon }) => (
          <DropdownMenuItem key={value} onClick={() => setTheme(value as any)} className="gap-2">
            <ThemeIcon className="h-4 w-4" />
            {label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
