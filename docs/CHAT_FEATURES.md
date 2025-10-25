# Chat Interface - Feature Reference Guide

## Quick Feature Overview

### 🎨 Visual Design
- **Header:** Professional gradient (purple to blue) with glass-morphism effects
- **Status Indicator:** Green pulsing dot when AI provider is connected
- **Message Bubbles:**
  - User messages: Blue, right-aligned
  - AI messages: Gray, left-aligned with provider badge
  - Error messages: Red with warning icon
- **Animations:** Smooth slide-in, fade, pulse (300ms transitions)

### 💬 Chat Features

#### Welcome Screen
```
┌─────────────────────────────────────┐
│  [?] Welcome to AI Assistant        │
│                                      │
│  Ask questions about your Amazon     │
│  affiliate data...                   │
│                                      │
│  Example Questions:                  │
│  ┌──────────────────────────────┐   │
│  │ What are my total earnings   │   │
│  │ this month?                   │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ Show me the top 5 products   │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

#### Message Format
```
User Message:
┌──────────────────────────────────┐
│                     [👤] You     │
│              What are my total   │
│              earnings?           │
│              12:30 PM            │
└──────────────────────────────────┘

AI Response:
┌──────────────────────────────────┐
│ [🤖] Google Gemini Pro           │
│ Based on your data, your total   │
│ earnings are **$1,234.56**       │
│ 12:30 PM                         │
└──────────────────────────────────┘
```

### ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift + Enter` | New line in message |
| `Tab` | Navigate between elements |

### 🔧 Input Controls

#### Textarea Features
- **Auto-resize:** Grows with content (max 120px)
- **Character limit:** 2000 characters
- **Character counter:** Real-time display (e.g., "234/2000")
- **Multi-line support:** Shift+Enter for new lines

#### Send Button States
- **Enabled:** Blue circular button with send icon
- **Disabled:** Gray when input is empty
- **Loading:** Spinning animation while processing
- **Hover:** Scales up 1.05x with shadow

### 📱 Responsive Breakpoints

| Screen Size | Behavior |
|-------------|----------|
| **Desktop (1200px+)** | Full layout, all features visible |
| **Tablet (768-1200px)** | Condensed header, optimized spacing |
| **Mobile (480-768px)** | Simplified header, larger touch targets |
| **Small Mobile (<480px)** | Icon-only buttons, minimal spacing |

### 🎯 Interactive Elements

#### Header Buttons
```
┌──────────────────────────────────────────┐
│ [💬] AI Assistant                        │
│ ● Google Gemini Pro                      │
│                     [🗑️ Clear] [← Dashboard] │
└──────────────────────────────────────────┘
```

#### Example Questions (Clickable)
- Click to auto-fill input
- Auto-sends after click
- Hover effect: Lifts up with blue border

### 🔔 Toast Notifications

#### Success (Green)
```
┌────────────────────────────┐
│ ✓ Chat history cleared     │
└────────────────────────────┘
```

#### Warning (Orange)
```
┌────────────────────────────┐
│ ⚠ No AI provider configured │
└────────────────────────────┘
```

#### Error (Red)
```
┌────────────────────────────┐
│ ✕ Network error occurred    │
└────────────────────────────┘
```

**Toast Behavior:**
- Auto-appear from right
- 5-second auto-dismiss
- Slide-out animation
- Multiple toasts stack vertically

### 💾 Chat History

#### localStorage Structure
```javascript
{
  "chat_history": [
    {
      "type": "user",
      "text": "What are my earnings?",
      "timestamp": "2025-10-25T12:30:00.000Z",
      "provider": null
    },
    {
      "type": "ai",
      "text": "Your total earnings are $1,234.56",
      "timestamp": "2025-10-25T12:30:05.000Z",
      "provider": "Google Gemini Pro"
    }
  ]
}
```

**Features:**
- Persists across page reloads
- Max 50 messages (auto-prune oldest)
- Clear all with confirmation dialog
- Timestamps in ISO format

### 🎭 Typing Indicator

```
[🤖] ● ● ●  (animated bouncing dots)
```

**Animation:**
- 3 dots bounce sequentially
- Staggered delay: 0s, 0.2s, 0.4s
- 1.4s loop animation
- Shows during AI processing

### 🔒 Security Features

#### XSS Protection
```javascript
// User input (escaped)
"<script>alert('xss')</script>"
→ "&lt;script&gt;alert('xss')&lt;/script&gt;"

// AI response (sanitized markdown)
"**Bold** [link](javascript:alert('xss'))"
→ "<strong>Bold</strong> <a>link</a>"  // JS removed
```

