import { http, HttpResponse, delay } from 'msw';

/**
 * MSW Request Handlers
 * Mock API responses for development and testing
 */
export const handlers = [
  // Mock login endpoint
  http.post('http://localhost:8000/api/v1/auth/login', async ({ request }) => {
    await delay(500);
    const body = await request.json() as { email: string; password: string };
    
    return HttpResponse.json({
      token: 'mock-jwt-token-' + Date.now(),
      candidate_id: 'mock-candidate-' + Date.now(),
      email: body.email,
    });
  }),

  // Mock register endpoint
  http.post('http://localhost:8000/api/v1/candidates/register', async ({ request }) => {
    await delay(500);
    const body = await request.json() as { email: string; password: string; full_name: string };
    
    return HttpResponse.json({
      token: 'mock-jwt-token-' + Date.now(),
      candidate_id: 'mock-candidate-' + Date.now(),
      email: body.email,
    });
  }),

  // Mock interview message endpoint
  http.post('http://localhost:8000/api/v1/interviews/:id/messages', async ({ params }) => {
    const { id } = params;
    
    console.log('[MSW] Intercepted interview message for session:', id);
    
    // Simulate AI response delay (1-2 seconds)
    await delay(1000 + Math.random() * 1000);
    
    // Mock AI responses based on message content
    const aiResponses = [
      'Thank you for your response. Let me ask you another question...',
      'That\'s an interesting approach. Can you explain your reasoning?',
      'I see. How would you handle edge cases in this scenario?',
      'Great! Now let\'s move on to a more challenging question.',
      'Can you walk me through your thought process step by step?',
    ];
    
    const randomResponse = aiResponses[Math.floor(Math.random() * aiResponses.length)];
    
    return HttpResponse.json({
      message_id: crypto.randomUUID(),
      ai_response: randomResponse,
      question_number: Math.floor(Math.random() * 8) + 2, // Random between 2-9
      total_questions: 10,
    });
  }),
];
