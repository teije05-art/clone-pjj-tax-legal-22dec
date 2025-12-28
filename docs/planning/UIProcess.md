# KPMG Professional UI Styling Plan

## Overview

Transform the Reflex tax workflow app into a professional KPMG-branded SaaS dashboard with modern styling, glassmorphism effects, and the 60-30-10 color rule.

---

## Color Palette (from KPMG brand image)

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary Navy | Deep Blue | `#191E62` | Headers, text, icons |
| KPMG Blue | Action Blue | `#00338D` | Secondary accents, gradients |
| Electric Pink | CTA Accent | `#E6007E` | Primary buttons, active states |
| Tech Purple | Accent | `#6D2077` | Gradients, badges |
| Background | Slate-50 | `#F8FAFC` | Page backgrounds |
| Success | Emerald | `#10B981` | Completed states |

---

## Implementation Phases

### Phase 1: Foundation Setup

**Files to create/modify:**

1. **Create** `assets/styles/kpmg-theme.css`
   - CSS custom properties for all brand colors
   - Glassmorphism utilities (.glass-card)
   - Gradient definitions
   - Typography classes
   - Animation keyframes (fade-in, hover-lift, speed-lines)
   - Import Google Fonts (Inter, Plus Jakarta Sans)

2. **Modify** `.web/tailwind.config.js`
   - Add KPMG color palette under `theme.extend.colors.kpmg`
   - Custom shadows (glass, card, card-hover)
   - Custom gradients (gradient-kpmg, gradient-header)
   - Font families (sans: Inter, heading: Plus Jakarta Sans)

3. **Modify** `reflex_app/reflex_app.py`
   - Add stylesheet import: `/styles/kpmg-theme.css`
   - Add Google Fonts import
   - Keep existing rx.theme() for Radix compatibility

### Phase 2: Reusable Components

**Create** `reflex_app/components/ui.py` with:

- `step_container()` - Glassmorphism card wrapper for all steps
- `step_header()` - Icon + title + description pattern
- `kpmg_button()` - Branded button variants (primary, secondary, outline, ghost)
- `info_callout()` - Blue-tinted info box
- `warning_callout()` - Amber warning box
- `error_callout()` - Red error box
- `content_card()` - Subtle accent-bordered cards

### Phase 3: Header Redesign

**Modify** `reflex_app/components/header.py`

Design:
- Navy-to-blue gradient background (`from-kpmg-navy via-kpmg-blue to-kpmg-navy`)
- Mesh gradient overlay (subtle pink/purple radial gradients at 15% opacity)
- KPMG logo in white (via brightness-0 invert filter)
- Glassmorphism container around logo/title (`bg-white/10 backdrop-blur-md`)
- Pink badge for current step indicator
- White/transparent styling for all text

### Phase 4: Progress Bar Redesign

**Modify** `reflex_app/components/progress.py`

Design:
- Completed steps: Emerald circle with white checkmark
- Current step: Pink-to-purple gradient with ring effect
- Future steps: Slate outline with gray number
- Connecting lines that fill emerald when step completed
- Clean white background with subtle shadow

### Phase 5: Step Components

**Modify** `step_1.py` through `step_6.py`

Pattern for each step:
- Wrap content in `step_container()` for glassmorphism card
- Use `step_header()` with navy gradient icon box
- Use `info_callout()` for user instructions
- Style inputs with `border-2 border-slate-200 focus:border-kpmg-blue focus:ring-4`
- Use `kpmg_button()` variants for actions
- Primary CTA: Pink-purple gradient
- Back buttons: Outline variant

### Phase 6: Main Layout

**Modify** `reflex_app/reflex_app.py` index()

- Background: Gradient from slate-50 to white
- Footer: Clean with pink "AI" badge accent
- Proper spacing and max-width containers

---

## 60-30-10 Rule Application

- **60% White/Neutral**: Page backgrounds, card backgrounds, body text
- **30% Navy/Blue**: Header gradient, step icons, headings, borders
- **10% Pink/Purple**: Primary buttons, active step badge, accents

---

## File Modification Summary

| File | Action | Priority |
|------|--------|----------|
| `assets/styles/kpmg-theme.css` | Create | High |
| `.web/tailwind.config.js` | Modify | High |
| `reflex_app/reflex_app.py` | Modify | High |
| `components/ui.py` | Create | High |
| `components/header.py` | Modify | High |
| `components/progress.py` | Modify | High |
| `components/step_1.py` | Modify | Medium |
| `components/step_2.py` | Modify | Medium |
| `components/step_3.py` | Modify | Medium |
| `components/step_4.py` | Modify | Medium |
| `components/step_5.py` | Modify | Medium |
| `components/step_6.py` | Modify | Medium |

---

## Key Visual Elements

1. **Glassmorphism**: `bg-white/80 backdrop-blur-md border border-white/30`
2. **Gradient buttons**: `bg-gradient-to-r from-kpmg-pink to-kpmg-purple`
3. **Navy icon boxes**: `bg-gradient-to-br from-kpmg-navy to-kpmg-blue rounded-xl`
4. **Focus states**: `focus:ring-4 focus:ring-kpmg-blue/20`
5. **Hover lift**: `hover:transform hover:-translate-y-0.5 hover:shadow-lg`
6. **Speed aesthetic**: Subtle mesh gradient overlay in header

---

## Typography

| Element | Font | Weight | Class |
|---------|------|--------|-------|
| Page/Step titles | Plus Jakarta Sans | Bold | `font-heading text-2xl font-bold` |
| Body text | Inter | Regular | `text-slate-600` |
| Captions | Inter | Regular | `text-sm text-slate-500` |
| Buttons | Inter | Medium | `font-medium` |

---

## Implementation Order

1. Create CSS file with variables and utilities
2. Update Tailwind config with color palette
3. Update main app with stylesheet imports
4. Create ui.py with reusable components
5. Redesign header with gradient
6. Redesign progress bar
7. Update step_1.py as reference implementation
8. Apply pattern to steps 2-6
