import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ThemeProvider } from '@mui/material/styles';
import { teamifiedTheme } from '../../../../theme/theme';
import InterviewProgress from './InterviewProgress';

const renderWithTheme = (component: React.ReactElement) =>
  render(<ThemeProvider theme={teamifiedTheme}>{component}</ThemeProvider>);

describe('InterviewProgress', () => {
  it('renders progress text correctly', () => {
    renderWithTheme(<InterviewProgress current={3} total={10} />);
    
    expect(screen.getByText('Question 3 of 10 (30% complete)')).toBeInTheDocument();
  });

  it('calculates percentage correctly', () => {
    renderWithTheme(<InterviewProgress current={5} total={10} />);
    
    expect(screen.getByText('Question 5 of 10 (50% complete)')).toBeInTheDocument();
  });

  it('handles 0% progress', () => {
    renderWithTheme(<InterviewProgress current={0} total={10} />);
    
    expect(screen.getByText('Question 0 of 10 (0% complete)')).toBeInTheDocument();
  });

  it('handles 100% progress', () => {
    renderWithTheme(<InterviewProgress current={10} total={10} />);
    
    expect(screen.getByText('Question 10 of 10 (100% complete)')).toBeInTheDocument();
  });

  it('renders progress bar', () => {
    const { container } = renderWithTheme(<InterviewProgress current={5} total={10} />);
    
    const progressBar = container.querySelector('[role="progressbar"]');
    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveAttribute('aria-valuenow', '50');
  });

  it('handles edge case when total is 0', () => {
    renderWithTheme(<InterviewProgress current={0} total={0} />);
    
    expect(screen.getByText('Question 0 of 0 (0% complete)')).toBeInTheDocument();
  });

  it('rounds percentage to nearest integer', () => {
    renderWithTheme(<InterviewProgress current={1} total={3} />);
    
    // 1/3 = 33.333%, should round to 33%
    expect(screen.getByText('Question 1 of 3 (33% complete)')).toBeInTheDocument();
  });
});
