import { describe, it, expect, beforeEach } from 'vitest';
import { useInterviewStore } from './interviewStore';

describe('InterviewStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useInterviewStore.getState().reset();
  });

  it('initializes with default state', () => {
    const state = useInterviewStore.getState();
    
    expect(state.sessionId).toBeNull();
    expect(state.messages).toEqual([]);
    expect(state.currentQuestion).toBe(0);
    expect(state.totalQuestions).toBe(0);
    expect(state.isAiTyping).toBe(false);
    expect(state.status).toBe('not_started');
  });

  it('sets session ID', () => {
    const { setSessionId } = useInterviewStore.getState();
    
    setSessionId('test-session-123');
    
    expect(useInterviewStore.getState().sessionId).toBe('test-session-123');
  });

  it('adds message with generated ID and timestamp', () => {
    const { addMessage } = useInterviewStore.getState();
    
    addMessage({
      role: 'ai',
      content: 'Hello, welcome to your interview!',
    });
    
    const state = useInterviewStore.getState();
    expect(state.messages).toHaveLength(1);
    expect(state.messages[0]).toMatchObject({
      role: 'ai',
      content: 'Hello, welcome to your interview!',
    });
    expect(state.messages[0].id).toBeDefined();
    expect(state.messages[0].timestamp).toBeGreaterThan(0);
  });

  it('adds multiple messages in order', () => {
    const { addMessage } = useInterviewStore.getState();
    
    addMessage({ role: 'ai', content: 'First message' });
    addMessage({ role: 'candidate', content: 'Second message' });
    addMessage({ role: 'ai', content: 'Third message' });
    
    const state = useInterviewStore.getState();
    expect(state.messages).toHaveLength(3);
    expect(state.messages[0].content).toBe('First message');
    expect(state.messages[1].content).toBe('Second message');
    expect(state.messages[2].content).toBe('Third message');
  });

  it('sets AI typing state', () => {
    const { setAiTyping } = useInterviewStore.getState();
    
    setAiTyping(true);
    expect(useInterviewStore.getState().isAiTyping).toBe(true);
    
    setAiTyping(false);
    expect(useInterviewStore.getState().isAiTyping).toBe(false);
  });

  it('updates progress', () => {
    const { updateProgress } = useInterviewStore.getState();
    
    updateProgress(5, 10);
    
    const state = useInterviewStore.getState();
    expect(state.currentQuestion).toBe(5);
    expect(state.totalQuestions).toBe(10);
  });

  it('sets status', () => {
    const { setStatus } = useInterviewStore.getState();
    
    setStatus('in_progress');
    expect(useInterviewStore.getState().status).toBe('in_progress');
    
    setStatus('completed');
    expect(useInterviewStore.getState().status).toBe('completed');
  });

  it('resets to initial state', () => {
    const { setSessionId, addMessage, updateProgress, setAiTyping, setStatus, reset } = 
      useInterviewStore.getState();
    
    // Modify state
    setSessionId('test-123');
    addMessage({ role: 'ai', content: 'Test' });
    updateProgress(5, 10);
    setAiTyping(true);
    setStatus('in_progress');
    
    // Reset
    reset();
    
    const state = useInterviewStore.getState();
    expect(state.sessionId).toBeNull();
    expect(state.messages).toEqual([]);
    expect(state.currentQuestion).toBe(0);
    expect(state.totalQuestions).toBe(0);
    expect(state.isAiTyping).toBe(false);
    expect(state.status).toBe('not_started');
  });
});
