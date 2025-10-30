import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

/**
 * MSW Browser Worker
 * Used for mocking API in development environment
 */
export const worker = setupWorker(...handlers);