#### Input Validation
- Max length: 2000 chars (enforced client-side)
- Empty message rejection
- Duplicate send prevention
- Session expiration redirect

### 📊 Message Rendering

#### Markdown Support
| Markdown | Rendered |
|----------|----------|
| `**bold**` | **bold** |
| `*italic*` | *italic* |
| `` `code` `` | `code` |
| `- list item` | • list item |
| `[link](url)` | link |

#### Code Blocks
```
Input:
```python
print("Hello")
```

Rendered:
┌─────────────────┐
│ print("Hello")  │
└─────────────────┘
```

### 🎨 Color Palette

```css
/* Primary Colors */
--primary-color: #2563eb    /* Blue */
--success-color: #10b981    /* Green */
--warning-color: #f59e0b    /* Amber */
--error-color: #ef4444      /* Red */

/* Neutral Colors */
--bg-primary: #ffffff       /* White */
--bg-secondary: #f8fafc     /* Light Gray */
--text-primary: #0f172a     /* Dark Blue */
--text-secondary: #475569   /* Gray */
```

### 🚀 Performance

| Metric | Target |
|--------|--------|
| Initial Load | < 200ms |
| Message Send | < 500ms (network dependent) |
| Scroll Animation | 100ms smooth |
| localStorage Save | < 10ms |
| Markdown Render | < 50ms |

### 🐛 Error Scenarios

#### Network Error
```
User: [message]
System: [Error bubble]
        ✕ Network error. Please check your connection.
        12:30 PM
Toast: [Red] Network error occurred
```

#### Session Expired
```
Toast: [Error] Session expired. Please log in again.
→ Redirect to /login after 2 seconds
```

#### Provider Offline
```
Header: [Red dot] No provider configured
Toast: [Warning] No AI provider configured
```

### 📏 Spacing System

```css
--spacing-xs: 0.25rem   /* 4px */
--spacing-sm: 0.5rem    /* 8px */
--spacing-md: 1rem      /* 16px */
--spacing-lg: 1.5rem    /* 24px */
--spacing-xl: 2rem      /* 32px */
```

### 🎯 Accessibility Features

- **Keyboard Navigation:** Full tab support
- **Focus Indicators:** 2px blue outline
- **Reduced Motion:** Respects `prefers-reduced-motion`
- **High Contrast:** Enhanced borders in high-contrast mode
- **Screen Readers:** Semantic HTML structure
- **Color Contrast:** WCAG AA compliant

### 💡 User Hints

#### Input Area
```
Press Enter to send, Shift + Enter for new line
```

#### Character Counter
```
0/2000 → 234/2000 → 2000/2000
```

### 🔄 State Management

#### JavaScript State
```javascript
{
  isProcessing: false,        // Currently sending message
  chatHistory: [],            // All messages
  currentProvider: 'gemini',  // Active AI provider
  providerDisplayName: 'Google Gemini Pro'
}
```

### 📐 Layout Structure

```
┌─────────────────────────────────┐
│ Header (Fixed)                  │
├─────────────────────────────────┤
│                                 │
│ Messages (Scrollable)           │
│                                 │
│ • Welcome / Chat bubbles        │
│                                 │
│ [Typing Indicator]              │
├─────────────────────────────────┤
│ Input Area (Fixed)              │
│ [Textarea] 0/2000 [Send]        │
│ Hint: Press Enter to send       │
└─────────────────────────────────┘
```

### 🎬 Animation Timeline

#### Message Send Flow
```
1. User clicks send (0ms)
2. Input disabled (0ms)
3. User message appears (50ms)
4. Input cleared (50ms)
5. Typing indicator shows (100ms)
6. AJAX request sent (100ms)
7. Response received (500ms)
8. Typing indicator hides (500ms)
9. AI message appears (550ms)
10. Scroll to bottom (650ms)
11. Input re-enabled (650ms)
```

### 📱 Mobile Optimizations

- Touch-friendly targets (min 44x44px)
- No hover effects on touch devices
- Full-width on small screens
- Bottom-fixed input area
- Toast notifications full-width
- Simplified header (icon-only buttons)

---

**Quick Start:**
1. Open `/chat` in browser
2. Click an example question OR type your own
3. Press Enter to send
4. View AI response with markdown
5. Continue conversation
6. Clear history anytime with Clear button
7. Return to dashboard with Dashboard button

**Developer Note:** All features are production-ready with comprehensive error handling, security, and accessibility built-in.
