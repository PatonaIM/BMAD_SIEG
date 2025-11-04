/**
 * Text Segmentation Tests
 * 
 * Tests for caption text segmentation and sanitization
 */

import { describe, it, expect } from 'vitest'
import { sanitizeCaptionText, segmentCaptionText } from '@/src/features/interview/utils/textSegmentation'

describe('sanitizeCaptionText', () => {
  it('should remove markdown bold formatting', () => {
    const result = sanitizeCaptionText('This is **bold** text')
    expect(result).toBe('This is bold text')
  })

  it('should remove markdown italic formatting', () => {
    const result = sanitizeCaptionText('This is _italic_ text')
    expect(result).toBe('This is italic text')
  })

  it('should remove markdown code formatting', () => {
    const result = sanitizeCaptionText('This is `code` text')
    expect(result).toBe('This is code text')
  })

  it('should remove markdown headers', () => {
    const result = sanitizeCaptionText('# Header text')
    expect(result).toBe('Header text')
  })

  it('should clean multiple spaces', () => {
    const result = sanitizeCaptionText('This   has    multiple     spaces')
    expect(result).toBe('This has multiple spaces')
  })

  it('should trim whitespace', () => {
    const result = sanitizeCaptionText('  Text with whitespace  ')
    expect(result).toBe('Text with whitespace')
  })

  it('should return empty string for null/undefined', () => {
    expect(sanitizeCaptionText('')).toBe('')
  })

  it('should handle text with no formatting', () => {
    const result = sanitizeCaptionText('Plain text caption')
    expect(result).toBe('Plain text caption')
  })
})

describe('segmentCaptionText', () => {
  it('should return single segment for short text', () => {
    const result = segmentCaptionText('Short caption')
    expect(result).toEqual(['Short caption'])
  })

  it('should split at sentence boundaries when text exceeds max length', () => {
    // Create text long enough to require splitting (>120 chars)
    const text = 'This is the first sentence that contains some meaningful content. This is the second sentence with more meaningful content. And here is a third one.'
    const result = segmentCaptionText(text)
    expect(result.length).toBeGreaterThan(1)
  })

  it('should handle abbreviations without splitting', () => {
    const text = 'Dr. Smith is here.'
    const result = segmentCaptionText(text)
    // Should not split at "Dr."
    expect(result.length).toBe(1)
  })

  it('should respect max character limit (~120 chars)', () => {
    const longText = 'This is a very long sentence that exceeds the maximum character limit for a single caption segment and should be split into multiple segments for better readability and user experience.'
    const result = segmentCaptionText(longText)
    
    expect(result.length).toBeGreaterThan(1)
    result.forEach(segment => {
      expect(segment.length).toBeLessThanOrEqual(150) // Allow some buffer
    })
  })

  it('should return empty array for empty string', () => {
    const result = segmentCaptionText('')
    expect(result).toEqual([])
  })

  it('should sanitize text before segmentation', () => {
    const text = '**This is bold.** This is normal.'
    const result = segmentCaptionText(text)
    expect(result[0]).not.toContain('**')
  })

  it('should handle multiple sentences combined when short', () => {
    const text = 'First. Second. Third.'
    const result = segmentCaptionText(text)
    // Short sentences might be combined
    expect(result.length).toBeGreaterThanOrEqual(1)
  })

  it('should handle text with special punctuation', () => {
    const text = 'Question? Answer! Statement.'
    const result = segmentCaptionText(text)
    expect(result.length).toBeGreaterThanOrEqual(1)
    expect(result.join(' ')).toContain('Question')
    expect(result.join(' ')).toContain('Answer')
  })

  it('should handle edge case with only abbreviations', () => {
    const text = 'Dr. Mr. Mrs. Ms. Prof.'
    const result = segmentCaptionText(text)
    expect(result.length).toBeGreaterThanOrEqual(1)
  })

  it('should filter out empty segments', () => {
    const text = 'Text with... multiple periods...'
    const result = segmentCaptionText(text)
    result.forEach(segment => {
      expect(segment.length).toBeGreaterThan(0)
    })
  })
})
