"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bot } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export interface TypingIndicatorProps {
  isVisible?: boolean
}

/**
 * TypingIndicator Component
 * Shows animated dots to indicate AI is generating a response
 * - Left-aligned like AI messages
 * - Smooth enter/exit animations with Framer Motion
 */
export default function TypingIndicator({ isVisible = true }: TypingIndicatorProps) {
  if (!isVisible) return null

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.25 }}
        >
          <div className="flex items-start gap-2 mb-4">
            {/* AI Avatar */}
            <Avatar className="w-10 h-10 bg-primary">
              <AvatarFallback className="bg-primary text-primary-foreground">
                <Bot className="w-5 h-5" />
              </AvatarFallback>
            </Avatar>

            {/* Typing bubble */}
            <div className="bg-primary px-4 py-3 rounded-lg flex items-center gap-1 min-w-[70px]">
              <span className="w-2 h-2 rounded-full bg-primary-foreground animate-bounce [animation-delay:-0.3s]" />
              <span className="w-2 h-2 rounded-full bg-primary-foreground animate-bounce [animation-delay:-0.15s]" />
              <span className="w-2 h-2 rounded-full bg-primary-foreground animate-bounce" />
              {/* Hidden text for screen readers */}
              <span className="sr-only">AI is thinking...</span>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
