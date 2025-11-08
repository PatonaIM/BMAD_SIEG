"use client"

import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface AnalysisSectionProps {
  title: string
  items: string[]
  icon: LucideIcon
  variant: 'success' | 'warning' | 'info'
}

export function AnalysisSection({ title, items, icon: Icon, variant }: AnalysisSectionProps) {
  const variantStyles = {
    success: {
      container: 'border-green-200 bg-green-50/50',
      icon: 'text-green-600 bg-green-100',
      title: 'text-green-900',
      item: 'text-green-800'
    },
    warning: {
      container: 'border-yellow-200 bg-yellow-50/50',
      icon: 'text-yellow-600 bg-yellow-100',
      title: 'text-yellow-900',
      item: 'text-yellow-800'
    },
    info: {
      container: 'border-blue-200 bg-blue-50/50',
      icon: 'text-blue-600 bg-blue-100',
      title: 'text-blue-900',
      item: 'text-blue-800'
    }
  }

  const styles = variantStyles[variant]

  if (!items || items.length === 0) {
    return null
  }

  return (
    <div className={cn("border rounded-lg p-4", styles.container)}>
      <div className="flex items-center gap-3 mb-3">
        <div className={cn("rounded-lg p-2", styles.icon)}>
          <Icon className="h-4 w-4" />
        </div>
        <h3 className={cn("font-semibold", styles.title)}>{title}</h3>
      </div>

      <ul className="space-y-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-start gap-2">
            <span className={cn("mt-1.5 h-1.5 w-1.5 rounded-full shrink-0", 
              variant === 'success' ? 'bg-green-600' :
              variant === 'warning' ? 'bg-yellow-600' :
              'bg-blue-600'
            )} />
            <span className={cn("text-sm", styles.item)}>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
