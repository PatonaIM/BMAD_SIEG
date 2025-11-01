"use client"

import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export interface PermissionDeniedHelpProps {
  deviceType: 'microphone' | 'camera';
  onRetry: () => void;
}

/**
 * Component to display browser-specific instructions for enabling permissions
 */
export function PermissionDeniedHelp({ deviceType, onRetry }: PermissionDeniedHelpProps) {
  // Detect browser
  const getBrowserName = (): string => {
    const userAgent = navigator.userAgent.toLowerCase();
    if (userAgent.includes('chrome') && !userAgent.includes('edg')) return 'chrome';
    if (userAgent.includes('firefox')) return 'firefox';
    if (userAgent.includes('safari') && !userAgent.includes('chrome')) return 'safari';
    if (userAgent.includes('edg')) return 'edge';
    return 'unknown';
  };

  const browser = getBrowserName();
  const deviceLabel = deviceType === 'microphone' ? 'Microphone' : 'Camera';

  const getInstructions = (): string[] => {
    switch (browser) {
      case 'chrome':
      case 'edge':
        return [
          `Click the camera/microphone icon in the address bar (next to the URL)`,
          `Select "Always allow ${window.location.hostname} to access your ${deviceType}"`,
          `Click "Done" and refresh the page`,
        ];
      case 'firefox':
        return [
          `Click the permissions icon (shield or padlock) in the address bar`,
          `Find "${deviceLabel}" in the permissions list`,
          `Change the setting to "Allow"`,
          `Refresh the page`,
        ];
      case 'safari':
        return [
          `Click "Safari" in the menu bar`,
          `Select "Settings for This Website..."`,
          `Find "${deviceLabel}" in the dropdown`,
          `Change the setting to "Allow"`,
          `Refresh the page`,
        ];
      default:
        return [
          `Check your browser settings for site permissions`,
          `Allow access to your ${deviceType} for this website`,
          `Refresh the page`,
        ];
    }
  };

  const instructions = getInstructions();

  return (
    <Card className="p-6 border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/30">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <AlertCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
        </div>
        
        <div className="flex-1 space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-red-900 dark:text-red-100">
              {deviceLabel} Access Denied
            </h3>
            <p className="text-sm text-red-700 dark:text-red-300 mt-1">
              To continue with the interview, you need to enable {deviceType} access.
            </p>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium text-red-900 dark:text-red-100">
              How to enable {deviceType} access:
            </p>
            <ol className="list-decimal list-inside space-y-1.5 text-sm text-red-800 dark:text-red-200">
              {instructions.map((instruction, index) => (
                <li key={index} className="pl-2">
                  {instruction}
                </li>
              ))}
            </ol>
          </div>

          <div className="flex gap-3">
            <Button
              onClick={onRetry}
              variant="default"
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              Retry Access
            </Button>
            <Button
              onClick={() => window.location.reload()}
              variant="outline"
              className="border-red-300 text-red-700 hover:bg-red-100 dark:border-red-800 dark:text-red-300 dark:hover:bg-red-900/30"
            >
              Refresh Page
            </Button>
          </div>

          <p className="text-xs text-red-600 dark:text-red-400">
            <strong>Note:</strong> You cannot proceed with the interview until {deviceType} access is granted.
          </p>
        </div>
      </div>
    </Card>
  );
}
