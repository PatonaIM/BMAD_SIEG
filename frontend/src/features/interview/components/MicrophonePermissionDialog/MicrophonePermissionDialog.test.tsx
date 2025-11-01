import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MicrophonePermissionDialog } from './MicrophonePermissionDialog';

// Mock navigator.mediaDevices
const mockGetUserMedia = vi.fn();
const mockPermissionsQuery = vi.fn();

beforeEach(() => {
  // Reset mocks
  mockGetUserMedia.mockReset();
  mockPermissionsQuery.mockReset();
  localStorage.clear();

  // Mock navigator.mediaDevices
  Object.defineProperty(global.navigator, 'mediaDevices', {
    value: {
      getUserMedia: mockGetUserMedia,
    },
    writable: true,
    configurable: true,
  });

  // Mock navigator.permissions
  Object.defineProperty(global.navigator, 'permissions', {
    value: {
      query: mockPermissionsQuery,
    },
    writable: true,
    configurable: true,
  });
});

describe('MicrophonePermissionDialog', () => {
  it('renders prompt state with permission request', async () => {
    mockPermissionsQuery.mockResolvedValue({ state: 'prompt' });
    
    render(<MicrophonePermissionDialog />);
    
    await waitFor(() => {
      expect(screen.getByText(/microphone access required/i)).toBeInTheDocument();
      expect(screen.getByText(/allow microphone/i)).toBeInTheDocument();
    });
  });

  it('does not render when permission already granted', async () => {
    localStorage.setItem('microphone_permission', 'granted');
    
    const { container } = render(<MicrophonePermissionDialog />);
    
    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it('calls onPermissionGranted when permission is granted', async () => {
    const onPermissionGranted = vi.fn();
    const mockStream = {
      getTracks: () => [{ stop: vi.fn() }],
    };
    
    mockPermissionsQuery.mockResolvedValue({ state: 'prompt' });
    mockGetUserMedia.mockResolvedValue(mockStream);
    
    render(<MicrophonePermissionDialog onPermissionGranted={onPermissionGranted} />);
    
    await waitFor(() => {
      const button = screen.getByText(/allow microphone/i);
      fireEvent.click(button);
    });
    
    await waitFor(() => {
      expect(onPermissionGranted).toHaveBeenCalled();
      expect(localStorage.getItem('microphone_permission')).toBe('granted');
    });
  });

  it('shows denied state when permission is denied', async () => {
    const onPermissionDenied = vi.fn();
    
    mockPermissionsQuery.mockResolvedValue({ state: 'prompt' });
    mockGetUserMedia.mockRejectedValue(new Error('Permission denied'));
    
    render(<MicrophonePermissionDialog onPermissionDenied={onPermissionDenied} />);
    
    await waitFor(() => {
      const button = screen.getByText(/allow microphone/i);
      fireEvent.click(button);
    });
    
    await waitFor(() => {
      expect(screen.getByText(/microphone access denied/i)).toBeInTheDocument();
      expect(onPermissionDenied).toHaveBeenCalled();
      expect(localStorage.getItem('microphone_permission')).toBe('denied');
    });
  });

  it('shows instructions for enabling microphone when denied', async () => {
    mockPermissionsQuery.mockResolvedValue({ state: 'denied' });
    
    render(<MicrophonePermissionDialog />);
    
    await waitFor(() => {
      expect(screen.getByText(/how to enable/i)).toBeInTheDocument();
      expect(screen.getByText(/click the lock icon/i)).toBeInTheDocument();
    });
  });

  it('provides refresh and text input fallback options when denied', async () => {
    mockPermissionsQuery.mockResolvedValue({ state: 'denied' });
    
    render(<MicrophonePermissionDialog />);
    
    await waitFor(() => {
      expect(screen.getByText(/refresh page/i)).toBeInTheDocument();
      expect(screen.getByText(/use text input/i)).toBeInTheDocument();
    });
  });

  it('hides dialog when "Use Text Input" is clicked', async () => {
    mockPermissionsQuery.mockResolvedValue({ state: 'denied' });
    
    const { container } = render(<MicrophonePermissionDialog />);
    
    await waitFor(() => {
      const button = screen.getByText(/use text input/i);
      fireEvent.click(button);
    });
    
    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it('shows checking state initially', () => {
    mockPermissionsQuery.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<MicrophonePermissionDialog />);
    
    // Look for the spinner element
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('respects show prop', async () => {
    mockPermissionsQuery.mockResolvedValue({ state: 'prompt' });
    
    const { rerender, container } = render(
      <MicrophonePermissionDialog show={false} />
    );
    
    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
    
    rerender(<MicrophonePermissionDialog show={true} />);
    
    await waitFor(() => {
      expect(screen.getByText(/microphone access required/i)).toBeInTheDocument();
    });
  });
});
