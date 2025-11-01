"use client"

import { Progress } from "@/components/ui/progress"
import { motion } from "framer-motion"

export interface InterviewProgressProps {
  current: number
  total: number
}

/**
 * InterviewProgress Component
 * Displays progress bar and text showing question completion
 * - Positioned at top of chat interface
 * - Smooth animation transitions with Framer Motion
 */
export default function InterviewProgress({ current, total }: InterviewProgressProps) {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0

  return (
    <div className="sticky top-0 bg-background p-4 border-b border-border z-10">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <p className="text-sm text-muted-foreground font-medium mb-2">
          Question {current} of {total} ({percentage}% complete)
        </p>

        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          style={{ transformOrigin: "left" }}
        >
          <Progress value={percentage} className="h-2" />
        </motion.div>
      </motion.div>
    </div>
  )
}
