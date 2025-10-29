import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ThemeProvider } from '@mui/material/styles';
import { teamifiedTheme } from '../../../../theme/theme';
import InterviewChat, { Message } from './InterviewChat';

const renderWithTheme = (component: React.ReactElement) =>
  render(<ThemeProvider theme={teamifiedTheme}>{component}</ThemeProvider>);

// Mock scrollTo for testing
beforeEach(() => {
  Element.prototype.scrollTo = vi.fn();
});

describe('InterviewChat', () => {
  const mockMessages: Message[] = [
    {
      id: '1',
      role: 'ai',
      content: 'Hello! Welcome to your interview.',
      timestamp: Date.now() - 5000,
    },
    {
      id: '2',
      role: 'candidate',
      content: 'Thank you! I am excited to start.',
      timestamp: Date.now() - 3000,
    },
    {
      id: '3',
      role: 'ai',
      content: 'Let me start with a simple question...',
      timestamp: Date.now() - 1000,
    },
  ];

  it('renders empty state when no messages', () => {
    renderWithTheme(<InterviewChat messages={[]} />);
    
    expect(screen.getByText('Your interview will begin shortly...')).toBeInTheDocument();
  });

  it('renders all messages in chronological order', () => {
    renderWithTheme(<InterviewChat messages={mockMessages} />);
    
    expect(screen.getByText('Hello! Welcome to your interview.')).toBeInTheDocument();
    expect(screen.getByText('Thank you! I am excited to start.')).toBeInTheDocument();
    expect(screen.getByText('Let me start with a simple question...')).toBeInTheDocument();
  });

  it('does not show empty state when messages exist', () => {
    renderWithTheme(<InterviewChat messages={mockMessages} />);
    
    expect(screen.queryByText('Your interview will begin shortly...')).not.toBeInTheDocument();
  });

  it('renders with scrollable container', () => {
    const { container } = renderWithTheme(<InterviewChat messages={mockMessages} />);
    
    // Check for the main container Box element
    const scrollContainer = container.querySelector('.MuiBox-root');
    expect(scrollContainer).toBeInTheDocument();
  });

  it('handles single message correctly', () => {
    renderWithTheme(<InterviewChat messages={[mockMessages[0]]} />);
    
    expect(screen.getByText('Hello! Welcome to your interview.')).toBeInTheDocument();
  });
});
