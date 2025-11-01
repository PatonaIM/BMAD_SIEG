"use client"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Spinner } from "@/components/ui/spinner"
import { Send } from "lucide-react"
import { useState, useRef, useEffect } from "react"
import type { KeyboardEvent } from "react"

export interface ChatInputProps {
  onSubmit: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

const MAX_CHARACTERS = 2000

/**
 * ChatInput Component
 * Multiline text input with character counter and submit button
 * - Enter key submits message
 * - Shift+Enter creates new line
 * - Responsive design for different screen sizes
 * - Full accessibility support
 */
export default function ChatInput({
  onSubmit,
  disabled = false,
  placeholder = "Type your response...",
}: ChatInputProps) {
  const [message, setMessage] = useState("")
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const charCount = message.length
  const isOverLimit = charCount > MAX_CHARACTERS
  const isEmpty = message.trim().length === 0
  const isSubmitDisabled = disabled || isEmpty || isOverLimit

  // Return focus to input after message sent
  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus()
    }
  }, [disabled])

  const handleSubmit = () => {
    if (isSubmitDisabled) return

    const trimmedMessage = message.trim()
    if (trimmedMessage) {
      onSubmit(trimmedMessage)
      setMessage("")
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
    // Allow Shift+Enter for new line (default behavior)
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        handleSubmit()
      }}
      className="p-4 lg:p-6 bg-background border-t border-border flex gap-2 lg:gap-4 items-end"
    >
      <div className="flex-1">
        <Textarea
          ref={inputRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          aria-label="Interview response input"
          aria-describedby="char-count-label keyboard-hint-label"
          aria-required="true"
          aria-invalid={isOverLimit}
          className={`min-h-[56px] max-h-[120px] resize-none ${disabled ? "bg-muted" : ""}`}
        />
        <div className="flex justify-between items-center mt-2 px-2 flex-col lg:flex-row gap-1 lg:gap-0">
          <span
            id="char-count-label"
            className={`text-xs lg:text-sm ${isOverLimit ? "text-destructive" : "text-muted-foreground"}`}
            role="status"
            aria-live="polite"
          >
            {charCount}/{MAX_CHARACTERS} characters
          </span>
          <span
            id="keyboard-hint-label"
            className="hidden lg:inline text-xs text-muted-foreground"
            aria-label="Keyboard shortcuts"
          >
            Press Enter to send, Shift+Enter for new line
          </span>
        </div>
      </div>

      <Button
        type="submit"
        disabled={isSubmitDisabled}
        aria-label={disabled ? "Sending message..." : "Send message"}
        className="min-w-[90px] lg:min-w-[120px] h-14"
        size="lg"
      >
        {disabled ? <Spinner className="mr-2" /> : <Send className="mr-2 h-4 w-4" />}
        Send
      </Button>
    </form>
  )
}
