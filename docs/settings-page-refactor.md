# Settings Page Refactor - November 10, 2025

## Changes Made

Refactored the settings page to clearly distinguish between working features and planned features.

### ✅ Working Features (Kept)

1. **Appearance Section**
   - Theme toggle (Light/Dark/System) - Fully functional
   - Uses `next-themes` library
   - Persisted across sessions
   - Fixed hydration issue with mounted state

### 🔮 Coming Soon Features (Stubbed)

All non-functional features now display with:
- "Coming Soon" badge
- Reduced opacity (60%)
- Brief description of planned functionality
- No interactive elements to avoid confusion

**Sections marked as Coming Soon:**

1. **Account Information**
   - Full name, phone, experience updates
   - Will connect to existing `/api/v1/profile/basic-info` endpoint

2. **Password & Security**
   - Change password functionality
   - Two-factor authentication
   - Requires new `/api/v1/auth/change-password` endpoint

3. **Notifications**
   - Email notifications toggle
   - Job match alerts
   - Interview reminders
   - Requires new `notification_preferences` DB field and API

### 🗑️ Removed Features

- **Privacy Settings** - Moved to future roadmap
- **Danger Zone** (Delete Account) - Will be admin-only feature

## Technical Details

**File Modified:**
- `frontend/app/settings/page.tsx`

**Key Changes:**
1. Removed all non-functional form inputs and buttons
2. Added proper theme state management with hydration fix
3. Added "Coming Soon" badges using existing Badge component
4. Reduced visual complexity by removing misleading UI elements

## Next Steps

### Priority 1: Account Information
- Wire up existing profile API
- Add form validation
- Add success/error toasts

### Priority 2: Password Management
- Create `PUT /api/v1/auth/change-password` backend endpoint
- Implement password validation (min 8 chars, complexity rules)
- Add current password verification

### Priority 3: Notifications
- Add `notification_preferences` JSONB field to candidates table
- Create notification preferences API endpoints
- Implement email notification system

### Priority 4: Privacy & Advanced Features
- Profile visibility controls
- Account deletion workflow
- Data export functionality

## Benefits

- **User Clarity**: No confusion about what works vs. what doesn't
- **Better UX**: No broken buttons or misleading forms
- **Clean Code**: Removed unused state management
- **Future Ready**: Easy to enable sections as features are built
