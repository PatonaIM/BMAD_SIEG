# Commit Message Template

## Quick Format
```
<type>[scope]: <description>
```

## Character Limits
- **Subject**: 50 characters maximum
- **Body**: 72 characters per line

## Types
- `feat`: New feature
- `fix`: Bug fix  
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding/fixing tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `build`: Build system changes
- `revert`: Revert previous commit

## Common Scopes
- `(api)`: Backend API
- `(ui)`: Frontend/UI
- `(auth)`: Authentication
- `(db)`: Database
- `(config)`: Configuration
- `(deps)`: Dependencies

## Examples

### Simple commits:
```
feat(auth): add password reset feature
fix(api): handle null user response
docs: update README installation steps
refactor(ui): extract reusable form component
test(auth): add login validation tests
chore(deps): update React to v18.2.0
```

### With body (when needed):
```
feat(api): add user profile management endpoints

- Add GET /api/profile endpoint
- Add PUT /api/profile endpoint  
- Implement avatar upload functionality
- Add comprehensive input validation

Closes #234
```

### Breaking changes:
```
feat(auth)!: change login endpoint structure

BREAKING CHANGE: /auth/login now returns user object 
instead of just token. Update client code accordingly.

Fixes #456
```

## Usage Notes
- Use imperative mood ("add" not "added")
- Start description with lowercase
- No period at end of subject
- Separate body with blank line
- Reference issues: "Fixes #123", "Closes #456"
- For breaking changes: use `!` or `BREAKING CHANGE:` footer