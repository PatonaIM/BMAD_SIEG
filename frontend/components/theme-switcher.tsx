"use client"

import { useTheme } from "./theme-provider"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Sun, Moon, Waves, Trees, Sparkles, Sunset, Flower2 } from "lucide-react"

const themes = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "ocean", label: "Ocean Blue", icon: Waves },
  { value: "forest", label: "Forest Green", icon: Trees },
  { value: "purple", label: "Royal Purple", icon: Sparkles },
  { value: "sunset", label: "Sunset Orange", icon: Sunset },
  { value: "rose", label: "Rose Pink", icon: Flower2 },
] as const

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme()
  const currentTheme = themes.find((t) => t.value === theme) || themes[0]
  const Icon = currentTheme.icon

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" className="relative bg-transparent">
          <Icon className="h-5 w-5" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {themes.map(({ value, label, icon: ThemeIcon }) => (
          <DropdownMenuItem
            key={value}
            onClick={() => setTheme(value)}
            className="flex items-center gap-2 cursor-pointer"
          >
            <ThemeIcon className="h-4 w-4" />
            <span>{label}</span>
            {theme === value && <span className="ml-auto">✓</span>}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
