import React, { useEffect, useState } from 'react';
import { Mic, AlertCircle, CheckCircle } from 'lucide-react';

export interface MicrophonePermissionDialogProps {
  onPermissionGranted?: () => void;
  onPermissionDenied?: () => void;
  show?: boolean;
}

type PermissionState = 'prompt' | 'granted' | 'denied' | 'checking';

/**
 * Dialog for requesting microphone permissions
 * Shows explanation and handles permission states
 */
export function MicrophonePermissionDialog({
  onPermissionGranted,
  onPermissionDenied,
  show = true,
}: MicrophonePermissionDialogProps) {
  const [permissionState, setPermissionState] = useState<PermissionState>('checking');
  const [isVisible, setIsVisible] = useState(show);

  useEffect(() => {
    checkPermissionStatus();
  }, []);

  useEffect(() => {
    setIsVisible(show);
  }, [show]);

  /**
   * Check current permission status from localStorage and browser
   */
  const checkPermissionStatus = async () => {
    // Check localStorage first
    const storedPermission = localStorage.getItem('microphone_permission');
    
    if (storedPermission === 'granted') {
      setPermissionState('granted');
      setIsVisible(false);
      onPermissionGranted?.();
      return;
    }

    if (storedPermission === 'denied') {
      setPermissionState('denied');
      return;
    }

    // Check browser permission API if available
    if (navigator.permissions && navigator.permissions.query) {
      try {
        const result = await navigator.permissions.query({ name: 'microphone' as PermissionName });
        
        if (result.state === 'granted') {
          setPermissionState('granted');
          localStorage.setItem('microphone_permission', 'granted');
          setIsVisible(false);
          onPermissionGranted?.();
        } else if (result.state === 'denied') {
          setPermissionState('denied');
          localStorage.setItem('microphone_permission', 'denied');
          onPermissionDenied?.();
        } else {
          setPermissionState('prompt');
        }
      } catch (error) {
        // Fallback if permission API not supported
        setPermissionState('prompt');
      }
    } else {
      setPermissionState('prompt');
    }
  };

  /**
   * Request microphone permission
   */
  const requestPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Permission granted
      stream.getTracks().forEach(track => track.stop());
      setPermissionState('granted');
      localStorage.setItem('microphone_permission', 'granted');
      setIsVisible(false);
      onPermissionGranted?.();
    } catch (error) {
      // Permission denied
      setPermissionState('denied');
      localStorage.setItem('microphone_permission', 'denied');
      onPermissionDenied?.();
    }
  };

  if (!isVisible || permissionState === 'granted') {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className={`p-3 rounded-full ${
            permissionState === 'denied' ? 'bg-red-100' : 'bg-purple-100'
          }`}>
            {permissionState === 'denied' ? (
              <AlertCircle className="w-6 h-6 text-red-600" />
            ) : (
              <Mic className="w-6 h-6 text-purple-600" />
            )}
          </div>
          <h2 className="text-xl font-semibold text-gray-900">
            {permissionState === 'denied' ? 'Microphone Access Denied' : 'Microphone Access Required'}
          </h2>
        </div>

        {/* Content */}
        {permissionState === 'prompt' && (
          <>
            <p className="text-gray-700 mb-4">
              To participate in the voice interview, we need access to your microphone. 
              Your responses will be recorded and transcribed to help us evaluate your skills.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">Why we need this:</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Record your spoken answers during the interview</li>
                <li>• Convert speech to text for analysis</li>
                <li>• Provide a natural conversation experience</li>
              </ul>
            </div>
            <button
              onClick={requestPermission}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Allow Microphone
            </button>
            <p className="text-xs text-gray-500 mt-3 text-center">
              You can also use text input if you prefer
            </p>
          </>
        )}

        {permissionState === 'denied' && (
          <>
            <p className="text-gray-700 mb-4">
              Microphone access was denied. To use voice input, please enable microphone 
              permissions in your browser settings.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-yellow-900 mb-2">How to enable:</h3>
              <ol className="text-sm text-yellow-800 space-y-2">
                <li>1. Click the lock icon in your browser's address bar</li>
                <li>2. Find "Microphone" in the permissions list</li>
                <li>3. Change the setting to "Allow"</li>
                <li>4. Refresh this page</li>
              </ol>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => window.location.reload()}
                className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
              >
                Refresh Page
              </button>
              <button
                onClick={() => setIsVisible(false)}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-lg transition-colors"
              >
                Use Text Input
              </button>
            </div>
          </>
        )}

        {permissionState === 'checking' && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        )}
      </div>
    </div>
  );
}
