import { setupServer } from 'msw/node';
import { handlers } from './handlers';

/**
 * MSW Server
 * Used for mocking API in test environment
 */
export const server = setupServer(...handlers);
