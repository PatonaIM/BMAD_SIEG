# AI Prompts Documentation

This directory contains carefully crafted prompts for AI-assisted UI development using tools like Vercel v0, Lovable, and similar platforms.

## 📁 Files in This Directory

### `v0-ui-generation-guide.md`
**Comprehensive guide for generating Teamified UI with v0**

Contains:
- ✅ Phase 1: Design System Foundation prompt
- ✅ Phase 2: Pre-Interview System Check prompt
- ✅ Complete workflow from prompt to production
- ✅ Testing checklists
- ✅ Troubleshooting guide
- ✅ Integration instructions

**Use this file when:**
- Starting UI development with v0
- Need to understand the complete workflow
- Want to see detailed prompt structure
- Looking for testing and deployment guidance

---

## 🚀 Quick Start

1. **Read the full guide:** `v0-ui-generation-guide.md`
2. **Copy Phase 1 prompt** → Paste into v0.dev
3. **Generate design system components** → Test and export
4. **Copy Phase 2 prompt** → Paste into v0.dev (new session)
5. **Generate Pre-Interview Check screen** → Integrate and test

---

## 🎯 Prompt Strategy

We use a **Hybrid Approach**:
- **Phase 1:** Build reusable design system (foundation)
- **Phase 2+:** Build screens using design system components

**Why this works:**
- Ensures consistency across all screens
- Faster iteration after foundation is built
- Easier to maintain and update
- Production-ready code quality

---

## 📝 Creating New Prompts

When creating prompts for additional screens, follow this structure:

### 1. High-Level Goal
Clear, concise summary of what you're building.

### 2. Step-by-Step Instructions
Granular, numbered actions the AI should take.

### 3. Code Examples & Constraints
Exact specifications, data structures, API contracts.

### 4. Strict Scope
Define boundaries - what to do AND what NOT to do.

**Template:**
```markdown
# [SCREEN/COMPONENT NAME]

## PROJECT CONTEXT
[Background, tech stack, user context]

## STEP-BY-STEP INSTRUCTIONS
1. [Specific action]
2. [Specific action]
...

## CODE EXAMPLES & CONSTRAINTS
[Sample code, data structures, specifications]

## STRICT SCOPE
**YOU SHOULD:** [List of allowed actions]
**YOU SHOULD NOT:** [List of restricted actions]

## DELIVERABLES
[List of expected files/outputs]
```

---

## 🔄 Maintenance

**Update prompts when:**
- Design system specifications change
- New component patterns emerge
- Technology stack updates
- Accessibility requirements evolve

**Version control:**
- Keep prompts in git
- Document changes in commit messages
- Tag major versions
- Archive old prompts in `archive/` subdirectory

---

## 🆘 Getting Help

**If prompts don't generate expected results:**
1. Review the troubleshooting section in main guide
2. Be more explicit with specifications
3. Provide exact pixel values and colors
4. Reference specific framework patterns
5. Iterate with v0 using specific feedback

**Common fixes:**
- "Make the button exactly 44px height"
- "Use MUI's Box component with sx prop for layout"
- "Add proper TypeScript interfaces for all props"
- "Include ARIA labels for screen readers"

---

## 📚 Related Documentation

- **Front-End Specification:** `docs/front-end-spec.md`
- **Architecture Document:** `docs/architecture.md` (when created)
- **PRD:** `docs/prd.md`
- **Coding Standards:** `docs/architecture/coding-standards.md`

---

**Last Updated:** October 28, 2025  
**Maintained By:** UX Expert (Sally)
