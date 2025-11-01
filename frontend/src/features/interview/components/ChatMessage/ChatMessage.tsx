import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bot } from "lucide-react"
import { memo } from "react"

export interface ChatMessageProps {
  role: "ai" | "candidate"
  content: string
  timestamp: number
}

/**
 * ChatMessage Component
 * Displays a single message bubble in the interview chat
 * - AI messages: Left-aligned, brand purple background, white text
 * - Candidate messages: Right-aligned, light grey background, dark text
 * - Responsive design for different screen sizes
 * - Full accessibility support
 * - Memoized for performance optimization (PERF-001)
 */
const ChatMessage = memo(function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const isAI = role === "ai"

  // Format timestamp as HH:mm AM/PM
  const formatTime = (ts: number) => {
    const date = new Date(ts)
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  }

  return (
    <div
      className={`flex ${isAI ? "flex-row" : "flex-row-reverse"} items-start gap-2 mb-4`}
      role="article"
      aria-label={`${isAI ? "AI interviewer" : "Your"} message at ${formatTime(timestamp)}`}
    >
      {/* Avatar - only show for AI messages */}
      {isAI && (
        <Avatar className="w-9 h-9 lg:w-10 lg:h-10 bg-primary">
          <AvatarFallback className="bg-primary text-primary-foreground">
            <Bot className="w-4 h-4 lg:w-5 lg:h-5" />
          </AvatarFallback>
        </Avatar>
      )}

      {/* Message bubble */}
      <div className="max-w-[80%] lg:max-w-[70%] flex flex-col gap-1">
        <div
          className={`px-3 py-2 lg:px-4 lg:py-3 rounded-lg break-words ${
            isAI ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
          }`}
        >
          <p className="text-sm lg:text-base">{content}</p>
        </div>

        {/* Timestamp */}
        <time
          className={`text-xs lg:text-sm text-muted-foreground px-2 ${isAI ? "self-start" : "self-end"}`}
          dateTime={new Date(timestamp).toISOString()}
        >
          {formatTime(timestamp)}
        </time>
      </div>
    </div>
  )
})

export default ChatMessage
