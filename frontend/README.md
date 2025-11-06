# Teamified Frontend - Next.js + TypeScript

Modern job interview platform built with Next.js 16 App Router, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework**: [Next.js 16](https://nextjs.org/) with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4 + shadcn/ui components
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Testing**: Vitest + React Testing Library
- **Forms**: React Hook Form + Zod validation

## Getting Started

### Prerequisites

- Node.js 18+ and pnpm installed

### Installation

```bash
# Install dependencies
pnpm install

# Copy environment variables
cp .env.example .env.local

# Start development server
pnpm dev
```

Visit [http://localhost:3000](http://localhost:3000) to view the application.

## Available Scripts

```bash
pnpm dev          # Start development server
pnpm build        # Build for production
pnpm start        # Start production server
pnpm lint         # Run ESLint
pnpm lint:fix     # Fix ESLint issues
pnpm format       # Format code with Prettier
pnpm test         # Run tests with Vitest
pnpm test:ui      # Run tests with UI
pnpm test:coverage # Generate coverage report
```

## Mock API Mode

This project includes a mock API feature flag that allows you to preview the UI without a working backend.

### Enabling Mock Mode

Set the environment variable in your `.env.local` file:

```env
NEXT_PUBLIC_MOCK_API=true
```

When enabled:
- All API calls return mock data instead of making real network requests
- A visual indicator appears at the top of pages to show mock mode is active
- You can navigate through all pages and see the UI with sample data

### Disabling Mock Mode

To use real API calls, set:

```env
NEXT_PUBLIC_MOCK_API=false
```

Or remove the variable entirely (defaults to `false`).

## Project Structure

```
frontend/
├── app/              # Next.js App Router pages
├── components/       # React components
├── hooks/           # Custom React hooks
├── lib/             # Utilities and helpers
├── styles/          # Global styles
└── tests/           # Test files
```

## Environment Variables

Required environment variables (see `.env.example`):

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_MOCK_API=false
```

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [TanStack Query](https://tanstack.com/query)

## Contributing

Please refer to the [architecture documentation](../docs/architecture/frontend/) for coding standards and best practices.
