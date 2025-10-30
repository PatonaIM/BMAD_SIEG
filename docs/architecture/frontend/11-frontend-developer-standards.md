# 11. Frontend Developer Standards

## 11.1 Critical Coding Rules

1. **Always use TypeScript** - No `any` types without explicit justification
2. **Component naming** - Use PascalCase for components, files match component names
3. **Imports** - Use `@/` alias for absolute imports, avoid relative paths beyond parent
4. **Props** - Destructure in function signature, prefix booleans with `is/has/should`
5. **State** - Use Zustand for shared state, useState for local UI state
6. **Effects** - Clean up side effects, include all dependencies in useEffect
7. **Error handling** - Always wrap async operations in try-catch
8. **Accessibility** - Include proper ARIA labels, ensure keyboard navigation
9. **Testing** - Write tests alongside components, test user behavior not implementation
10. **MUI theming** - Use theme values via `sx` prop or `styled`, never hardcode colors

## 11.2 Quick Reference

**Start Development:**
```bash
npm run dev
```

**Run Tests:**
```bash
npm run test
npm run test:ui        # UI mode
npm run test:coverage  # With coverage
```

**Build:**
```bash
npm run build
npm run preview  # Preview production build
```

**Linting:**
```bash
npm run lint
npm run lint:fix
```

**Type Checking:**
```bash
npm run type-check
```

## 11.3 Common Patterns

**Fetching Data:**
```typescript
// Using TanStack Query hooks
const { data, isLoading, error } = useInterviews();

// With parameters
const { data: interview } = useInterview(interviewId);

// Mutations
const { mutate, isPending } = useStartInterview();
mutate(interviewId);
```

**Form Handling:**
```typescript
const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});
```

**Navigation:**
```typescript
const navigate = useNavigate();
navigate(ROUTES.CANDIDATE.DASHBOARD);
```

**Global State:**
```typescript
const user = useGlobalStore(selectUser);
const { setUser, logout } = useGlobalStore();
```

**Query Invalidation:**
```typescript
const queryClient = useQueryClient();
queryClient.invalidateQueries({ queryKey: interviewKeys.lists() });
```

---
