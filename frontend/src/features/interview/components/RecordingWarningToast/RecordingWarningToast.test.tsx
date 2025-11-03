/**
 * Recording Warning Toast Tests
 */

import { render } from '@testing-library/react'
import { RecordingWarningToast } from './RecordingWarningToast'
import { describe, it, expect, beforeEach, afterEach } from 'vitest'

describe('RecordingWarningToast', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('renders without crashing', () => {
    render(
      <RecordingWarningToast 
        sessionId="test-session-123"
        isRecording={true}
      />
    )
    // Component returns null, so no DOM assertions needed
    expect(true).toBe(true)
  })

  it('stores flag in localStorage when recording starts', () => {
    render(
      <RecordingWarningToast 
        sessionId="test-session-123"
        isRecording={true}
      />
    )
    
    // Check localStorage flag was set
    expect(localStorage.getItem('interview_recording_warning_shown_test-session-123')).toBe('true')
  })

  it('does not store flag when not recording', () => {
    render(
      <RecordingWarningToast 
        sessionId="test-session-123"
        isRecording={false}
      />
    )
    
    expect(localStorage.getItem('interview_recording_warning_shown_test-session-123')).toBeNull()
  })

  it('does not store flag without session ID', () => {
    render(
      <RecordingWarningToast 
        sessionId=""
        isRecording={true}
      />
    )
    
    expect(localStorage.getItem('interview_recording_warning_shown_')).toBeNull()
  })

  it('creates unique storage keys for different sessions', () => {
    const { rerender } = render(
      <RecordingWarningToast 
        sessionId="session-1"
        isRecording={true}
      />
    )
    
    expect(localStorage.getItem('interview_recording_warning_shown_session-1')).toBe('true')
    
    rerender(
      <RecordingWarningToast 
        sessionId="session-2"
        isRecording={true}
      />
    )
    
    expect(localStorage.getItem('interview_recording_warning_shown_session-2')).toBe('true')
  })
})
