/**
 * Caption Queue Tests
 * 
 * Tests for caption queue management system
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { CaptionQueue } from '@/src/features/interview/utils/captionQueue'

describe('CaptionQueue', () => {
  let queue: CaptionQueue

  beforeEach(() => {
    queue = new CaptionQueue(10)
  })

  describe('enqueue', () => {
    it('should add AI captions to the queue', () => {
      queue.enqueue('Test caption', 'assistant')
      
      const current = queue.getCurrent()
      expect(current).toBeDefined()
      expect(current?.text).toBe('Test caption')
      expect(current?.role).toBe('assistant')
      expect(current?.isVisible).toBe(true)
    })

    it('should filter out user captions', () => {
      queue.enqueue('User message', 'user')
      
      const current = queue.getCurrent()
      expect(current).toBeNull()
    })

    it('should maintain max history size', () => {
      const smallQueue = new CaptionQueue(3)
      
      smallQueue.enqueue('Caption 1', 'assistant')
      smallQueue.enqueue('Caption 2', 'assistant')
      smallQueue.enqueue('Caption 3', 'assistant')
      smallQueue.enqueue('Caption 4', 'assistant')
      
      const history = smallQueue.getHistory(10)
      expect(history.length).toBe(3)
      expect(history[0].text).toBe('Caption 4') // Most recent first
    })

    it('should set timestamp on caption', () => {
      const before = Date.now()
      queue.enqueue('Test caption', 'assistant')
      const after = Date.now()
      
      const current = queue.getCurrent()
      expect(current?.timestamp).toBeGreaterThanOrEqual(before)
      expect(current?.timestamp).toBeLessThanOrEqual(after)
    })
  })

  describe('getCurrent', () => {
    it('should return null for empty queue', () => {
      const current = queue.getCurrent()
      expect(current).toBeNull()
    })

    it('should return most recent caption', () => {
      queue.enqueue('Caption 1', 'assistant')
      queue.enqueue('Caption 2', 'assistant')
      
      const current = queue.getCurrent()
      expect(current?.text).toBe('Caption 2')
    })
  })

  describe('getHistory', () => {
    it('should return empty array for empty queue', () => {
      const history = queue.getHistory(3)
      expect(history).toEqual([])
    })

    it('should return captions in reverse chronological order', () => {
      queue.enqueue('Caption 1', 'assistant')
      queue.enqueue('Caption 2', 'assistant')
      queue.enqueue('Caption 3', 'assistant')
      
      const history = queue.getHistory(3)
      expect(history.length).toBe(3)
      expect(history[0].text).toBe('Caption 3')
      expect(history[1].text).toBe('Caption 2')
      expect(history[2].text).toBe('Caption 1')
    })

    it('should limit results to requested count', () => {
      queue.enqueue('Caption 1', 'assistant')
      queue.enqueue('Caption 2', 'assistant')
      queue.enqueue('Caption 3', 'assistant')
      
      const history = queue.getHistory(2)
      expect(history.length).toBe(2)
      expect(history[0].text).toBe('Caption 3')
      expect(history[1].text).toBe('Caption 2')
    })
  })

  describe('clear', () => {
    it('should remove all captions from queue', () => {
      queue.enqueue('Caption 1', 'assistant')
      queue.enqueue('Caption 2', 'assistant')
      
      queue.clear()
      
      expect(queue.getCurrent()).toBeNull()
      expect(queue.getHistory(10)).toEqual([])
    })
  })

  describe('setCurrentVisibility', () => {
    it('should update visibility of current caption', () => {
      queue.enqueue('Test caption', 'assistant')
      
      const before = queue.getCurrent()
      expect(before?.isVisible).toBe(true)
      
      queue.setCurrentVisibility(false)
      
      const after = queue.getCurrent()
      expect(after?.isVisible).toBe(false)
    })

    it('should do nothing for empty queue', () => {
      expect(() => queue.setCurrentVisibility(false)).not.toThrow()
    })
  })
})
