# Design System — TRUE STAR BD LIMITED

> **Status:** Adopted  
> **Tech Stack:** TailwindCSS · Lucide React · Framer Motion  
> **Last Updated:** 2026-07-02

---

## Table of Contents

1. [Design Tokens](#1-design-tokens)
2. [Component Specifications](#2-component-specifications)
3. [Form Patterns](#3-form-patterns)
4. [Navigation Patterns](#4-navigation-patterns)
5. [Feedback Patterns](#5-feedback-patterns)
6. [Data Visualization](#6-data-visualization)
7. [Dark Mode](#7-dark-mode)
8. [Responsive Adaptation](#8-responsive-adaptation)

---

## 1. Design Tokens

### 1.1 Color Palette

All colours use a 50–950 scale. CSS variables are consumed via Tailwind's `theme.extend.colors` and referenced in components as `var(--color-*)`.

#### Primary — Trust & Action

| Token               | Hex       | CSS Variable              | Usage                               |
|---------------------|-----------|---------------------------|--------------------------------------|
| primary-50          | `#EFF6FF` | `--color-primary-50`      | Background tint, tags                |
| primary-100         | `#DBEAFE` | `--color-primary-100`     | Light background, hover states       |
| primary-200         | `#BFDBFE` | `--color-primary-200`     | Badge backgrounds                    |
| primary-300         | `#93C5FD` | `--color-primary-300`     | Border light                         |
| primary-400         | `#60A5FA` | `--color-primary-400`     | Border, pressed state                |
| primary-500         | `#3B82F6` | `--color-primary-500`     | Primary buttons, links               |
| primary-600         | `#2563EB` | `--color-primary-600`     | Button hover, active links           |
| primary-700         | `#1D4ED8` | `--color-primary-700`     | Active state, pressed buttons        |
| primary-800         | `#1E40AF` | `--color-primary-800`     | Text on light backgrounds            |
| primary-900         | `#1E3A8A` | `--color-primary-900`     | High-contrast text                   |
| primary-950         | `#1E3A5F` | `--color-primary-950`     | Dark mode surfaces                   |

#### Slate — UI Surfaces

| Token             | Hex       | CSS Variable            | Usage                              |
|-------------------|-----------|-------------------------|-------------------------------------|
| slate-50          | `#F8FAFC` | `--color-slate-50`      | Page background                     |
| slate-100         | `#F1F5F9` | `--color-slate-100`     | Card background                     |
| slate-200         | `#E2E8F0` | `--color-slate-200`     | Dividers, borders                   |
| slate-300         | `#CBD5E1` | `--color-slate-300`     | Input borders                       |
| slate-400         | `#94A3B8` | `--color-slate-400`     | Disabled text                       |
| slate-500         | `#64748B` | `--color-slate-500`     | Muted text                          |
| slate-600         | `#475569` | `--color-slate-600`     | Secondary text                      |
| slate-700         | `#334155` | `--color-slate-700`     | Body text                           |
| slate-800         | `#1E293B` | `--color-slate-800`     | Heading text                        |
| slate-900         | `#0F172A` | `--color-slate-900`     | High-emphasis text                  |
| slate-950         | `#020617` | `--color-slate-950`     | Near-black, code headers            |

#### Success — Green

| Token   | Hex       | CSS Variable          | Usage                          |
|---------|-----------|-----------------------|--------------------------------|
| 50      | `#F0FDF4` | `--color-success-50`  | Background tint                |
| 100     | `#DCFCE7` | `--color-success-100` | Light background               |
| 200     | `#BBF7D0` | `--color-success-200` | Badge background               |
| 300     | `#86EFAC` | `--color-success-300` | Border                         |
| 400     | `#4ADE80` | `--color-success-400` | Icon                           |
| 500     | `#22C55E` | `--color-success-500` | Primary green                  |
| 600     | `#16A34A` | `--color-success-600` | Hover                          |
| 700     | `#15803D` | `--color-success-700` | Active                         |
| 800     | `#166534` | `--color-success-800` | Text on light                  |
| 900     | `#14532D` | `--color-success-900` | Text                           |
| 950     | `#052E16` | `--color-success-950` | Dark mode                      |

#### Warning — Amber

| Token   | Hex       | CSS Variable          | Usage                          |
|---------|-----------|-----------------------|--------------------------------|
| 50      | `#FFFBEB` | `--color-warning-50`  | Background tint                |
| 100     | `#FEF3C7` | `--color-warning-100` | Light background               |
| 200     | `#FDE68A` | `--color-warning-200` | Badge background               |
| 300     | `#FCD34D` | `--color-warning-300` | Border                         |
| 400     | `#FBBF24` | `--color-warning-400` | Icon                           |
| 500     | `#F59E0B` | `--color-warning-500` | Primary amber                  |
| 600     | `#D97706` | `--color-warning-600` | Hover                          |
| 700     | `#B45309` | `--color-warning-700` | Active                         |
| 800     | `#92400E` | `--color-warning-800` | Text on light                  |
| 900     | `#78350F` | `--color-warning-900` | Text                           |
| 950     | `#451A03` | `--color-warning-950` | Dark mode                      |

#### Error — Red

| Token   | Hex       | CSS Variable        | Usage                          |
|---------|-----------|---------------------|--------------------------------|
| 50      | `#FEF2F2` | `--color-error-50`  | Background tint                |
| 100     | `#FEE2E2` | `--color-error-100` | Light background               |
| 200     | `#FECACA` | `--color-error-200` | Badge background               |
| 300     | `#FCA5A5` | `--color-error-300` | Border                         |
| 400     | `#F87171` | `--color-error-400` | Icon                           |
| 500     | `#EF4444` | `--color-error-500` | Primary red                    |
| 600     | `#DC2626` | `--color-error-600` | Hover                          |
| 700     | `#B91C1C` | `--color-error-700` | Active                         |
| 800     | `#991B1B` | `--color-error-800` | Text on light                  |
| 900     | `#7F1D1D` | `--color-error-900` | Text                           |
| 950     | `#450A0A` | `--color-error-950` | Dark mode                      |

#### Info — Cyan

| Token   | Hex       | CSS Variable       | Usage                          |
|---------|-----------|--------------------|--------------------------------|
| 50      | `#ECFEFF` | `--color-info-50`  | Background tint                |
| 100     | `#CFFAFE` | `--color-info-100` | Light background               |
| 200     | `#A5F3FC` | `--color-info-200` | Badge background               |
| 300     | `#67E8F9` | `--color-info-300` | Border                         |
| 400     | `#22D3EE` | `--color-info-400` | Icon                           |
| 500     | `#06B6D4` | `--color-info-500` | Primary cyan                   |
| 600     | `#0891B2` | `--color-info-600` | Hover                          |
| 700     | `#0E7490` | `--color-info-700` | Active                         |
| 800     | `#155E75` | `--color-info-800` | Text on light                  |
| 900     | `#164E63` | `--color-info-900` | Text                           |
| 950     | `#083344` | `--color-info-950` | Dark mode                      |

#### Neutral — Gray

| Token   | Hex       | CSS Variable          | Usage                              |
|---------|-----------|-----------------------|------------------------------------|
| 50      | `#F9FAFB` | `--color-neutral-50`  | Lightest background                |
| 100     | `#F3F4F6` | `--color-neutral-100` | Card background                    |
| 200     | `#E5E7EB` | `--color-neutral-200` | Borders                            |
| 300     | `#D1D5DB` | `--color-neutral-300` | Input borders                      |
| 400     | `#9CA3AF` | `--color-neutral-400` | Disabled text                      |
| 500     | `#6B7280` | `--color-neutral-500` | Muted text                         |
| 600     | `#4B5563` | `--color-neutral-600` | Secondary text                     |
| 700     | `#374151` | `--color-neutral-700` | Body text                          |
| 800     | `#1F2937` | `--color-neutral-800` | Heading text                       |
| 900     | `#111827` | `--color-neutral-900` | High-emphasis text                 |
| 950     | `#030712` | `--color-neutral-950` | Near-black                         |

---

### 1.2 Typography

#### Font Family

| Usage     | Stack                                           | Tailwind Key  |
|-----------|-------------------------------------------------|---------------|
| Headings  | `'Inter', system-ui, -apple-system, sans-serif` | `font-heading`|
| Body      | `system-ui, -apple-system, sans-serif`          | `font-body`   |
| Mono      | `'JetBrains Mono', 'Fira Code', monospace`     | `font-mono`   |

#### Font Scale

| Name     | Size  | Line Height | Letter Spacing | Tailwind      | Usage                      |
|----------|-------|-------------|----------------|---------------|----------------------------|
| xs       | 12px  | 1.5 (16px)  | 0.02em         | `text-xs`     | Caption, helper text       |
| sm       | 14px  | 1.5 (20px)  | 0.01em         | `text-sm`     | Small UI labels, metadata  |
| base     | 16px  | 1.5 (24px)  | 0              | `text-base`   | Body text                  |
| lg       | 18px  | 1.5 (28px)  | 0              | `text-lg`     | Larger body, card titles   |
| xl       | 20px  | 1.4 (28px)  | -0.01em        | `text-xl`     | Section headings           |
| 2xl      | 24px  | 1.35 (32px) | -0.01em        | `text-2xl`    | Sub-page headings          |
| 3xl      | 30px  | 1.3 (39px)  | -0.015em       | `text-3xl`    | Page headings              |
| 4xl      | 36px  | 1.25 (45px) | -0.02em        | `text-4xl`    | Major section headings     |
| 5xl      | 48px  | 1.2 (58px)  | -0.025em       | `text-5xl`    | Hero headings              |
| 6xl      | 60px  | 1.15 (69px) | -0.03em        | `text-6xl`    | Landing page hero          |

#### Font Weights

| Weight   | Value | Tailwind      | Usage                          |
|----------|-------|---------------|--------------------------------|
| Light    | 300   | `font-light`  | Large hero text                |
| Normal   | 400   | `font-normal` | Body text                      |
| Medium   | 500   | `font-medium` | Labels, button text            |
| Semibold | 600   | `font-semibold`| Subheadings, active nav        |
| Bold     | 700   | `font-bold`   | Main headings, emphasis        |

#### Usage Guidelines

- **Headings (h1–h6):** Use `font-heading` with semibold or bold. Maintain a clear hierarchy — never skip levels.
- **Body:** Use `font-body` with normal weight at `text-base` (16px) for readability.
- **Labels & Buttons:** Medium weight, `text-sm` (14px) or `text-base` (16px), uppercase or sentence case depending on context.
- **Captions:** `text-xs` (12px), normal weight, neutral-500 colour.
- **Code:** `font-mono` at `text-sm` or `text-base`.
- Line length for body text should not exceed 75 characters per line.

---

### 1.3 Spacing

Base unit: **4 px**. All spacing derives from a 4 px grid.

| Token    | Pixels | Tailwind  | Usage                          |
|----------|--------|-----------|--------------------------------|
| space-0  | 0 px   | `p-0`     | No spacing                     |
| space-1  | 4 px   | `p-1`     | Compact inner padding          |
| space-2  | 8 px   | `p-2`     | Tight padding, icon gaps       |
| space-3  | 12 px  | `p-3`     | Input padding, small gaps      |
| space-4  | 16 px  | `p-4`     | Standard card padding          |
| space-5  | 20 px  | `p-5`     | Generous card padding          |
| space-6  | 24 px  | `p-6`     | Section padding                |
| space-8  | 32 px  | `p-8`     | Modal padding, large sections  |
| space-10 | 40 px  | `p-10`    | Page section vertical spacing  |
| space-12 | 48 px  | `p-12`    | Hero sections                  |
| space-16 | 64 px  | `p-16`    | Large page sections            |
| space-20 | 80 px  | `p-20`    | Major layout gaps              |
| space-24 | 96 px  | `p-24`    | Page-level grouping            |

#### Padding & Margin Guidelines

- **Cards:** `p-4` (default), `p-6` (featured).
- **Form fields:** `px-3 py-2` (md), `px-3 py-1.5` (sm), `px-4 py-3` (lg).
- **Page sections:** `py-12` or `py-16` vertical, `px-4` or `px-6` horizontal.
- **Modal content:** `p-6`.
- **Button padding:** Use `px-4 py-2` (md), proportional scaling for other sizes.
- **List items:** `px-4 py-3` for standard density, `px-4 py-2` for compact.

---

### 1.4 Shadows

| Level | CSS Value                                             | Tailwind      | Usage                    |
|-------|-------------------------------------------------------|---------------|--------------------------|
| sm    | `0 1px 2px 0 rgb(0 0 0 / 0.05)`                      | `shadow-sm`   | Buttons, small cards     |
| md    | `0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)` | `shadow-md`   | Cards, dropdowns |
| lg    | `0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)` | `shadow-lg`   | Dropdowns, popovers |
| xl    | `0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)` | `shadow-xl`   | Modals, sidebars |
| 2xl   | `0 25px 50px -12px rgb(0 0 0 / 0.25)`                | `shadow-2xl`  | Full-screen modals       |
| inner | `inset 0 2px 4px 0 rgb(0 0 0 / 0.05)`               | `shadow-inner`| Pressed states, inputs   |
| none  | `0 0 #0000`                                          | `shadow-none` | Flat surfaces            |

- **Dark mode:** Shadow opacity reduced by 50% — use coloured shadows (e.g. `rgb(0 0 0 / 0.25)` → `0.125`) or `shadow-lg` with `ring-1 ring-white/10` for depth.

---

### 1.5 Border Radius

| Token    | Value    | Tailwind         | Usage                                    |
|----------|----------|------------------|------------------------------------------|
| none     | 0 px     | `rounded-none`   | Tables, list groups                      |
| sm       | 2 px     | `rounded-sm`     | Inputs, small buttons                    |
| md       | 4 px     | `rounded-md`     | Default buttons, cards, selects          |
| lg       | 8 px     | `rounded-lg`     | Large cards, modals                      |
| xl       | 12 px    | `rounded-xl`     | Featured cards, dialogs                  |
| 2xl      | 16 px    | `rounded-2xl`    | Side panels, sheets                      |
| full     | 9999 px  | `rounded-full`   | Badges, avatars, pills, toggle switches  |

---

### 1.6 Breakpoints

| Name | Width     | Tailwind  | Content                                                |
|------|-----------|-----------|--------------------------------------------------------|
| xs   | 0–639 px  | `max-sm:` | Mobile portrait, single column                         |
| sm   | ≥640 px   | `sm:`     | Mobile landscape, two-column grids appear              |
| md   | ≥768 px   | `md:`     | Tablets, sidebar collapses to drawer                   |
| lg   | ≥1024 px  | `lg:`     | Desktop, full sidebar, multi-column layouts            |
| xl   | ≥1280 px  | `xl:`     | Large desktop, max content width                       |
| 2xl  | ≥1536 px  | `2xl:`    | Extra-wide, ultrawide monitors                         |

**Approach:** Mobile-first. Base styles target mobile (xs). Progressive enhancement via `sm:`, `md:`, `lg:`, `xl:`, `2xl:` breakpoints.

---

### 1.7 Z-Index Scale

| Layer       | Value  | CSS Variable          | Elements                           |
|-------------|--------|-----------------------|------------------------------------|
| base        | 0      | `--z-base`            | Page content                       |
| dropdown    | 50     | `--z-dropdown`        | Dropdown menus, popovers           |
| sticky      | 100    | `--z-sticky`          | Sticky headers, table headers      |
| navbar      | 200    | `--z-navbar`          | Top navigation bar, sidebars       |
| backdrop    | 250    | `--z-backdrop`        | Modal/overlay backdrops            |
| modal       | 300    | `--z-modal`           | Modal dialogs, side panels         |
| toast       | 400    | `--z-toast`           | Toast notifications, alerts        |
| tooltip     | 500    | `--z-tooltip`         | Tooltips, floating labels          |

---

## 2. Component Specifications

### 2.1 Button

#### Variants

| Variant   | Background          | Text         | Border           | Hover BG           | Active BG          |
|-----------|---------------------|--------------|------------------|--------------------|--------------------|
| primary   | primary-500         | white        | transparent      | primary-600        | primary-700        |
| secondary | slate-100           | slate-800    | transparent      | slate-200          | slate-300          |
| outline   | transparent         | primary-500  | primary-500      | primary-50         | primary-100        |
| ghost     | transparent         | slate-700    | transparent      | slate-100          | slate-200          |
| danger    | error-500           | white        | transparent      | error-600          | error-700          |
| link      | transparent         | primary-500  | transparent      | underline          | primary-600        |

#### Sizes

| Size | Height | Padding           | Font       | Icon Size |
|------|--------|-------------------|------------|-----------|
| xs   | 28 px  | `px-2 py-1`       | `text-xs`  | 14 px     |
| sm   | 32 px  | `px-3 py-1.5`     | `text-sm`  | 16 px     |
| md   | 40 px  | `px-4 py-2`       | `text-sm`  | 18 px     |
| lg   | 48 px  | `px-6 py-2.5`     | `text-base`| 20 px     |
| xl   | 56 px  | `px-8 py-3`       | `text-base`| 22 px     |

#### States

- **Default:** As defined per variant.
- **Hover:** Background shift 100–200 levels darker (or lighter for dark mode). Cursor pointer.
- **Active:** Scale transform `scale(0.97)` with Framer Motion `whileTap`. Background 200–300 levels darker.
- **Disabled:** `opacity-50`, `cursor-not-allowed`, no hover effects.
- **Loading:** Show a `<Loader2>` spinner (Lucide) replacing or alongside text. Disable interaction. Framer Motion `animate={{ rotate: 360 }}` for continuous spin.

#### With Icon

- **Icon only:** Use `aria-label` for accessibility. Square padding to match height.
- **Icon + text:** Icon left-aligned, `gap-2` spacing. Right icon for dropdown arrows.

#### Full Width

- Apply `w-full` class. Use when button should fill parent container (forms, mobile CTAs).

---

### 2.2 Input

#### Types

`text`, `email`, `password`, `search`, `number`, `tel`, `url` — mapped via the native `type` attribute.

#### Sizes

| Size | Height | Padding       | Font       |
|------|--------|---------------|------------|
| sm   | 32 px  | `px-3 py-1.5` | `text-sm`  |
| md   | 40 px  | `px-3 py-2`   | `text-sm`  |
| lg   | 48 px  | `px-4 py-3`   | `text-base`|

#### States

| State     | Border        | Background     | Text        |
|-----------|---------------|----------------|-------------|
| default   | slate-300     | white          | slate-900   |
| focus     | primary-500   | white          | slate-900   |
| error     | error-500     | error-50       | slate-900   |
| disabled  | slate-200     | slate-100      | slate-400   |
| readonly  | slate-200     | slate-50       | slate-700   |

- **Focus:** `ring-2 ring-primary-500/20` outline offset.
- **Transition:** All state changes animate at `duration-150 ease-in-out`.

#### With Icon

- **Left icon:** Absolute-positioned icon 12 px from left edge. Input receives `pl-10` padding.
- **Right icon:** Absolute-positioned icon 12 px from right edge. Input receives `pr-10` padding. Clickable (e.g. search clear, password toggle).

#### Supporting Elements

- **Label:** `text-sm font-medium text-slate-700 mb-1` (stacked above).
- **Helper text:** `text-xs text-slate-500 mt-1` below input.
- **Error message:** `text-xs text-error-500 mt-1` below input, accompanied by error state border.
- **Character count:** `text-xs text-slate-400 mt-1` bottom-right aligned.

#### Password Visibility Toggle

- Right icon button (Eye / EyeOff icons) toggles `input.type` between `password` and `text`.

---

### 2.3 Select

#### Variants

- **Native select:** Wraps `<select>` element for full browser autofill/form support.
- **Custom dropdown:** Trigger button + dropdown list, used when rich options (icons, descriptions) are needed.

#### Sizes

Same as Input: sm (32 px), md (40 px), lg (48 px).

#### States

| State     | Border        | Background     | Chevron           |
|-----------|---------------|----------------|-------------------|
| default   | slate-300     | white          | slate-400         |
| focus     | primary-500   | white          | primary-500       |
| error     | error-500     | white          | error-500         |
| disabled  | slate-200     | slate-100      | slate-300         |

- Chevron icon: `<ChevronDown size={16}>` with `transition-transform` — rotates 180° on open.

#### Placeholder

When no option is selected, show placeholder text in `text-slate-400`. Native select: use `<option value="" disabled selected>`.

---

### 2.4 Checkbox & Radio

#### Sizes

| Size | Box     | Icon Size |
|------|---------|-----------|
| sm   | 16 px   | 12 px     |
| md   | 20 px   | 14 px     |

#### States

| State        | Border        | Background     | Icon/Checkmark    |
|--------------|---------------|----------------|-------------------|
| unchecked    | slate-300     | white          | hidden            |
| checked      | primary-500   | primary-500    | white checkmark   |
| indeterminate| primary-500   | primary-500    | white minus       |
| disabled     | slate-200     | slate-100      | slate-300         |
| error        | error-500     | error-50       | error-600         |

- **Label:** `text-sm text-slate-700` positioned to the right with `gap-3`.
- **Focused:** `ring-2 ring-primary-500/20` on the input.
- **Radio:** Circular shape (`rounded-full`). Checked state shows a filled inner circle.

---

### 2.5 Badge

#### Variants

| Variant | Background     | Text           |
|---------|----------------|----------------|
| default | slate-100      | slate-700      |
| primary | primary-100    | primary-700    |
| success | success-100    | success-700    |
| warning | warning-100    | warning-800    |
| error   | error-100      | error-700      |
| info    | info-100       | info-700       |
| purple  | purple-100     | purple-700     |
| pink    | pink-100       | pink-700       |

#### Sizes

| Size | Height | Padding         | Font       |
|------|--------|-----------------|------------|
| sm   | 18 px  | `px-1.5`        | `text-xs`  |
| md   | 22 px  | `px-2`          | `text-xs`  |
| lg   | 26 px  | `px-2.5`        | `text-sm`  |

#### Variations

- **Dot indicator:** 6 px circle (`rounded-full`) before text, colour matches variant.
- **Remove button:** `×` or `<X size={12}>` on the right, only on md/lg. Clicking dispatches an `onRemove` callback.

---

### 2.6 Card

#### Variants

| Variant   | Background | Border         | Shadow  | Hover                    |
|-----------|------------|----------------|---------|--------------------------|
| default   | white      | none           | none    | none                     |
| bordered  | white      | slate-200, 1px | none    | none                     |
| elevated  | white      | none           | md      | lg on hover              |
| interactive | white   | slate-200, 1px | sm      | shadow-lg, translateY(-2px), border-primary-300 |

#### Card Sections

- **Header:** `px-4 pt-4 pb-2` (default) or `px-6 pt-6 pb-3` (comfortable). Contains title + optional actions.
- **Body:** `px-4 py-2` (default), `px-6 py-3` (comfortable). Main content area.
- **Footer:** `px-4 pb-4 pt-2` (default), `px-6 pb-6 pt-3` (comfortable). Border-top divider. Contains actions.

#### Actions

- **Top-right actions:** Absolute-positioned icon buttons in the header (`top-3 right-3`).
- **Clickable card:** Entire card clickable via a wrapping `<Link>` or `onClick`. Interactive cursor. Hover state as defined above.

---

### 2.7 Modal

#### Sizes

| Name | Max Width | Usage                        |
|------|-----------|------------------------------|
| sm   | 400 px    | Confirmations, short prompts |
| md   | 500 px    | Default, most dialogs        |
| lg   | 700 px    | Forms, detailed content      |
| xl   | 900 px    | Complex forms, data tables   |
| full | 100%      | Full-screen takeover         |

#### Structure

- **Backdrop:** Fixed full-screen overlay (`bg-black/50`). Optional blur via Framer Motion.
- **Dialog panel:** Centered (`flex items-center justify-center`), white background, `rounded-xl`, `shadow-xl`.
- **Header:** `flex items-center justify-between`, `p-6 pb-0`. Title (`text-lg font-semibold`). Close button (ghost, no label, `<X>` icon).
- **Body:** `p-6`. Scrollable if content overflows — `overflow-y-auto max-h-[70vh]`.
- **Footer:** `flex items-center justify-end gap-3`, `p-6 pt-0`. Contains action buttons (Cancel + Confirm).

#### Behaviour

- **Close on ESC:** `useEffect` with `keydown` listener for `Escape`.
- **Close on overlay click:** Click handler on backdrop (exclude dialog panel via `e.stopPropagation()`).
- **Focus trap:** First focusable element receives focus on mount. Tab cycles within modal. Use `focus-trap-react` or custom implementation.
- **Body scroll lock:** `overflow: hidden` on `<body>` when modal is open.
- **Animation:** Framer Motion — backdrop fades in (`opacity: 0 → 1`), dialog scales and fades (`scale: 0.95 → 1, opacity: 0 → 1`) with `type: "spring"`, `duration: 0.3`.

---

### 2.8 Table

#### Variants

| Variant   | Styling                                 |
|-----------|-----------------------------------------|
| default   | Horizontal borders only (`border-b`)    |
| striped   | Alternating row backgrounds (even: `slate-50`) |
| bordered  | Full grid borders (`border` on all cells) |
| compact   | Reduced padding (`px-3 py-2`)           |

#### Header

- **Sortable headers:** Click handler toggles sort direction. Icon (ChevronUp/Down or ArrowUpDown) indicates sort state. Active sorted column header text is `font-semibold`.
- **Select all checkbox:** In first column header.

#### Rows

- **Selectable rows:** First column is a checkbox. Checked row gets `bg-primary-50` background.
- **Action column:** Last column with a kebab menu (`<MoreHorizontal>` icon) triggering a dropdown with row actions.

#### States

- **Empty state:** Colspan covers all columns. Centered illustration/message with optional CTA button.
- **Loading state:** Skeleton rows (`animate-pulse`) matching column widths.

#### Responsive

- **Desktop:** Standard table layout.
- **Tablet/Mobile:** Wrap table in `overflow-x-auto` for horizontal scroll. Optionally render as a card list (`<div>` per row) at `max-md:`.

---

### 2.9 Dropdown

#### Positions

| Position      | Classes                                     |
|---------------|---------------------------------------------|
| bottom-left   | `top-full left-0 mt-1`                      |
| bottom-right  | `top-full right-0 mt-1`                     |
| top-left      | `bottom-full left-0 mb-1`                   |
| top-right     | `bottom-full right-0 mb-1`                  |

#### Structure

- **Trigger:** Button or clickable element with ref.
- **Panel:** Absolute-positioned `div`, `min-w-[12rem]`, `bg-white`, `rounded-lg`, `shadow-lg`, `ring-1 ring-black/5`, `z-dropdown`.
- **Item:** `flex items-center gap-3 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100`. Active item: `bg-slate-100 text-slate-900`.
- **Icon item:** Lucide icon (16–18 px) left-aligned.
- **Divider:** `<hr class="my-1 border-slate-200">`.
- **Header:** `px-4 py-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider`.
- **Disabled item:** `opacity-50 cursor-not-allowed`.

#### Behaviour

- Open on trigger click, close on outside click (ref-based detection) or ESC.
- Framer Motion: `initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }}`, `exit` for unmount.
- **Scrollable:** `max-h-60 overflow-y-auto` when content exceeds height.

---

### 2.10 Tabs

#### Variants

| Variant   | Styling                                                          |
|-----------|------------------------------------------------------------------|
| underline | `border-b border-slate-200`. Active tab: `border-b-2 border-primary-500 text-primary-600`. |
| pill      | `rounded-lg`. Active: `bg-primary-500 text-white`. Inactive: `text-slate-600 hover:bg-slate-100`. |
| segmented | `rounded-lg bg-slate-100 p-1`. Active: `bg-white shadow-sm`. |

#### Features

- **With icon:** Lucide icon (16 px) before the label.
- **With badge count:** `<Badge>` component inline after label, `ml-2`.
- **Scrollable:** Horizontal scroll container with fade edges when overflow. Use `overflow-x-auto` with `scroll-snap-x`.
- **Animation:** Framer Motion `layoutId="active-tab"` for the active indicator underline/pill transition.

---

### 2.11 Pagination

#### Structure

- **Page numbers:** Visible pages shown with smart ellipsis (e.g. `1 ... 5 6 7 ... 20`).
- **Previous / Next buttons:** `<<` and `>>` with `ChevronLeft` / `ChevronRight` icons. Disabled (`opacity-50 pointer-events-none`) at boundaries.
- **Page size selector:** Small `<select>` or button group (10 / 20 / 50 / 100).
- **Total count:** `text-sm text-slate-500` — "Showing 1–10 of 247 results".

#### States

| Element       | Default                               | Active              | Disabled            |
|---------------|---------------------------------------|---------------------|---------------------|
| Page button   | `w-9 h-9 text-sm rounded-md`          | `bg-primary-500 text-white` | —        |
| Prev/Next     | Same as page button                   | —                   | `opacity-30`        |

---

### 2.12 Breadcrumb

#### Structure

- **Home icon:** `<Home size={16}>` inline as first item.
- **Items:** `text-sm` links, separated by a chevron (`<ChevronRight size={14}>`), slash (`/`), or arrow (`→`).
- **Last item:** Current page, `text-slate-900 font-medium`, not a link.
- **Max items:** When more than 4 items, truncate middle items with ellipsis (`…`) — clicking expands the full path.

---

### 2.13 Toast / Notification

#### Types

| Type    | Icon            | Background  | Border          |
|---------|-----------------|-------------|-----------------|
| success | `<CheckCircle>` | success-50  | success-500     |
| error   | `<XCircle>`     | error-50    | error-500       |
| warning | `<AlertTriangle>`| warning-50 | warning-500     |
| info    | `<Info>`        | info-50     | info-500        |

#### Structure

- **Container:** Fixed `top-4 right-4`, `z-toast`. Stacks toasts vertically with `gap-3`.
- **Toast:** `min-w-[320px] max-w-[420px]`, `rounded-lg`, `shadow-lg`, `p-4`. Flex layout: icon | content | dismiss.
- **Content:** Title (`text-sm font-semibold`), Description (`text-sm text-slate-600`), optional Action button.
- **Dismiss:** `<X size={16}>` button (ghost).

#### Behaviour

- **Auto-dismiss:** Default 5 seconds. Configurable per toast.
- **Manual dismiss:** Click X button.
- **Animation:** Framer Motion — `initial={{ opacity: 0, x: 100 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 100, scale: 0.95 }}`. Stack animates with `layout` prop.
- **Stacking:** Multiple toasts render as a vertical stack. New toasts appear at the top.

---

### 2.14 Alert

#### Types

| Type    | Icon            | Background     | Border        |
|---------|-----------------|----------------|---------------|
| info    | `<Info>`        | info-50        | info-200      |
| success | `<CheckCircle>` | success-50     | success-200   |
| warning | `<AlertTriangle>`| warning-50    | warning-200   |
| error   | `<XCircle>`     | error-50       | error-200     |

#### Variants

| Variant   | Styling                          |
|-----------|----------------------------------|
| inline    | `rounded-lg p-4`                 |
| banner    | `rounded-none px-4 py-3 w-full`  |

#### Structure

- `flex items-start gap-3` with icon, content, and optional dismiss/action.
- Title: `text-sm font-semibold`. Description: `text-sm`.
- Dismissible: `<X>` button. `onDismiss` callback.
- Action: `<button>` or `<Link>` inside the alert, styled as an inline text link.

---

### 2.15 Tooltip

#### Positions

| Position | Classes                          |
|----------|----------------------------------|
| top      | `bottom-full left-1/2 -translate-x-1/2 mb-2` |
| bottom   | `top-full left-1/2 -translate-x-1/2 mt-2`    |
| left     | `right-full top-1/2 -translate-y-1/2 mr-2`   |
| right    | `left-full top-1/2 -translate-y-1/2 ml-2`    |

#### Arrow

- 8 px × 8 px rotated square (`rotate-45`) absolutely positioned. Background matches tooltip background. Border via `border` on the parent.

#### Behaviour

- **Show:** On `mouseEnter` / `focus`. Default delay: 300 ms.
- **Hide:** On `mouseLeave` / `blur`. Default delay: 100 ms.
- **Max width:** `max-w-xs` (320 px).
- **Content:** `px-3 py-1.5 text-xs font-medium bg-slate-900 text-white rounded-md`.
- **Animation:** Framer Motion — `initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}`.
- **Accessibility:** `role="tooltip"` on the floating element. `aria-describedby` on the trigger referencing the tooltip `id`.

---

### 2.16 Skeleton

#### Variants

| Variant    | Classes                                  | Usage                    |
|------------|------------------------------------------|--------------------------|
| text       | `h-4 w-full rounded`                     | Text line placeholder   |
| circle     | `h-10 w-10 rounded-full`                 | Avatar placeholder      |
| rectangle  | `h-32 w-full rounded-lg`                 | Image placeholder       |
| card       | `h-40 w-full rounded-xl`                 | Card placeholder        |
| table-row  | `h-12 w-full rounded`                    | Table row placeholder   |

#### Animation

- **Pulse:** `animate-pulse` (Tailwind built-in) — opacity fades 100% → 75%.
- **Shimmer:** Custom `animate-shimmer` using CSS gradient + `translateX` keyframes. Preferred for content-heavy sections.

#### Colours

- Background: `bg-slate-200` (light), `bg-slate-700` (dark).
- Shimmer highlight: `via-white/30` (light), `via-white/5` (dark).
- Use `rounded-md` by default unless variant specifies otherwise.

---

### 2.17 Avatar

#### Sizes

| Size | Dimension | Tailwind     | Icon Size | Initials Font |
|------|-----------|--------------|-----------|---------------|
| xs   | 24 px     | `w-6 h-6`    | 12 px     | `text-xs`     |
| sm   | 32 px     | `w-8 h-8`    | 14 px     | `text-sm`     |
| md   | 40 px     | `w-10 h-10`  | 18 px     | `text-base`   |
| lg   | 48 px     | `w-12 h-12`  | 20 px     | `text-lg`     |
| xl   | 64 px     | `w-16 h-16`  | 24 px     | `text-xl`     |
| 2xl  | 80 px     | `w-20 h-20`  | 32 px     | `text-2xl`    |

#### States

- **Image:** `<img>` with `object-cover rounded-full`. On error, fallback to initials or icon.
- **Initials fallback:** First two characters of name, `bg-primary-100 text-primary-700 font-semibold`.
- **Icon fallback:** `<User>` icon in `text-slate-400` on `bg-slate-200`.
- **Status dot:** 8 px circle bottom-right of avatar. Green (online), slate (offline), amber (away). Absolute-positioned with 2 px white ring.

#### Grouped Avatars

- Overlapping stack (`-ml-2` per subsequent avatar), bordered with 2 px white ring.
- "+N" overflow indicator: last circle shows "+3" for remaining count.

---

### 2.18 Progress Bar

#### Variants

| Variant      | Behaviour                                  |
|--------------|--------------------------------------------|
| determinate  | Value between 0–100. Width reflects value. |
| indeterminate| Continuous animation (`animate-pulse` or striped). |

#### Sizes

| Size | Height |
|------|--------|
| sm   | 4 px   |
| md   | 8 px   |
| lg   | 12 px  |

#### Colours

- **Track:** `bg-slate-200` (light), `bg-slate-700` (dark).
- **Fill:** `bg-primary-500` by default. Overridable: success (`success-500`), warning (`warning-500`), error (`error-500`).
- **Label & percentage:** `text-sm font-medium` above or to the right of the bar.
- **Animation:** Width transitions with `transition-all duration-500 ease-out` for smooth filling. Indeterminate uses `animate-progress` keyframes.

---

### 2.19 Accordion

#### Structure

- **Trigger:** Button with `w-full flex items-center justify-between px-4 py-3 text-sm font-medium`. Chevron icon rotates 180° on open.
- **Content panel:** `px-4 pb-3 pt-1 text-sm text-slate-600`.
- **Border:** `border-b border-slate-200` between items.

#### Variants

| Variant  | Styling                                              |
|----------|------------------------------------------------------|
| default  | `rounded-none` with border separators               |
| compact  | Reduced padding (`px-3 py-2`), smaller font          |

#### Behaviour

- **Single expand:** Only one panel open at a time. Close previously opened on new trigger.
- **Multi expand:** Multiple panels can remain open.
- **Animation:** Framer Motion `AnimatePresence` + `motion.div` with `initial={{ height: 0 }} animate={{ height: "auto" }} exit={{ height: 0 }}`. `overflow-hidden`.

---

## 3. Form Patterns

### 3.1 Layout

| Layout        | Usage                          | Grid                          |
|---------------|--------------------------------|-------------------------------|
| Single column | Most forms, mobile-first       | `flex flex-col gap-4`         |
| Multi-column  | Address, settings, dense forms | `grid grid-cols-1 md:grid-cols-2 gap-4` |
| Inline        | Search/filter bars             | `flex flex-wrap items-end gap-3` |

### 3.2 Field Groups

- Related fields grouped in a `<fieldset>` with `<legend>` or a visual group with divider.
- Consistent `gap-4` between fields within a group.
- Groups separated by `<hr class="my-6">` for sections.

### 3.3 Validation

| Trigger   | When                                        |
|-----------|---------------------------------------------|
| onBlur    | On field exit — shows errors immediately    |
| onChange  | After first blur — real-time validation     |
| onSubmit  | On form submit — validates all fields       |

### 3.4 Error Display

- **Below field:** `text-xs text-error-500 mt-1` message.
- **Field border:** Input/Select receives error border colour (`border-error-500`).
- **Group error:** Banner at the top of a form section: "Please fix 3 errors below."
- **Summary:** Optional error summary above the submit button.

### 3.5 Success Display

- Green checkmark icon (`<CheckCircle size={16}>`) to the right of the input `pr-10`.
- `border-success-500` on the field.

### 3.6 Help Text

- Below field, `text-xs text-slate-500 mt-1`.
- Can contain links or formatting for guidance.

### 3.7 Required Indicator

- Asterisk (`*`) after the label, `text-error-500` colour.
- Legend at form top: "Fields marked with * are required."

### 3.8 Submit Button

- Full width on mobile, left-aligned or right-aligned on desktop.
- `gap-3` between Cancel and Submit.
- Submit uses `type="submit"`. Primary variant. Disabled during submission, shows loading spinner.

### 3.9 Multi-Step Form

- **Progress indicator:** Stepper component at top.
  - Each step: circle (numbered or checkmark) + label.
  - Active step: primary-500. Completed: success-500. Future: slate-300.
  - Connector line between steps.
- **Navigation:** Back / Next buttons at the bottom. "Back" is ghost, "Next" is primary.
- **Content:** Single step visible at a time. Framer Motion `AnimatePresence` with slide direction.

---

## 4. Navigation Patterns

### 4.1 Top Navigation

- Fixed at top, `h-16`, `bg-white/95 backdrop-blur-md`, `border-b border-slate-200`, `z-navbar`.
- **Left:** Logo + brand mark.
- **Center:** Primary nav links (hidden on mobile, shown on `md:`).
- **Right:** Search, notifications (bell icon with badge), user avatar dropdown.
- **Dropdowns:** Mega-menu style for categories on marketplace. Framer Motion slide + fade.

### 4.2 Sidebar Navigation

- Fixed left, `w-64`, `bg-white`, `border-r border-slate-200`, `z-sticky`.
- **Collapsible:** Toggle button collapses to `w-16` (icons only) on desktop. User preference persisted.
- **Nested items:** Indentation, expand/collapse chevron. Active item: `bg-primary-50 text-primary-700` + left border accent.
- **Section labels:** `text-xs font-semibold text-slate-500 uppercase tracking-wider px-4 pt-6 pb-2`.

### 4.3 Mobile Navigation

- **Hamburger drawer:** Slide-in panel from left. Full viewport height. Overlay backdrop. Framer Motion slide animation.
- **Bottom tab bar:** Fixed `h-16` at bottom. 4–5 tabs with icons + labels. Active tab uses primary colour. Present only on mobile (`lg:hidden`).

### 4.4 Breadcrumb Navigation

- As defined in [2.12 Breadcrumb](#212-breadcrumb).
- Used on product detail, category, dashboard pages.

### 4.5 Step Navigation (Checkout)

- Horizontal stepper across the top of the checkout flow.
- Steps: Cart → Shipping → Payment → Confirmation.
- Interactive: click completed steps to revisit.
- Responsive: collapses to vertical list on mobile.

### 4.6 Tab Navigation (Detail Pages)

- As defined in [2.10 Tabs](#210-tabs).
- Used on product pages (Details, Reviews, Shipping Info) and dashboard sections.

---

## 5. Feedback Patterns

### 5.1 Toast Notifications

- Used for: "Item added to cart", "Order placed", "Settings saved".
- Auto-dismiss after 5 seconds unless it requires user action.
- Stack vertically, newest on top.

### 5.2 Inline Alerts

- Used for: "No search results found", "Connection lost", "Payment declined".
- Placed at page top or within a section.
- Banner variant for critical system messages.

### 5.3 Modals for Confirmations

- Used for: "Delete item?", "Cancel order?", "Discard changes?".
- Small modal (sm). Title, description, Cancel + Confirm (danger variant) buttons.

### 5.4 Loading States

- **Content loading:** Skeleton placeholders matching final layout dimensions. No layout shift.
- **Action loading:** Button shows `<Loader2>` spinner. Form inputs and buttons are disabled.
- **Page transition:** Full-page loading overlay on route change.
- **Infinite scroll:** Bottom-of-list skeleton or spinner on feed/listing pages.

### 5.5 Empty States

- **Illustration:** Relevant SVG illustration (e.g. empty cart, no orders).
- **Message:** Title + description explaining the empty state.
- **Action:** CTA button to resolve (e.g. "Browse Products", "Create First Listing").
- **Layout:** Centered in available space, `py-16`.

### 5.6 Error States

- **Message:** Description of what went wrong.
- **Retry:** Button or link to retry the failed action.
- **Fallback:** If applicable, alternative content suggestion.

### 5.7 Progress Indicators

- Used for: Multi-step forms (checkout, vendor onboarding), file upload, batch operations.
- Determinate progress bar for measurable tasks, indeterminate for unknown duration.

### 5.8 Optimistic UI Updates

- Update UI immediately on user action (e.g. toggle favourite, add to cart).
- Show success state with the option to undo (e.g. "Removed from favourites" → "Undo").
- On API failure, revert the change and show an error toast.

---

## 6. Data Visualization

### 6.1 Charts (via Recharts)

| Chart Type | Usage                                           |
|------------|-------------------------------------------------|
| Line       | Sales trends over time, traffic analytics       |
| Bar        | Category comparison, monthly revenue breakdown  |
| Pie        | Category distribution (market share)            |
| Area       | Cumulative sales, user growth                   |
| Donut      | Rating breakdown, payment method distribution   |

- **Colours:** Pull from primary palette and semantic colours.
- **Responsive:** Container-based resizing via `ResponsiveContainer`.
- **Tooltips:** Custom tooltip card matching design system styling.
- **Empty state:** Chart area shows "No data" placeholder.

### 6.2 Metric Cards

- **Value:** Large font (`text-3xl font-bold`).
- **Label:** `text-sm text-slate-500`.
- **Trend indicator:** Percent change with up/down arrow. Positive: `text-success-500`. Negative: `text-error-500`.

### 6.3 Rating Distribution

- Horizontal stacked bar chart showing 1–5 star counts.
- Total width indicates proportion. Star icon on the left.

### 6.4 Progress Bars

- As defined in [2.18 Progress Bar](#218-progress-bar).
- Used for vendor completion score, listing quality, achievement badges.

### 6.5 Sparklines

- Mini line charts embedded in table cells or metric cards.
- Simple SVG polyline without axes.
- 80–120 px width, 24–32 px height.

### 6.6 Colour Coding for Status

| Status       | Colour       |
|--------------|--------------|
| Active       | success-500  |
| Pending      | warning-500  |
| Suspended    | error-500    |
| Draft        | slate-400    |
| In Review    | info-500     |
| Verified     | success-500  |

---

## 7. Dark Mode

### 7.1 Strategy

CSS custom properties overridden via the `dark` class on `<html>`. Tailwind's `dark:` variant used for component-level overrides.

### 7.2 Colour Overrides

| Light Token        | Dark Token         | Notes                          |
|--------------------|--------------------|---------------------------------|
| white / neutral-50 | slate-900          | Page background                 |
| slate-50           | slate-800          | Card background                 |
| slate-100          | slate-800          | Surface background              |
| slate-200          | slate-700          | Borders                         |
| slate-300          | slate-600          | Input borders                   |
| slate-400          | slate-500          | Disabled text                   |
| slate-500          | slate-400          | Muted text                      |
| slate-700          | slate-300          | Body text                       |
| slate-800          | slate-100          | Heading text                    |
| slate-900          | slate-50           | High-emphasis text              |

### 7.3 Component-Specific Dark Styles

- **Cards:** `bg-slate-800`, border `slate-700`, shadow reduced to `shadow-lg` with `ring-1 ring-white/5`.
- **Buttons (primary):** Same background, text white. Hover: brighten 100 levels.
- **Buttons (ghost):** `text-slate-300 hover:bg-slate-700`.
- **Modals:** `bg-slate-800`, backdrop `bg-black/70`.
- **Inputs:** `bg-slate-800 border-slate-600 text-slate-100`.
- **Dropdowns:** `bg-slate-800 ring-1 ring-white/10`, items `hover:bg-slate-700`.
- **Tables:** `border-slate-700`, header `bg-slate-800`, striped rows `bg-slate-800/50`.

### 7.4 Shadows

- Reduced opacity: All shadow values halved in opacity.
- Alternative: Use `shadow-lg` + `ring-1 ring-white/5 ring-inset` for depth instead of heavy shadows.

### 7.5 Contrast

- Minimum contrast ratio 4.5:1 for text, 3:1 for large text (WCAG AA).
- Dark backgrounds: white text with `font-medium` to compensate for reduced contrast.
- Interactive elements maintain 3:1 contrast against their background in all states.

### 7.6 Persistence & Detection

- System preference: `prefers-color-scheme: dark` media query.
- Manual toggle: User can switch via button in navbar. Preference persisted in `localStorage`.
- Priority: Manual toggle > System preference > Light (default).
- `class`-based approach: `dark` class on `<html>`. No flash-of-wrong-theme via inline script in `<head>`.

---

## 8. Responsive Adaptation

### 8.1 Component Behaviour at Breakpoints

| Component      | < md (768 px)                | ≥ md                           | ≥ lg (1024 px)                |
|----------------|------------------------------|--------------------------------|-------------------------------|
| Top Nav        | Logo + hamburger + cart      | Logo + links + search + user   | Same + full search            |
| Sidebar        | Hidden (slide drawer)        | Hidden (slide drawer)          | Visible, collapsible          |
| Table          | Horizontal scroll / card list| Horizontal scroll              | Full table                     |
| Cards grid     | 1 column                     | 2 columns                      | 3–4 columns                   |
| Forms          | Single column                | Single column                  | Multi-column sections         |
| Modal          | 90% width, full-height       | Centered, sm/md size           | Any size                       |
| Tabs           | Horizontal scroll            | Full width                     | Full width                     |
| Pagination     | Prev/Next only               | Prev + pages + Next            | Full pagination + size selector|

### 8.2 Table → Card List

- At `max-md:`, `<table>` transforms into a card list:
  - Each row becomes a card (`rounded-lg border p-4`).
  - Each cell becomes a labelled row: `<span class="font-medium">Label:</span> {value}`.
  - Actions become full-width buttons or icon row.
  - Checkbox remains on the left.

### 8.3 Sidebar → Bottom Nav

- At `max-lg:`, the sidebar collapses entirely.
- Primary navigation items appear in a fixed bottom tab bar.
- Secondary nav items are accessible via a "More" tab or a hamburger drawer.
- Bottom bar is `h-16 bg-white border-t` with `px-4` spacing.

### 8.4 Multi-Column → Single Column

- Layouts using `grid-cols-2` or `grid-cols-3` collapse to `grid-cols-1` at `max-md:`.
- Side-by-side filter panels stack vertically.
- Product grids: `grid-cols-2` on mobile, `grid-cols-3` on md, `grid-cols-4` on lg.

### 8.5 Horizontal Scroll

- Overflowing content (code blocks, wide tables, tab bars) wrapped in `overflow-x-auto`.
- Fade edges using CSS gradients on a pseudo-element mask.
- Scroll indicators (arrows) optionally shown on hover.

### 8.6 Touch-Friendly Interactions

- Minimum touch target: 44 px × 44 px (WCAG 2.5.5).
- Buttons, links, form controls sized to meet this minimum, especially on mobile.
- Hover-only effects (underline, background change) also activate on `:focus-visible` and `:active` for touch users.
- Swipe gestures: Product carousels, image galleries, notification dismiss.
- Tap feedback: Framer Motion `whileTap={{ scale: 0.97 }}` on interactive elements.
- No horizontal pinch-zoom disabled — maintain user control.
