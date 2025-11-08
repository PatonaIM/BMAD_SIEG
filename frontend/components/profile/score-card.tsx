"use client"

import { cn } from "@/lib/utils"

interface ScoreCardProps {
  score: number
  className?: string
}

export function ScoreCard({ score, className }: ScoreCardProps) {
  // Determine color based on score thresholds
  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 50) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 70) return 'Excellent'
    if (score >= 50) return 'Good'
    return 'Needs Improvement'
  }

  return (
    <div className={cn("flex items-center justify-between p-6 border-2 rounded-lg", getScoreColor(score), className)}>
      <div>
        <p className="text-sm font-medium opacity-80 mb-1">Overall Score</p>
        <p className="text-2xl font-bold">{score}/100</p>
      </div>
      <div className={cn(
        "px-4 py-2 rounded-full text-sm font-semibold",
        score >= 70 ? "bg-green-600 text-white" :
        score >= 50 ? "bg-yellow-600 text-white" :
        "bg-red-600 text-white"
      )}>
        {getScoreLabel(score)}
      </div>
    </div>
  )
}
