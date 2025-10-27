# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a repository template for Teamified projects featuring a full-stack architecture with NestJS backend and React frontend using Material-UI 3 Expressive Design system.

## Architecture & Code Organization

### Backend (NestJS)
- **Module Structure**: Organized by feature with entities, services, controllers, DTOs, and tests
- **File Naming**: kebab-case with descriptive suffixes (e.g., `feature.entity.ts`, `feature.service.ts`)
- **Database**: TypeORM entities with UUID primary keys, snake_case column names
- **Authentication**: JWT-based with role-based access control
- **API**: RESTful endpoints at `/api/v1/` prefix

### Frontend (React + TypeScript)
- **Component Structure**: Functional components with TypeScript interfaces
- **State Management**: Local state with useState, form handling patterns
- **UI Framework**: Material-UI 3 with custom expressive design theme
- **File Organization**: Components in dedicated folders with index.ts exports

## Design System

### Material-UI 3 Expressive Design
- **Colors**: Primary `#A16AE8` (purple), Secondary `#8096FD` (blue)
- **Typography**: Plus Jakarta Sans font family with expressive scale
- **Spacing**: 8px base unit system
- **Components**: 16px+ border radius, generous spacing, smooth animations
- **Layout**: LayoutMUI wrapper with SidebarMUI navigation

### Key Design Patterns
- **Buttons**: Rounded corners (16px), gradient backgrounds, hover effects
- **Cards**: 20px border radius, subtle shadows with hover elevation
- **Forms**: Always-visible patterns with 16px field spacing
- **Typography**: Semantic hierarchy with h3 page titles, h6 section headers

## Code Standards

### Backend Standards
- **Entities**: TypeORM decorators, validation with class-validator
- **Services**: Injectable with Repository pattern, proper error handling
- **Controllers**: Route prefix `/api/v1/`, ValidationPipe with whitelist
- **DTOs**: Request/response DTOs with ApiProperty decorators
- **Testing**: Jest with mock repositories and comprehensive test coverage

### Frontend Standards  
- **Components**: TypeScript interfaces, proper prop typing
- **Forms**: Controlled components with validation patterns
- **Styling**: Material-UI sx prop with theme integration
- **Testing**: Vitest with React Testing Library
- **Error Handling**: Try-catch with user-friendly error messages

### File Structure Examples
```
Backend:
src/{feature}/
├── entities/{feature}.entity.ts
├── services/{feature}.service.ts  
├── controllers/{feature}.controller.ts
├── dto/{feature}.dto.ts
└── {feature}.module.ts

Frontend:
src/components/{ComponentName}/
├── index.ts
├── {ComponentName}.tsx
├── {ComponentName}.test.tsx
└── {ComponentName}.module.css
```

## Quality Standards

- **TypeScript**: Strict mode enabled, no implicit any
- **Testing**: Unit tests for services/components, integration tests for controllers
- **Performance**: Database indexing, React.memo for expensive components
- **Security**: Input validation, JWT validation, XSS/SQL injection prevention
- **Accessibility**: WCAG 2.1 AA compliance, proper ARIA labels, keyboard navigation

## Documentation References

- **Coding Standards**: `docs/architecture/coding-standards.md`
- **Style Guide**: `docs/style-guide/material-ui-expressive-design.md`
- **Quick Reference**: `docs/style-guide/style-guide-quick-reference.md`

## Key Implementation Notes

- All components must use ThemeProvider with muiTheme
- Follow 8px spacing system consistently
- Implement proper TypeScript interfaces for all props and data
- Use semantic HTML and maintain accessibility standards
- Database tables use snake_case, TypeScript uses camelCase
- API endpoints follow RESTful conventions with proper HTTP status codes
- Always implement both happy path and error handling scenarios