/**
 * Caption Queue System
 * 
 * Manages AI caption timing and display logic.
 * - Filters candidate captions (only shows AI captions)
 * - Tracks caption visibility state
 * - Maintains caption history
 */

export interface CaptionItem {
  text: string
  timestamp: number
  role: 'user' | 'assistant'
  isVisible: boolean
}

export class CaptionQueue {
  private queue: CaptionItem[] = []
  private maxHistorySize: number

  constructor(maxHistorySize: number = 10) {
    this.maxHistorySize = maxHistorySize
  }

  /**
   * Add a new caption to the queue
   * Only AI captions are added (user captions are filtered out)
   */
  enqueue(text: string, role: 'user' | 'assistant'): void {
    // Filter out user captions - only show AI captions
    if (role === 'user') {
      return
    }

    const caption: CaptionItem = {
      text,
      timestamp: Date.now(),
      role,
      isVisible: true
    }

    this.queue.push(caption)

    // Limit queue size to maxHistorySize
    if (this.queue.length > this.maxHistorySize) {
      this.queue.shift()
    }
  }

  /**
   * Get the current caption to display
   * Returns the most recent caption or null if queue is empty
   */
  getCurrent(): CaptionItem | null {
    if (this.queue.length === 0) {
      return null
    }
    return this.queue[this.queue.length - 1]
  }

  /**
   * Get last N captions for history display
   * Returns captions in reverse chronological order (newest first)
   */
  getHistory(count: number): CaptionItem[] {
    const start = Math.max(0, this.queue.length - count)
    return this.queue.slice(start).reverse()
  }

  /**
   * Clear all captions from the queue
   */
  clear(): void {
    this.queue = []
  }

  /**
   * Update visibility of the current caption
   */
  setCurrentVisibility(isVisible: boolean): void {
    const current = this.getCurrent()
    if (current) {
      current.isVisible = isVisible
    }
  }
}
