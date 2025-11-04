/**
 * Text Segmentation Utilities
 * 
 * Utilities for breaking long AI responses into readable caption segments
 * and sanitizing caption text.
 */

const MAX_CHARS_PER_SEGMENT = 120 // ~2 lines of text
const SENTENCE_ENDINGS = /[.!?]+\s+/g
const MARKDOWN_PATTERNS = /(\*\*|__|`|#|_)/g
const MULTIPLE_SPACES = /\s+/g
const ABBREVIATIONS = ['Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Sr.', 'Jr.', 'e.g.', 'i.e.', 'etc.']

/**
 * Sanitize caption text by removing markdown and cleaning punctuation
 * 
 * @param text - Raw caption text
 * @returns Cleaned text suitable for display
 * 
 * @example
 * sanitizeCaptionText("**Hello**  world!") // => "Hello world!"
 */
export function sanitizeCaptionText(text: string): string {
  if (!text) return ''

  let cleaned = text

  // Remove markdown formatting
  cleaned = cleaned.replace(MARKDOWN_PATTERNS, '')

  // Decode HTML entities
  const textarea = document.createElement('textarea')
  textarea.innerHTML = cleaned
  cleaned = textarea.value

  // Clean punctuation
  cleaned = cleaned.replace(MULTIPLE_SPACES, ' ')
  cleaned = cleaned.trim()

  return cleaned
}

/**
 * Segment long caption text into readable chunks
 * 
 * Breaks text at:
 * 1. Sentence boundaries (., !, ?)
 * 2. Natural clause breaks (,, ;, and, but)
 * 3. Max character limit (~120 chars, ~2 lines)
 * 
 * @param text - Caption text to segment
 * @returns Array of text segments
 * 
 * @example
 * segmentCaptionText("This is a long sentence. And another one!")
 * // => ["This is a long sentence.", "And another one!"]
 */
export function segmentCaptionText(text: string): string[] {
  if (!text) return []

  // Sanitize first
  const cleaned = sanitizeCaptionText(text)

  // If text is short enough, return as single segment
  if (cleaned.length <= MAX_CHARS_PER_SEGMENT) {
    return [cleaned]
  }

  const segments: string[] = []
  let currentSegment = ''

  // Split by sentences first
  const sentences = splitBySentences(cleaned)

  for (const sentence of sentences) {
    // If sentence itself is too long, split further
    if (sentence.length > MAX_CHARS_PER_SEGMENT) {
      // Flush current segment if exists
      if (currentSegment) {
        segments.push(currentSegment.trim())
        currentSegment = ''
      }

      // Split long sentence at clause boundaries
      const clauses = splitByClauses(sentence)
      for (const clause of clauses) {
        if (clause.length > MAX_CHARS_PER_SEGMENT) {
          // If even a clause is too long, split at max length
          segments.push(...splitAtMaxLength(clause))
        } else {
          segments.push(clause.trim())
        }
      }
    } else {
      // Check if adding this sentence exceeds max length
      const testSegment = currentSegment ? `${currentSegment} ${sentence}` : sentence

      if (testSegment.length > MAX_CHARS_PER_SEGMENT) {
        // Flush current segment and start new one
        if (currentSegment) {
          segments.push(currentSegment.trim())
        }
        currentSegment = sentence
      } else {
        currentSegment = testSegment
      }
    }
  }

  // Add any remaining segment
  if (currentSegment) {
    segments.push(currentSegment.trim())
  }

  return segments.filter(s => s.length > 0)
}

/**
 * Split text by sentence boundaries, handling abbreviations
 */
function splitBySentences(text: string): string[] {
  // Replace abbreviations temporarily to avoid false splits
  let protectedText = text
  const abbreviationMap: { [key: string]: string } = {}

  ABBREVIATIONS.forEach((abbr, index) => {
    const placeholder = `__ABBR${index}__`
    abbreviationMap[placeholder] = abbr
    protectedText = protectedText.replace(new RegExp(abbr.replace('.', '\\.'), 'g'), placeholder)
  })

  // Split by sentence endings
  const sentences = protectedText.split(SENTENCE_ENDINGS)

  // Restore abbreviations
  return sentences.map(sentence => {
    let restored = sentence
    Object.entries(abbreviationMap).forEach(([placeholder, abbr]) => {
      restored = restored.replace(new RegExp(placeholder, 'g'), abbr)
    })
    return restored
  }).filter(s => s.trim().length > 0)
}

/**
 * Split text by clause boundaries (commas, semicolons, conjunctions)
 */
function splitByClauses(text: string): string[] {
  // Split at commas, semicolons, and common conjunctions
  const clausePattern = /(?:,\s+(?:and|but|or|yet|so)|;\s+|\s+and\s+|\s+but\s+)/gi
  return text.split(clausePattern).filter(s => s.trim().length > 0)
}

/**
 * Split text at max character length (last resort)
 */
function splitAtMaxLength(text: string): string[] {
  const segments: string[] = []
  let remaining = text

  while (remaining.length > MAX_CHARS_PER_SEGMENT) {
    // Try to split at last space before max length
    let splitIndex = MAX_CHARS_PER_SEGMENT
    const lastSpace = remaining.lastIndexOf(' ', MAX_CHARS_PER_SEGMENT)

    if (lastSpace > MAX_CHARS_PER_SEGMENT * 0.7) {
      // Good split point found (not too far back)
      splitIndex = lastSpace
    }

    segments.push(remaining.substring(0, splitIndex).trim())
    remaining = remaining.substring(splitIndex).trim()
  }

  if (remaining) {
    segments.push(remaining)
  }

  return segments
}
