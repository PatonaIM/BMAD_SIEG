# Create Commit Message

Create a standardized commit message following Conventional Commits specification and 50/72 rule.

## Purpose

Generate properly formatted commit messages that follow project standards for consistency, automation, and readability.

## Standards Reference

All commit messages must follow the standards defined in `docs/architecture/coding-standards.md`:

### Format Structure
\`\`\`
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
\`\`\`

### Character Limits (50/72 Rule)
- **Subject line**: 50 characters maximum (including type and scope)
- **Body lines**: 72 characters maximum per line

### Required Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code restructuring (no functional changes)
- `test`: Adding/fixing tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `build`: Build system changes
- `revert`: Revert previous commit

### Common Scopes
- `(api)`: Backend API changes
- `(ui)`: Frontend/UI changes
- `(auth)`: Authentication related
- `(db)`: Database changes
- `(config)`: Configuration changes
- `(deps)`: Dependencies

## Usage

This task can be invoked by:
1. **Direct command**: `*commit [description]`
2. **Task execution**: `*task create-commit-message`
3. **Natural request**: "Create a commit message for [description]"

## Process

1. **Gather Context**: Understand what changes were made
2. **Determine Type**: Select appropriate commit type (feat, fix, docs, etc.)
3. **Add Scope**: Include scope if applicable
4. **Write Description**: Clear, imperative mood, under 50 chars
5. **VALIDATE SUBJECT**: Count characters - MUST be ≤50 chars
6. **Add Body**: If needed, explain motivation wrapped at 72 chars
7. **VALIDATE BODY**: Each line MUST be ≤72 chars
8. **Include Footer**: Add breaking changes, issue references if needed
9. **FINAL CHECK**: Verify all validation checklist items

## Character Count Validation

**MANDATORY**: Before presenting any commit message, validate:

\`\`\`
Subject Line Check:
- Count total characters including type, scope, colon, space
- Example: "feat(auth): add reset" = 23 chars ✅
- Example: "feat(standards): add commit message support to all agents" = 55 chars ❌

Body Line Check:
- Each line must be ≤72 characters
- Use line breaks for longer explanations
- Wrap at word boundaries
\`\`\`

**If validation fails**: Revise and recount before presenting to user.

## Examples

### Simple Commit
\`\`\`
feat(auth): add password reset functionality
\`\`\`

### With Body
\`\`\`
fix(api): resolve race condition in user registration

Introduce request ID and reference to latest request to dismiss
incoming responses other than from latest request. This prevents
duplicate user creation when users double-click the register button.

Fixes #234
\`\`\`

### Breaking Change
\`\`\`
feat(api)!: change authentication endpoint

BREAKING CHANGE: /auth/login now requires email instead of username.
Update all client applications to use email field for authentication.

Closes #456
\`\`\`

## Validation Checklist

- ✅ Subject line ≤ 50 characters
- ✅ Body lines ≤ 72 characters
- ✅ Uses imperative mood ("add" not "added")
- ✅ Starts with lowercase (after type/scope)
- ✅ No period at end of subject
- ✅ Appropriate type selected
- ✅ Scope included if applicable
- ✅ Body explains WHY, not HOW
- ✅ References issues if applicable

## Anti-patterns to Avoid

❌ **Don't:**
- Exceed character limits
- Use past tense ("fixed" → "fix")
- Be vague ("Updated stuff")
- Mix multiple unrelated changes

✅ **Do:**
- Be specific and concise
- Use present tense, imperative mood
- Focus on business value
- Reference related issues
