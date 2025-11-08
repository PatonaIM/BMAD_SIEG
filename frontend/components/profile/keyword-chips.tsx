"use client"

import { Badge } from "@/components/ui/badge"

interface KeywordChipsProps {
  keywords: string[]
}

export function KeywordChips({ keywords }: KeywordChipsProps) {
  if (!keywords || keywords.length === 0) {
    return (
      <div className="text-sm text-muted-foreground italic">
        No missing keywords identified
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-muted-foreground">
        Missing Keywords ({keywords.length})
      </h4>
      <div className="flex flex-wrap gap-2">
        {keywords.map((keyword, index) => (
          <Badge 
            key={index} 
            variant="outline"
            className="border-purple-200 bg-purple-50 text-purple-700"
          >
            {keyword}
          </Badge>
        ))}
      </div>
      <p className="text-xs text-muted-foreground mt-2">
        Consider adding these relevant keywords to improve your resume
      </p>
    </div>
  )
}
