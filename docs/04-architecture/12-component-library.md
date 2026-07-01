# Component Library Architecture

> **Project:** TRUE STAR BD LIMITED — Multi-Vendor Digital Marketplace
> **Stack:** React 19+, Next.js 15+, TypeScript, TailwindCSS, Lucide React, Framer Motion
> **Status:** Architecture Reference

---

## 1. Component Architecture Philosophy

### Composition over Configuration

Components are designed as composable primitives rather than monolithic, prop-driven behemoths. A `Modal` component does not accept 50 props; instead, it composes `Modal.Overlay`, `Modal.Content`, `Modal.Header`, `Modal.Body`, and `Modal.Footer` subcomponents. This gives consumers full control over layout and styling while keeping each API surface narrow.

### Single Responsibility Principle

Each component owns exactly one concern. `FormField` handles label, error, and helper text wiring — it does not know how its child input validates. `Badge` renders a visual label — it does not handle click navigation. If a component grows multiple responsibilities, it is decomposed.

### Controlled and Uncontrolled Variants

Every form-like component (`Input`, `Select`, `Checkbox`, `Switch`, etc.) supports both controlled (value + onChange) and uncontrolled (defaultValue) usage. The internal pattern follows the `useControllableState` hook pattern, identical to how Radix UI or Reakit manage dual-mode state.

### TypeScript Generics for Reusable Types

Components that operate on arbitrary data shapes accept generic type parameters. `DataTable<T>` infers column accessors, row keys, and render props from the data type. `Select<T>` infers option value types. This eliminates `any` casts and provides full autocomplete to consumers.

### Forward Refs for Accessibility

All interactive elements — buttons, inputs, triggers, menu items — expose a ref via `forwardRef`. This enables imperative focus management, tooltip anchoring, and integration with third-party libraries (react-hook-form, react-aria, etc.).

### Compound Components Pattern

Complex UI surfaces (Tabs, Accordion, DropdownMenu, DataTable) expose a compound API. The parent component shares implicit state via `React.Context` so children synchronize without prop drilling. The consumer is free to reorder or omit children without breaking functionality.

### Render Props Where Appropriate

For components that require custom rendering (dropdown item content, table cell formatting, tooltip content), a render prop or `ReactNode` slot is preferred over a rigid set of props. This keeps the library open for arbitrary UI while maintaining consistent behavior.

---

## 2. Base UI Components (Atoms)

### Button

| Aspect | Details |
|--------|---------|
| **Component** | `<Button>` |
| **Props** | `variant` (primary, secondary, outline, ghost, danger, link), `size` (xs, sm, md, lg, xl), `loading` (boolean, shows spinner + disables), `icon` (Lucide icon component), `iconPosition` (left, right), `as` (polymorphic — `"a"`, `"button"`, or a component like `next/link`), `fullWidth`, `disabled`, `type` (submit, button, reset) |
| **Description** | Primary action trigger. Supports loading state with animated spinner, icon-only mode (square aspect ratio), and polymorphic rendering via `as` prop for router links. |
| **States** | default, hover, active, focused-visible, disabled, loading |
| **Accessibility** | `role="button"` when `as` is not a `<button>`; `aria-disabled` when loading (button stays focusable but announces busy); `aria-label` when icon-only; focus-visible ring via Tailwind `focus-visible:` |
| **Usage** | `<Button variant="primary" size="md" icon={ShoppingCart}>Add to Cart</Button>` |

### Input

| Aspect | Details |
|--------|---------|
| **Component** | `<Input>` |
| **Props** | `type` (text, email, password, number, tel, url, search, date), `size` (sm, md, lg), `state` (default, error, success, warning), `icon` (leading Lucide icon), `iconPosition` (left, right), `passwordToggle` (boolean — shows eye icon to reveal/hide password), `clearable` (boolean — shows X to clear value), `label` (renders floating label), `helperText`, `errorMessage`, `fullWidth`, `leftAddon`/`rightAddon` (string or ReactNode for prefix/suffix) |
| **Description** | Versatile text input with icon adornments, validation states, password visibility toggle, and clear button. All standard HTML input types supported. |
| **States** | default, hover, focus, disabled, readOnly, error, success, warning, filled |
| **Accessibility** | `aria-invalid` when `state="error"`; `aria-describedby` linking to `helperText`/`errorMessage`; `aria-label` when no visible label; label clickable via `htmlFor` |
| **Usage** | `<Input type="email" icon={Mail} state="error" errorMessage="Invalid email" placeholder="you@example.com" />` |

### Textarea

| Aspect | Details |
|--------|---------|
| **Component** | `<Textarea>` |
| **Props** | `size` (sm, md, lg), `resizable` (boolean, default true), `rows` (number, default 4), `maxLength` (character limit), `showCharCount` (boolean — displays `{current}/{max}`), `state` (default, error), `placeholder`, `autoResize` (grows with content via scrollHeight) |
| **Description** | Multi-line text input with optional auto-resize and character counter. |
| **States** | default, focus, disabled, error, filled, at-limit (visual hint when approaching maxLength) |
| **Accessibility** | `aria-invalid`; `aria-describedby` for char count; `aria-label` as fallback |
| **Usage** | `<Textarea maxLength={500} showCharCount autoResize placeholder="Product description..." />` |

### Select

| Aspect | Details |
|--------|---------|
| **Component** | `<Select>` |
| **Props** | `variant` (native, custom), `options` (`Array<{ value, label, disabled?, group? }>`), `grouped` (boolean — renders `<optgroup>`), `size` (sm, md, lg), `searchable` (boolean — filterable dropdown), `placeholder`, `clearable`, `loading`, `emptyMessage`, `state` (error, success) |
| **Description** | Dual-mode select: native `<select>` for simplicity/customization, or a custom dropdown with search filtering and grouped options. |
| **States** | default, hover, focus, open, disabled, error, loading, empty (no results), selected |
| **Accessibility** | `aria-expanded` on trigger; `aria-activedescendant` on searchable variant; `role="listbox"` and `role="option"`; keyboard navigation (arrow keys, Enter, Escape) |
| **Usage** | `<Select searchable placeholder="Choose category" options={categories} onValueChange={setCat} />` |

### Checkbox

| Aspect | Details |
|--------|---------|
| **Component** | `<Checkbox>` |
| **Props** | `checked` (controlled boolean or `"indeterminate"`), `defaultChecked`, `onCheckedChange`, `indeterminate` (boolean, tri-state), `disabled`, `size` (sm, md, lg), `label` (ReactNode), `id`, `name`, `value` |
| **Description** | Checkbox with optional label. Supports indeterminate state (tri-state for "select all" / tree nodes). Renders as a styled box with check/indeterminate icon. |
| **States** | unchecked, checked, indeterminate, hover, focus-visible, disabled, disabled+checked |
| **Accessibility** | Native `<input type="checkbox">` hidden behind styled element; `aria-checked="mixed"` for indeterminate; label clickable; keyboard toggle via Space |
| **Usage** | `<Checkbox checked={isIndeterminate} indeterminate label="Select all" onCheckedChange={handleAll} />` |

### RadioGroup

| Aspect | Details |
|--------|---------|
| **Component** | `<RadioGroup>` (parent), `<RadioGroup.Item>` (child) |
| **Props (Group)** | `value` (controlled), `defaultValue`, `onValueChange`, `name`, `orientation` (horizontal, vertical), `label` (fieldset legend), `disabled` |
| **Props (Item)** | `value`, `disabled`, `label`, `id` |
| **Description** | Radio button group wrapped in a `<fieldset>` with `<legend>`. Works as controlled or uncontrolled. Radios are visually styled circles with fill animation. |
| **States** | unchecked, checked, hover, focus-visible, disabled |
| **Accessibility** | `role="radiogroup"`; each item has `role="radio"` and `aria-checked`; keyboard navigation via arrow keys |
| **Usage** | `<RadioGroup label="Payment Method"><RadioGroup.Item value="bkash" label="bKash" /><RadioGroup.Item value="nagad" label="Nagad" /></RadioGroup>` |

### Switch / Toggle

| Aspect | Details |
|--------|---------|
| **Component** | `<Switch>` |
| **Props** | `checked`, `defaultChecked`, `onCheckedChange`, `disabled`, `size` (sm, md, lg), `label` (ReactNode, renders alongside or above), `labelPosition` (left, right), `srOnlyLabel` (for icon-only) |
| **Description** | Toggle switch with smooth thumb animation. Can be used standalone or paired with a label. |
| **States** | off, on, hover, focus-visible, disabled, disabled+on |
| **Accessibility** | `role="switch"`; `aria-checked`; keyboard toggle via Enter or Space; label clickable |
| **Usage** | `<Switch checked={notifications} onCheckedChange={setNotifications} label="Push notifications" />` |

### Badge

| Aspect | Details |
|--------|---------|
| **Component** | `<Badge>` |
| **Props** | `variant` (default, primary, success, warning, danger, info, outline, ghost), `size` (sm, md, lg), `dot` (boolean — renders as small indicator dot), `removable` (boolean — shows X to dismiss), `onRemove` (callback), `as` (polymorphic for links) |
| **Description** | Small label/tag for status, counts, or categories. Supports dot-only mode for online status indicators. |
| **States** | default, removable (with hover on X), clickable (when wrapped in interactive parent) |
| **Accessibility** | `aria-label` when removable; close button has `aria-label="Remove"` |
| **Usage** | `<Badge variant="success" dot>Verified</Badge>` |

### Avatar

| Aspect | Details |
|--------|---------|
| **Component** | `<Avatar>` |
| **Props** | `src` (image URL), `alt` (alt text), `fallback` (initials or ReactNode, shown while loading or on error), `size` (xs, sm, md, lg, xl, 2xl), `status` (online, offline, away, busy — shows colored dot), `statusPosition` (bottom-right, top-right), `shape` (circle, square, rounded) |
| **Description** | Image avatar with fallback initials, loading state, and online status indicator dot. |
| **States** | loaded, loading (skeleton pulse), error (fallback shown), with-status |
| **Accessibility** | `role="img"` with `aria-label` from `alt`; status dot uses `aria-label` |
| **Usage** | `<Avatar src="/sellers/john.jpg" fallback="JD" status="online" size="lg" />` |

### Card

| Aspect | Details |
|--------|---------|
| **Component** | `<Card>`, `<Card.Header>`, `<Card.Body>`, `<Card.Footer>` |
| **Props (Card)** | `variant` (elevated, bordered, flat, interactive), `padding` (none, sm, md, lg), `as` (polymorphic — `<a>`, `<button>`, `<article>`), `hoverable` (boolean — lift on hover), `onClick` |
| **Props (Header/Body/Footer)** | `padding` (inherit or override) |
| **Description** | Composable card container for content sections. Interactive variant supports hover/focus styles and ClickableCard mode. |
| **States** | default, hover (interactive), focus-visible, active (interactive) |
| **Accessibility** | `aria-label` when card is a single interactive element; role changes based on `as` prop |
| **Usage** | `<Card variant="elevated" padding="md"><Card.Header><Heading>Product</Heading></Card.Header><Card.Body>...</Card.Body><Card.Footer>...</Card.Footer></Card>` |

### Modal / Dialog

| Aspect | Details |
|--------|---------|
| **Component** | `<Modal>`, `<Modal.Trigger>`, `<Modal.Overlay>`, `<Modal.Content>`, `<Modal.Header>`, `<Modal.Body>`, `<Modal.Footer>`, `<Modal.Close>` |
| **Props (Modal)** | `open`, `defaultOpen`, `onOpenChange`, `size` (sm, md, lg, xl, fullscreen), `closeOnOverlayClick`, `closeOnEscape`, `preventScroll` (locks body scroll), `initialFocusRef`, `finalFocusRef`, `trapFocus` (boolean) |
| **Props (Overlay)** | `blur` (boolean for backdrop blur), `dismissible` |
| **Description** | Accessible modal dialog with focus trapping, scroll locking, and animated enter/exit (`AnimatePresence`). Compound structure gives full layout flexibility. |
| **States** | closed, opening (animate in), open, closing (animate out) |
| **Accessibility** | `role="dialog"`; `aria-modal="true"`; `aria-labelledby` (Header) and `aria-describedby` (Body); focus trap on open; return focus on close; Escape dismisses unless `closeOnEscape` is false |
| **Usage** | `<Modal open={isOpen} onOpenChange={setIsOpen} size="md"><Modal.Overlay /><Modal.Content><Modal.Header><Modal.Title>Confirm</Modal.Title></Modal.Header><Modal.Body>...</Modal.Body><Modal.Footer>...</Modal.Footer></Modal.Content></Modal>` |

### DropdownMenu

| Aspect | Details |
|--------|---------|
| **Component** | `<DropdownMenu>`, `<DropdownMenu.Trigger>`, `<DropdownMenu.Content>`, `<DropdownMenu.Item>`, `<DropdownMenu.Divider>`, `<DropdownMenu.Label>`, `<DropdownMenu.Sub>`, `<DropdownMenu.CheckboxItem>`, `<DropdownMenu.RadioGroup>` |
| **Props (Content)** | `align` (start, center, end), `side` (bottom, top, left, right), `sideOffset` (number), `alignOffset` (number), `collisionPadding` |
| **Props (Item)** | `disabled`, `icon` (Lucide icon), `inset` (boolean — indented for icon alignment), `shortcut` (string — e.g. "⌘K"), `destructive` (boolean — red styling) |
| **Description** | Full-featured dropdown menu with submenus, dividers, labels, checkbox items, and radio groups. Animates on open/close. |
| **States** | closed, opening, open, item-default, item-hover, item-disabled, item-destructive |
| **Accessibility** | `role="menu"`; `role="menuitem"`; `aria-disabled`; keyboard navigation (arrow keys, Enter, Escape); pointer-leave handling to close submenus with delay |
| **Usage** | `<DropdownMenu><DropdownMenu.Trigger><Button>Actions</Button></DropdownMenu.Trigger><DropdownMenu.Content><DropdownMenu.Item icon={Edit}>Edit</DropdownMenu.Item><DropdownMenu.Divider /><DropdownMenu.Item destructive icon={Trash}>Delete</DropdownMenu.Item></DropdownMenu.Content></DropdownMenu>` |

### Tabs

| Aspect | Details |
|--------|---------|
| **Component** | `<Tabs>`, `<Tabs.List>`, `<Tabs.Trigger>`, `<Tabs.Content>` |
| **Props (Tabs)** | `value` (controlled), `defaultValue`, `onValueChange`, `variant` (underline, pill, segmented, outlined), `orientation` (horizontal, vertical), `activationMode` (automatic — click/focus moves selection, manual — only click moves) |
| **Props (Trigger)** | `value`, `disabled`, `icon` (Lucide icon), `badge` (ReactNode — a `<Badge>`), `badgePosition` (right, top) |
| **Description** | Tab navigation with content panels. Supports icon and badge on triggers, vertical orientation, and segmented style. |
| **States** | inactive, active, hover, focus-visible, disabled |
| **Accessibility** | `role="tablist"`; triggers have `role="tab"` with `aria-selected` and `aria-controls`; content panels have `role="tabpanel"` with `aria-labelledby`; keyboard navigation via arrow keys (automatic mode) or arrow keys + Enter (manual mode) |
| **Usage** | `<Tabs defaultValue="description"><Tabs.List><Tabs.Trigger value="description">Description</Tabs.Trigger><Tabs.Trigger value="reviews" badge={<Badge>12</Badge>}>Reviews</Tabs.Trigger></Tabs.List><Tabs.Content value="description">...</Tabs.Content></Tabs>` |

### Breadcrumb

| Aspect | Details |
|--------|---------|
| **Component** | `<Breadcrumb>`, `<Breadcrumb.Item>`, `<Breadcrumb.Link>`, `<Breadcrumb.Separator>` |
| **Props (Breadcrumb)** | `maxItems` (number — truncates with ellipsis when exceeded), `expand` (boolean or ReactNode — shows "+N more" button), `separator` (ReactNode — default chevron, customizable to `/` or `→`) |
| **Props (Item)** | `href` (optional, current page omits link), `isCurrentPage` (boolean — `aria-current="page"`) |
| **Description** | Hierarchical breadcrumb navigation with truncation support for deep paths. |
| **States** | default, hover (link), current (bold, not clickable), collapsed (ellipsis) |
| **Accessibility** | `nav` with `aria-label="Breadcrumb"`; `aria-current="page"` on last item; `aria-hidden` on separator |
| **Usage** | `<Breadcrumb maxItems={3}><Breadcrumb.Item href="/">Home</Breadcrumb.Item><Breadcrumb.Item href="/products">Products</Breadcrumb.Item><Breadcrumb.Item isCurrentPage>Electronics</Breadcrumb.Item></Breadcrumb>` |

### Pagination

| Aspect | Details |
|--------|---------|
| **Component** | `<Pagination>`, `<Pagination.Prev>`, `<Pagination.Next>`, `<Pagination.PageButton>`, `<Pagination.Ellipsis>`, `<Pagination.PageSizeSelect>` |
| **Props (Pagination)** | `currentPage`, `totalPages`, `onPageChange`, `siblingCount` (number of page buttons on each side of current — default 1), `boundaryCount` (number of page buttons at start/end — default 1), `showFirst`/`showLast` (boolean for first/last buttons), `size` (sm, md, lg) |
| **Props (PageSizeSelect)** | `pageSize` (current), `pageSizes` (array of numbers), `onPageSizeChange` |
| **Description** | Page navigation with ellipsis for large ranges, optional page size selector, and first/last quick-jump buttons. |
| **States** | default, hover, active (current page), disabled (prev on first page, next on last) |
| **Accessibility** | `nav` with `aria-label="Pagination"`; current page has `aria-current="page"`; prev/next have `aria-label="Previous page"` / `aria-label="Next page"` |
| **Usage** | `<Pagination currentPage={1} totalPages={25} onPageChange={setPage} siblingCount={2} />` |

### Tooltip

| Aspect | Details |
|--------|---------|
| **Component** | `<Tooltip>`, `<Tooltip.Trigger>`, `<Tooltip.Content>` (also `<Tooltip.Arrow>`) |
| **Props (Tooltip)** | `content` (ReactNode — the tooltip text/content), `side` (top, bottom, left, right), `align` (start, center, end), `sideOffset` (number, default 4), `delayDuration` (ms — default 700 for show, 300 for hide), `skipDelayDuration` (ms — reduces delay on quick successive triggers), `maxWidth` (number — default 220px), `open`/`defaultOpen`/`onOpenChange` (controlled), `disabled` (boolean) |
| **Description** | Floating label that appears on hover/focus. Uses minimal delay to avoid flicker on incidental mouse movement. |
| **States** | closed, opening (delay), open, closing |
| **Accessibility** | Trigger has `aria-describedby` pointing to tooltip content; `role="tooltip"`; keyboard accessible via focus; respects `prefers-reduced-motion` to disable animation |
| **Usage** | `<Tooltip content="Add to wishlist" side="top"><button><Heart /></button></Tooltip>` |

### Toast

| Aspect | Details |
|--------|---------|
| **Component** | `<Toast>`, `<Toast.Title>`, `<Toast.Description>`, `<Toast.Close>`, `<Toast.Action>`, `<ToastProvider>`, `<ToastViewport>` |
| **Props (Toast)** | `type` (success, error, warning, info, loading), `duration` (ms — default 5000, 0 for persistent), `dismissible` (boolean, default true), `swipeDirection` (right, left, up, down — for swipe-to-dismiss), `onOpenChange`, `open` |
| **Props (Action)** | `altText` (string — required for screen readers), `onClick`, `asChild` |
| **Description** | Notification toast with auto-dismiss, swipe-to-dismiss, and stack management via `ToastProvider`. Loading type persists until manually dismissed or updated. |
| **States** | entering (slide-in animation), visible, dismissing (swipe or timeout), exited |
| **Accessibility** | `role="status"` (or `role="alert"` for errors); `aria-live="polite"` (or `"assertive"` for errors); swipe action is non-essential (content still visible) |
| **Usage** | `<Toast type="success"><Toast.Title>Product added</Toast.Title><Toast.Description>Item is in your cart</Toast.Description></Toast>` |

### Alert

| Aspect | Details |
|--------|---------|
| **Component** | `<Alert>`, `<Alert.Title>`, `<Alert.Description>`, `<Alert.Icon>`, `<Alert.Action>` |
| **Props (Alert)** | `type` (info, success, warning, error, neutral), `dismissible` (boolean), `onDismiss`, `icon` (Lucide icon — defaults per type), `action` (ReactNode — button / link) |
| **Description** | In-page notification banner. Can be dismissible (animated out) or persistent. |
| **States** | default, dismissing (slide/fade out), dismissed |
| **Accessibility** | `role="alert"` for error/warning; `role="status"` for info/success; `aria-live` accordingly; close button has `aria-label="Dismiss"` |
| **Usage** | `<Alert type="warning" dismissible><Alert.Title>Low stock</Alert.Title><Alert.Description>Only 3 units remaining</Alert.Description></Alert>` |

### Skeleton

| Aspect | Details |
|--------|---------|
| **Component** | `<Skeleton>`, `<Skeleton.Text>`, `<Skeleton.Circle>`, `<Skeleton.Card>`, `<Skeleton.Table>` |
| **Props (Skeleton)** | `variant` (text, circle, card, table, custom), `width` / `height` (CSS values), `lines` (number — for text variant), `lineHeight` (default `1rem`), `rounded` (full, md, lg, etc.), `speed` (animation speed — default 1.5s), `as` (div or span for inline) |
| **Description** | Loading placeholder with shimmer animation. Preset shapes for common patterns (text block, avatar circle, product card, table row). |
| **States** | loading (shimmer visible) |
| **Accessibility** | `aria-busy="true"`; `aria-label="Loading..."`; prefers `prefers-reduced-motion` to show static placeholder |
| **Usage** | `<Skeleton.Text lines={3} />` or `<Skeleton.Card />` |

### ProgressBar

| Aspect | Details |
|--------|---------|
| **Component** | `<ProgressBar>` |
| **Props** | `value` (0–100, or `null` for indeterminate), `size` (sm, md, lg), `variant` (default, success, warning, error, gradient), `showLabel` (boolean — percentage text), `labelPosition` (inside, right, bottom), `animated` (boolean — stripe animation), `rounded` (boolean, default true), `indeterminate` (boolean — infinite animation when value unknown), `max` (number — default 100) |
| **Description** | Horizontal progress indicator. Supports determinate (percentage) and indeterminate (animated bar) modes. |
| **States** | empty (0%), partial, complete (100%), indeterminate, error (stops at current value with error color) |
| **Accessibility** | `role="progressbar"`; `aria-valuenow` (determinate), `aria-valuemin="0"`, `aria-valuemax={max}`; `aria-label` when no visible label |
| **Usage** | `<ProgressBar value={65} showLabel variant="success" size="lg" />` |

### Accordion

| Aspect | Details |
|--------|---------|
| **Component** | `<Accordion>`, `<Accordion.Item>`, `<Accordion.Trigger>`, `<Accordion.Content>` |
| **Props (Accordion)** | `type` (single — one open at a time, multiple — multiple open), `value`/`defaultValue` (controlled — string for single, string[] for multiple), `onValueChange`, `collapsible` (single only — allows closing all), `compact` (boolean — reduced padding), `variant` (outlined, ghost, bordered) |
| **Props (Trigger)** | `icon` (Lucide icon, or default chevron), `iconPosition` (left, right), `hideIcon` (boolean) |
| **Description** | Vertically stacked collapsible sections. Supports single or multi-open modes. Animated expand/collapse via `AnimatePresence`. |
| **States** | closed, opening (animate), open, closing (animate), disabled (item) |
| **Accessibility** | Trigger is a `<button>` with `aria-expanded` and `aria-controls`; content has `role="region"` with `aria-labelledby`; keyboard via Enter/Space to toggle |
| **Usage** | `<Accordion type="single" collapsible><Accordion.Item value="shipping"><Accordion.Trigger>Shipping Info</Accordion.Trigger><Accordion.Content>...</Accordion.Content></Accordion.Item></Accordion>` |

### Table

| Aspect | Details |
|--------|---------|
| **Component** | `<Table>`, `<Table.Header>`, `<Table.Body>`, `<Table.Row>`, `<Table.Head>`, `<Table.Cell>`, `<Table.Caption>`, `<Table.Footer>` |
| **Props (Table)** | `variant` (bordered, striped, unstriped, grid), `size` (sm, md, lg), `stickyHeader` (boolean), `highlightOnHover` (boolean), `responsive` (boolean — horizontal scroll on mobile) |
| **Props (Head — sortable)** | `sortable` (boolean), `sortDirection` (asc, desc, none), `onSort`, `sortLabel` (aria label prefix) |
| **Props (Row — selectable)** | `selected` (boolean), `onSelect`, `disabled` |
| **Description** | Semantic HTML table with sortable headers, row selection, striped rows, and responsive overflow. |
| **States** | default, hover (row), active (sort), selected, striped |
| **Accessibility** | Full `<table>` semantics; `aria-sort` on sortable headers; `aria-selected` on rows; `scope="col"`/`scope="row"` on headers; `<caption>` for title; sticky header uses `position: sticky` with `z-index` |
| **Usage** | `<Table variant="striped"><Table.Header><Table.Head sortable sortDirection="asc" onSort={handleSort}>Price</Table.Head></Table.Header><Table.Body>...</Table.Body></Table>` |

### Tabs (Segmented alternative)

| Aspect | Details |
|--------|---------|
| **Component** | `<SegmentedControl>` |
| **Props** | `value`, `defaultValue`, `onValueChange`, `options` (`Array<{ value, label, icon?, disabled? }>`), `size` (sm, md, lg), `fullWidth` (boolean) |
| **Description** | Segmented button group (iOS-style). Compact alternative to underlined tabs for 2–4 options. |
| **States** | inactive, active, hover, disabled |
| **Accessibility** | `role="radiogroup"`; each option has `role="radio"` with `aria-checked`; keyboard via arrow keys |
| **Usage** | `<SegmentedControl options={[{value:"grid",icon:Grid},{value:"list",icon:List}]} />` |

### Drawer

| Aspect | Details |
|--------|---------|
| **Component** | `<Drawer>`, `<Drawer.Overlay>`, `<Drawer.Content>`, `<Drawer.Header>`, `<Drawer.Body>`, `<Drawer.Footer>`, `<Drawer.Close>` |
| **Props (Drawer)** | `open`, `onOpenChange`, `side` (left, right, top, bottom), `size` (sm, md, lg, xl, or specific width/height via CSS), `closeOnOverlayClick`, `closeOnEscape`, `preventScroll`, `trapFocus` |
| **Description** | Slide-in panel from any edge. Supports overlay dimming, focus trapping, and scroll locking. |
| **States** | closed, entering (slide-in), open, exiting (slide-out) |
| **Accessibility** | `role="dialog"`; `aria-modal="true"`; same pattern as Modal for labelling and focus management |
| **Usage** | `<Drawer side="right" size="md" open={isCartOpen} onOpenChange={setCartOpen}><Drawer.Content>...</Drawer.Content></Drawer>` |

### Popover

| Aspect | Details |
|--------|---------|
| **Component** | `<Popover>`, `<Popover.Trigger>`, `<Popover.Content>`, `<Popover.Arrow>`, `<Popover.Close>` |
| **Props (Popover)** | `open`, `defaultOpen`, `onOpenChange`, `side` (top, bottom, left, right), `align` (start, center, end), `sideOffset` (number), `alignOffset` (number), `collisionPadding`, `arrow` (boolean), `arrowWidth`/`arrowHeight` (number), `matchTriggerWidth` (boolean) |
| **Description** | Floating panel that appears on trigger click. Unlike Tooltip (hover), Popover is click-activated and interactive (content can contain form elements). |
| **States** | closed, open, closing |
| **Accessibility** | `aria-haspopup="dialog"` on trigger; `aria-expanded`; `role="dialog"` on Content; focus trap when open; Escape to close |
| **Usage** | `<Popover><Popover.Trigger><Button variant="outline">Filter</Button></Popover.Trigger><Popover.Content><Popover.Arrow />...</Popover.Content></Popover>` |

### Command / Keyboard Shortcut

| Aspect | Details |
|--------|---------|
| **Component** | `<Kbd>` |
| **Props** | `keys` (string[] — e.g. `["⌘", "K"]` or `["Ctrl", "S"]`), `size` (sm, md), `variant` (default, outline, ghost) |
| **Description** | Inline keyboard shortcut display. Renders a `<kbd>` element with styled key caps separated by plus signs. |
| **States** | default |
| **Accessibility** | `<kbd>` element; `aria-label` constructed automatically ("Command plus K"); visual keys are presentational |
| **Usage** | `<Kbd keys={["⌘", "K"]} />` → renders as ⌘ + K |

---

## 3. Form Components (Molecules)

### FormField

| Aspect | Details |
|--------|---------|
| **Component** | `<FormField>` |
| **Props** | `name` (string — used for id generation and error mapping), `label` (ReactNode), `required` (boolean — adds asterisk), `error` (string — error message, sets `aria-invalid` on child), `helperText` (string — additional guidance), `hint` (string — inline hint below field), `children` (ReactNode — the input component), `layout` (vertical, horizontal — label beside input) |
| **Description** | Form field wrapper that connects label, input, error, and helper text via `aria-describedby`. Automatically generates `id` from `name`. |
| **Accessibility** | `aria-labelledby` on input from label; `aria-describedby` from error/helper; `aria-required="true"` when required; error has `role="alert"` |
| **Usage** | `<FormField name="email" label="Email" required error={errors.email}><Input type="email" /></FormField>` |

### FormSelect, FormTextarea, FormCheckbox, FormRadioGroup

Each follows the same pattern as FormField. Pre-wired combinations of label + field + error for convenience:

| Component | Inner element | Extra props |
|-----------|---------------|-------------|
| `<FormSelect>` | `<Select>` | `options`, `placeholder`, `searchable` |
| `<FormTextarea>` | `<Textarea>` | `maxLength`, `showCharCount`, `rows` |
| `<FormCheckbox>` | `<Checkbox>` | `checked`, `onCheckedChange`, group mode with `options` array |
| `<FormRadioGroup>` | `<RadioGroup>` | `options` array of `{ value, label }`, `orientation` |
| `<FormDatePicker>` | `<DatePicker>` | `mode` (single, range, time), `minDate`, `maxDate`, `locale` |
| `<FormFileUpload>` | `<FileUploader>` | `accept`, `maxSize`, `maxFiles`, `multiple` |
| `<FormPhoneInput>` | `<PhoneInput>` | `defaultCountry`, `countries` (whitelist) |
| `<FormRichTextEditor>` | `<RichEditor>` | `toolbar` (customizable toolbar items), `placeholder` |
| `<FormColorPicker>` | `<ColorPicker>` | `swatches`, `allowCustom` |
| `<FormAutocomplete>` | `<Autocomplete>` | `options`, `onSearch` (async), `debounceMs`, `loading`, `minChars` |

---

## 4. Layout Components

### Container

| Aspect | Details |
|--------|---------|
| **Component** | `<Container>` |
| **Props** | `size` (sm — 640px, md — 768px, lg — 1024px, xl — 1280px, fluid — 100%), `centered` (boolean — auto horizontal margins), `padding` (boolean or CSS token) |
| **Description** | Max-width wrapper that centers content. Used as top-level page layout constraint. |
| **Usage** | `<Container size="lg"> ... </Container>` |

### Grid

| Aspect | Details |
|--------|---------|
| **Component** | `<Grid>` |
| **Props** | `cols` (responsive object — `{ base: 1, sm: 2, md: 3, lg: 4 }` or number), `gap` (CSS gap token — `4`, `6`, `8`, etc.), `alignItems`, `justifyContent`, `as` |
| **Description** | CSS Grid wrapper with responsive column definitions via Tailwind breakpoint object. |
| **Usage** | `<Grid cols={{ base: 1, md: 2, lg: 3 }} gap={6}> ... </Grid>` |

### Flex

| Aspect | Details |
|--------|---------|
| **Component** | `<Flex>` |
| **Props** | `direction` (row, column, row-reverse, column-reverse), `align` (flex-start, center, flex-end, stretch, baseline), `justify` (flex-start, center, flex-end, between, around, evenly), `gap` (CSS gap token), `wrap` (boolean), `as` |
| **Description** | Flexbox layout utility component. |
| **Usage** | `<Flex align="center" justify="between" gap={4}> ... </Flex>` |

### Stack

| Aspect | Details |
|--------|---------|
| **Component** | `<Stack>` |
| **Props** | `orientation` (vertical, horizontal), `spacing` (CSS gap token — `1` through `16`), `divider` (boolean or ReactNode — renders a `<Divider>` between children), `as` |
| **Description** | Arranges children with consistent spacing. Shorthand for Flex with `gap` and predictable direction. |
| **Usage** | `<Stack spacing={4} divider> ... </Stack>` |

### SplitPane

| Aspect | Details |
|--------|---------|
| **Component** | `<SplitPane>` |
| **Props** | `defaultSize` (number — default width of first pane in px or %), `minSize` (number), `maxSize` (number), `direction` (horizontal, vertical), `resizable` (boolean), `onResize`, `snap` (array of pixel positions for snap points), `primary` (first, second — which pane grows on resize) |
| **Description** | Two-panel layout with a draggable divider. Supports snap points, min/max constraints, and vertical orientation. |
| **Accessibility** | `role="separator"` on divider bar, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`; keyboard resize via arrow keys |
| **Usage** | `<SplitPane defaultSize={300} minSize={200} maxSize={600}> <Sidebar /> <Main /> </SplitPane>` |

### PageHeader

| Aspect | Details |
|--------|---------|
| **Component** | `<PageHeader>`, `<PageHeader.Title>`, `<PageHeader.Description>`, `<PageHeader.Actions>` |
| **Props (PageHeader)** | `title` (string), `description` (string), `actions` (ReactNode — button group), `breadcrumb` (ReactNode — `<Breadcrumb>`), `separator` (boolean — divider below header), `backButton` (boolean or callback), `onBack` |
| **Description** | Page-level header with title, description, breadcrumb, back button, and action slot. |
| **Usage** | `<PageHeader title="Products" description="Manage your inventory" actions={<Button>Add Product</Button>} breadcrumb={<Breadcrumb />} />` |

### Section

| Aspect | Details |
|--------|---------|
| **Component** | `<Section>` |
| **Props** | `heading` (string or ReactNode), `headingLevel` (h1–h6), `description` (string), `actions` (ReactNode), `spacing` (top/bottom padding — sm, md, lg), `variant` (default, bordered, card) |
| **Description** | Content section with semantic heading, optional actions toolbar, and consistent spacing. |
| **Usage** | `<Section heading="Order Details" spacing="lg"> ... </Section>` |

### Divider

| Aspect | Details |
|--------|---------|
| **Component** | `<Divider>` |
| **Props** | `orientation` (horizontal, vertical), `label` (string — centered text aka "or"), `labelPosition` (left, center, right), `variant` (solid, dashed, dotted), `size` (thin, medium, thick) |
| **Description** | Visual separator line, optionally with centered label. |
| **Usage** | `<Divider label="or" />` |

---

## 5. Navigation Components

### TopNav

| Aspect | Details |
|--------|---------|
| **Component** | `<TopNav>`, `<TopNav.Logo>`, `<TopNav.Link>`, `<TopNav.Dropdown>`, `<TopNav.Actions>`, `<TopNav.MobileMenu>` |
| **Props (TopNav)** | `variant` (default, transparent, sticky, fixed), `logo` (ReactNode — image + text), `links` (array of navigation items), `actions` (ReactNode — cart, profile, notification icons), `mobileBreakpoint` (string — default `"md"`) |
| **Description** | Top navigation bar with logo, links, dropdowns, action icons, and responsive mobile hamburger menu. |
| **Accessibility** | `<nav>` with `aria-label="Main"`; mobile menu has `aria-expanded`; hamburger button has `aria-label="Open menu"` |
| **Usage** | `<TopNav logo={<Image src="/logo.svg" />} links={navItems} actions={<CartIcon />} />` |

### Sidebar

| Aspect | Details |
|--------|---------|
| **Component** | `<Sidebar>`, `<Sidebar.Item>`, `<Sidebar.Submenu>`, `<Sidebar.Group>`, `<Sidebar.Footer>`, `<Sidebar.Toggle>` |
| **Props (Sidebar)** | `collapsed` (boolean — icon-only mode), `onToggle`, `defaultCollapsed`, `items` (array of navigation items with nested children), `activePath` (string — current route for highlight), `variant` (default, compact, floating), `header` (ReactNode), `footer` (ReactNode) |
| **Description** | Collapsible vertical navigation with nested submenus, group labels, and active path highlighting. |
| **Accessibility** | `<nav>` with `aria-label="Sidebar"`; toggle button has `aria-label="Collapse sidebar"`; `aria-expanded` on submenu triggers; `aria-current="page"` on active item |
| **Usage** | `<Sidebar collapsed={isCollapsed} activePath="/dashboard" items={menuItems} />` |

### BreadcrumbNav

| Aspect | Details |
|--------|---------|
| **Component** | `<BreadcrumbNav>` |
| **Props** | `path` (string — current URL path like `/products/electronics/phones`), `homeLabel` (string — default "Home"), `homeHref` (string — default "/"), `separator` (ReactNode), `maxItems` (number), `mapping` (record of path segments to labels — `{ products: "Products", electronics: "Electronics" }`) |
| **Description** | Auto-generates breadcrumb from URL path with label mapping and truncation. |
| **Usage** | `<BreadcrumbNav path={pathname} mapping={routeLabels} maxItems={4} />` |

### MobileNav

| Aspect | Details |
|--------|---------|
| **Component** | `<MobileNav>` |
| **Props** | `open`, `onOpenChange`, `items` (navigation items), `logo`, `footer` |
| **Description** | Full-screen drawer navigation for mobile viewports. Overlays content with close button and link list. |
| **Usage** | `<MobileNav open={isMobileOpen} onOpenChange={setMobileOpen} items={navItems} />` |

### TabNav

| Aspect | Details |
|--------|---------|
| **Component** | `<TabNav>` |
| **Props** | `items` (array of `{ value, label, icon?, badge?, href? }`), `value`/`defaultValue`/`onValueChange`, `scrollable` (boolean — horizontal scroll on overflow), `variant` (underline, pill) |
| **Description** | Horizontal tab navigation for page-level sections. Scrollable when tabs overflow. |
| **Usage** | `<TabNav items={[{value:'all',label:'All'},{value:'active',label:'Active'}]} />` |

### StepNav (Wizard)

| Aspect | Details |
|--------|---------|
| **Component** | `<StepNav>`, `<StepNav.Step>` |
| **Props (StepNav)** | `currentStep` (number — 0-indexed), `steps` (array of `{ label, description?, icon? }`), `orientation` (horizontal, vertical), `variant` (numbered, icon, dot), `onStepClick` (optional — allows clicking completed steps) |
| **Description** | Multi-step progress indicator for checkout/onboarding wizards. Shows completed, current, and upcoming steps. |
| **States** | completed (green checkmark), current (highlighted), upcoming (dimmed), error (step with validation error) |
| **Accessibility** | `aria-current="step"` on current step; completed steps have `aria-label="Step {n}: completed"`; `<ol>` / `<li>` structure |
| **Usage** | `<StepNav currentStep={2} steps={["Cart", "Shipping", "Payment", "Confirm"]} />` |

### BottomNav

| Aspect | Details |
|--------|---------|
| **Component** | `<BottomNav>`, `<BottomNav.Item>` |
| **Props (BottomNav)** | `items` (array of `{ value, label, icon, href?, badge? }`), `value`/`defaultValue`/`onValueChange`, `variant` (default, compact — label only on active) |
| **Description** | Mobile bottom navigation bar with icon + label. Typically visible on screens smaller than `md`. |
| **Accessibility** | `<nav>` with `aria-label="Bottom navigation"`; `aria-current="page"` on active item |
| **Usage** | `<BottomNav items={[{value:'home',icon:Home,label:'Home'},{value:'search',icon:Search,label:'Search'}]} />` |

### PaginationNav

| Aspect | Details |
|--------|---------|
| **Component** | `<PaginationNav>` |
| **Props** | Same as `<Pagination>` above. Alias for page-navigation-specific use. |
| **Description** | Dedicated page navigation component wrapping the base Pagination with simplified API for route-based navigation (accepts `buildHref` function for SEO-friendly links). |
| **Usage** | `<PaginationNav currentPage={page} totalPages={total} buildHref={(p) => `/products?page=${p}`} />` |

---

## 6. Data Display Components

### DataTable

| Aspect | Details |
|--------|---------|
| **Component** | `<DataTable<T>>`, `<DataTable.Column>`, `<DataTable.Body>`, `<DataTable.Pagination>`, `<DataTable.Toolbar>`, `<DataTable.Filter>` |
| **Props (DataTable)** | `data` (T[]), `columns` (array of `ColumnDef<T>` — accessor key, header, cell render, sortable, filterable, width, align), `sortable` (boolean or per-column), `filterable` (boolean), `onRowClick`, `selectedRows` / `onSelectedRowsChange` (Set or array), `pageSize`, `page`, `total`, `onPageChange`, `onPageSizeChange`, `loading`, `emptyMessage`, `pagination` (boolean), `columnVisibility` (object — `{ columnKey: true/false }`), `onColumnVisibilityChange`, `exportable` (boolean — CSV/Excel export), `density` (compact, comfortable, spacious) |
| **Description** | Full-featured data table with sorting, filtering, pagination, row selection, column visibility toggle, and export. Generic type `T` provides full type safety. Sort/filter state can be server-driven or client-side. |
| **States** | loading (skeleton rows), empty, error, populated, sorting (active sort indicator), filtering (active filter indicators), selected (highlighted rows) |
| **Accessibility** | `<table>` with full ARIA; sortable headers use `<button>` with `aria-sort`; `aria-selected` on rows; `aria-rowcount` / `aria-colcount` when virtualized; live region for sort/filter announcements |
| **Usage** | `<DataTable data={products} columns={columns} sortable paginate exportable />` |

### DataGrid

| Aspect | Details |
|--------|---------|
| **Component** | `<DataGrid<T>>` |
| **Props** | `data` (T[]), `columns` (similar to DataTable but with `editable` per column), `editable` (boolean — inline cell editing), `onCellEdit` (callback — `(rowIndex, columnKey, value) => void`), `virtualize` (boolean — uses react-window for large datasets), `rowHeight` (number), `overscanCount`, `sortable`, `filterable`, `onScroll` (for infinite scroll) |
| **Description** | Spreadsheet-like grid with inline editing, virtualization for large data sets, and all DataTable features. Target use: seller inventory management, order processing. |
| **States** | Same as DataTable + editing (cell in edit mode with input), validation-error (cell shows error state) |
| **Accessibility** | `role="grid"`; `aria-readonly="false"` when editable; `aria-multiselectable`; cell edit triggers |
| **Usage** | `<DataGrid data={inventory} columns={cols} editable virtualize rowHeight={48} />` |

### ProductCard

| Aspect | Details |
|--------|---------|
| **Component** | `<ProductCard>`, `<ProductCard.Image>`, `<ProductCard.Title>`, `<ProductCard.Price>`, `<ProductCard.Rating>`, `<ProductCard.Seller>`, `<ProductCard.Badges>`, `<ProductCard.Actions>` |
| **Props (ProductCard)** | `product` (Product object), `variant` (grid, list), `aspectRatio` (1:1, 4:3, 3:2), `onClick`, `onAddToCart`, `onToggleWishlist`, `wishlisted` (boolean), `showSeller`, `showRating`, `badges` (array of badge props — sale, new, low-stock), `imageSizes` (for responsive `<Image>`) |
| **Description** | Product card for grid/list views. Composable from card atoms. Supports multiple image aspect ratios and hover overlay actions. |
| **States** | default, hover (lift + shadow), image-loading (skeleton), wishlist-toggling (heart animation), out-of-stock (dimmed + overlay) |
| **Accessibility** | `aria-label` from product name; key actions (add to cart, wishlist) have accessible labels; price formatted with `aria-label` |
| **Usage** | `<ProductCard product={product} variant="grid" onAddToCart={handleAdd} wishlisted={isWishlisted} />` |

### OrderCard

| Aspect | Details |
|--------|---------|
| **Component** | `<OrderCard>`, `<OrderCard.Header>`, `<OrderCard.Items>`, `<OrderCard.Total>`, `<OrderCard.Status>`, `<OrderCard.Actions>` |
| **Props (OrderCard)** | `order` (Order object — id, items, total, status, date, seller), `onViewDetails`, `onTrack`, `onCancel`, `compact` (boolean) |
| **Description** | Order summary card for order history. Shows item thumbnails, status badge, total, and action buttons. |
| **States** | default, expanded, cancelled (dimmed) |
| **Usage** | `<OrderCard order={order} onTrack={handleTrack} />` |

### SellerCard

| Aspect | Details |
|--------|---------|
| **Component** | `<SellerCard>` |
| **Props** | `seller` (object — `{ name, logo, rating, totalSales, responseTime, verified }`), `onClick`, `size` (sm, md, lg), `showStats` (boolean) |
| **Description** | Seller profile card with logo, name, rating stars, sales count, response time, and verified badge. |
| **Usage** | `<SellerCard seller={seller} showStats />` |

### ReviewCard

| Aspect | Details |
|--------|---------|
| **Component** | `<ReviewCard>` |
| **Props** | `review` (object — `{ user, rating, text, date, images? }`), `onHelpful` (callback), `helpfulCount` (number), `markedHelpful` (boolean), `maxLength` (number — truncate + "Read more") |
| **Description** | Customer review display with user avatar, star rating, date, text (expandable), images, and helpful vote button. |
| **States** | collapsed (truncated text), expanded (full text) |
| **Usage** | `<ReviewCard review={review} onHelpful={markHelpful} helpfulCount={12} />` |

### PriceDisplay

| Aspect | Details |
|--------|---------|
| **Component** | `<PriceDisplay>` |
| **Props** | `amount` (number), `originalAmount` (number — for sale comparison), `currency` (string — default "BDT"), `locale` (string — default "bn-BD"), `size` (sm, md, lg, xl), `variant` (default, sale, strikethrough, free), `discount` (boolean — shows discount percentage), `perUnit` (string — "/kg", "/piece"), `suffix` (string — "excl. VAT") |
| **Description** | Price display with formatted currency, optional original/sale price comparison, discount badge, and unit suffix. |
| **Usage** | `<PriceDisplay amount={1250} originalAmount={1500} discount size="lg" />` |

### RatingStars

| Aspect | Details |
|--------|---------|
| **Component** | `<RatingStars>` |
| **Props** | `rating` (number — 0–5), `maxStars` (default 5), `size` (sm, md, lg), `interactive` (boolean — allows clicking to set rating), `onRate` (callback — `(rating: number) => void`), `showValue` (boolean — display number next to stars), `halfStars` (boolean — allow 0.5 increments), `precision` (0.5 or 1) |
| **Description** | Star rating display and input. Supports fractional stars and interactive mode for submitting ratings. |
| **States** | display (static), interactive (hover preview, click to set), set (current value shown) |
| **Accessibility** | `role="img"` with `aria-label="Rating: 4 out of 5 stars"`; interactive uses `role="radiogroup"` with `role="radio"` per star; keyboard via arrow keys when interactive |
| **Usage** | `<RatingStars rating={4.5} halfStars interactive onRate={setRating} size="lg" />` |

### MetricCard

| Aspect | Details |
|--------|---------|
| **Component** | `<MetricCard>` |
| **Props** | `label` (string), `value` (string or number), `trend` (number — percentage change), `trendDirection` (up, down, neutral), `icon` (Lucide icon component), `variant` (default, success, warning, danger), `format` (currency, number, percentage), `prefix`/`suffix` (string), `sparkline` (data points array for mini chart), `onClick`, `loading` (boolean — show skeleton) |
| **Description** | Dashboard metric card with label, formatted value, trend indicator, icon, and optional sparkline chart. |
| **States** | default (showing data), loading (skeleton placeholder), trend-up, trend-down, trend-neutral |
| **Usage** | `<MetricCard label="Revenue" value={125000} trend={12.5} trendDirection="up" icon={DollarSign} format="currency" />` |

### Timeline

| Aspect | Details |
|--------|---------|
| **Component** | `<Timeline>`, `<Timeline.Item>`, `<Timeline.Icon>`, `<Timeline.Content>`, `<Timeline.Date>`, `<Timeline.Title>` |
| **Props (Timeline)** | `items` (array of `{ date, title, description?, status?, icon? }`), `orientation` (vertical, horizontal), `variant` (default, dotted, outlined), `activeStep` (number for progress highlighting) |
| **Description** | Vertical or horizontal timeline for order tracking, shipment status, or activity logs. |
| **States** | completed, current, upcoming, error |
| **Accessibility** | `aria-label` via `role="list"` structure; status icons have `aria-label` |
| **Usage** | `<Timeline items={orderEvents} orientation="vertical" />` |

### TreeView

| Aspect | Details |
|--------|---------|
| **Component** | `<TreeView>`, `<TreeView.Node>`, `<TreeView.Leaf>` |
| **Props (TreeView)** | `data` (nested nodes), `defaultExpanded` (string[] — node ids), `selected` (string — node id), `onSelect`, `onToggle`, `selectable` (boolean), `icons` (object — per-level or per-type icons), `indent` (number — px per level) |
| **Description** | Hierarchical tree for category navigation, folder structures, or organizational charts. |
| **States** | collapsed, expanded, selected, hover, leaf, branch |
| **Accessibility** | `role="tree"`, `role="treeitem"`, `aria-expanded`, `aria-selected`, `aria-level`; keyboard via arrow keys, Enter, Space |
| **Usage** | `<TreeView data={categories} selectable onSelect={setCategory} />` |

---

## 7. Feedback Components

### ToastContainer

| Aspect | Details |
|--------|---------|
| **Component** | `<ToastContainer>` (rendered once at app root, manages visible toasts as a stack) |
| **Props** | `position` (top-right, top-left, bottom-right, bottom-left, top-center, bottom-center), `gap` (spacing between toasts), `maxVisible` (number — e.g. 5), `expand` (boolean — show all vs. stacked), `duration` (default duration for all toasts), `swipeDirection` |
| **Description** | Global toast manager rendered once in the root layout. Provides `useToast()` hook to create/dismiss toasts from anywhere. |
| **Usage** | `<ToastContainer position="top-right" maxVisible={3} />` |

### AlertBanner

| Aspect | Details |
|--------|---------|
| **Component** | `<AlertBanner>` |
| **Props** | `type` (info, success, warning, error), `message` (string), `action` (ReactNode — button / link), `dismissible` (boolean), `onDismiss`, `fixed` (boolean — fixed top position), `sticky` (boolean — scrolls with page) |
| **Description** | Page-level announcement banner. Can be fixed at top of viewport or inline. |
| **Usage** | `<AlertBanner type="warning" message="Site maintenance tonight" dismissible />` |

### ConfirmDialog

| Aspect | Details |
|--------|---------|
| **Component** | `<ConfirmDialog>` |
| **Props** | `open`, `onOpenChange`, `title` (string), `message` (string or ReactNode), `confirmLabel` (string — default "Confirm"), `cancelLabel` (string — default "Cancel"), `variant` (default, destructive — red confirm button), `onConfirm`, `onCancel`, `loading` (boolean — shows spinner on confirm button), `icon` (Lucide icon — warning, info icons), `confirmDisabled` (boolean) |
| **Description** | Confirmation modal for destructive actions or important prompts. Built on Modal. |
| **Usage** | `<ConfirmDialog open={showDelete} onOpenChange={setShowDelete} title="Delete product?" message="This action cannot be undone." variant="destructive" onConfirm={handleDelete} loading={isDeleting} />` |

### EmptyState

| Aspect | Details |
|--------|---------|
| **Component** | `<EmptyState>` |
| **Props** | `icon` (Lucide icon component), `title` (string), `description` (string), `action` (ReactNode — `<Button>`), `illustration` (ReactNode — custom SVG or image), `size` (sm, md, lg) |
| **Description** | Placeholder shown when there is no data. Combines an illustration, heading, explanation, and a call-to-action button. |
| **Usage** | `<EmptyState icon={Package} title="No products yet" description="Add your first product to start selling" action={<Button>Add Product</Button>} />` |

### ErrorState

| Aspect | Details |
|--------|---------|
| **Component** | `<ErrorState>` |
| **Props** | `title` (string — default "Something went wrong"), `message` (string — default error description), `error` (Error object — for details, not displayed to user directly), `onRetry` (callback — retry button shown if provided), `icon` (Lucide icon — default alert), `fullPage` (boolean — centered full-page layout) |
| **Description** | Error display with retry action. Graceful error boundary fallback for components. |
| **Usage** | `<ErrorState onRetry={refetch} fullPage />` |

### LoadingOverlay

| Aspect | Details |
|--------|---------|
| **Component** | `<LoadingOverlay>` |
| **Props** | `loading` (boolean), `variant` (spinner, skeleton, shimmer), `blur` (boolean — blur background content), `opacity` (number — overlay opacity), `fullScreen` (boolean), `message` (string — loading text), `as` (overlay or inline replacement) |
| **Description** | Loading overlay that covers a container or full screen. Blurs background content while showing a spinner or skeleton. |
| **Usage** | `<LoadingOverlay loading={isLoading} variant="spinner" blur />` |

### ProgressStepper

| Aspect | Details |
|--------|---------|
| **Component** | `<ProgressStepper>` |
| **Props** | `currentStep` (number), `steps` (array of step objects with `label`, `description?`), `orientation` (horizontal, vertical), `variant` (numbered, icon, dot, compact), `onStepClick` (optional callback to navigate to completed steps) |
| **Description** | Step progress indicator for multi-step flows. Similar to StepNav but focused on progress visualization rather than navigation. |
| **Usage** | `<ProgressStepper currentStep={1} steps={["Details", "Photos", "Publish"]} />` |

### NotificationBell

| Aspect | Details |
|--------|---------|
| **Component** | `<NotificationBell>` |
| **Props** | `count` (number — unread count, 0 hides badge), `items` (array of notification objects — `{ id, title, description?, time, read, href? }`), `onItemClick`, `onMarkAllRead`, `onClear`, `loading`, `emptyMessage`, `onOpen` (callback when dropdown opens) |
| **Description** | Bell icon with unread badge and dropdown notification list. |
| **Usage** | `<NotificationBell count={unreadCount} items={notifications} onItemClick={handleClick} />` |

### InlineNotification

| Aspect | Details |
|--------|---------|
| **Component** | `<InlineNotification>` |
| **Props** | `type` (info, success, warning, error), `message` (string or ReactNode), `action` (ReactNode), `dismissible` (boolean), `onDismiss`, `icon` (boolean — show type icon) |
| **Description** | Compact notification embedded within content, not floating like Toast. Used inline in forms, tables, or sections. |
| **Usage** | `<InlineNotification type="success" message="Changes saved successfully" dismissible />` |

---

## 8. Business Components

### SearchBar

| Aspect | Details |
|--------|---------|
| **Component** | `<SearchBar>` |
| **Props** | `value`, `onChange`, `onSearch` (callback on Enter/click), `suggestions` (array of suggestion objects `{ label, value, type?, icon? }`), `onSuggestionSelect`, `loading` (boolean — spinner), `filters` (array of filter objects for category refinement), `activeFilter` (string), `onFilterChange`, `placeholder` (string), `debounceMs` (number), `onClear`, `recentSearches` (string[]), `showRecent` (boolean), `onRemoveRecent` |
| **Description** | Full-featured search input with dropdown suggestions, category filter pills, recent searches, and debounced async search. |
| **States** | idle, typing, loading (async search), suggestions-visible, no-results, filter-active |
| **Accessibility** | `role="combobox"` with `aria-expanded` and `aria-controls`; `aria-activedescendant` on suggestion list; `role="listbox"` for suggestions; Escape to close; keyboard navigation (arrow keys) |
| **Usage** | `<SearchBar value={query} onChange={setQuery} onSearch={handleSearch} suggestions={results} filters={categories} debounceMs={300} />` |

### ProductGallery

| Aspect | Details |
|--------|---------|
| **Component** | `<ProductGallery>`, `<ProductGallery.MainImage>`, `<ProductGallery.Thumbnails>`, `<ProductGallery.Zoom>`, `<ProductGallery.Lightbox>` |
| **Props (ProductGallery)** | `images` (array of `{ src, alt, thumbnail? }`), `aspectRatio` (1:1, 4:3), `zoom` (boolean — hover or click to zoom), `lightbox` (boolean — click to open fullscreen), `currentIndex`/`onIndexChange`, `thumbnailPosition` (bottom, left, right), `allowFullscreen` (boolean) |
| **Description** | Product image gallery with main image, thumbnail strip, hover zoom (lens or inner zoom), and fullscreen lightbox with prev/next navigation. |
| **Usage** | `<ProductGallery images={productImages} zoom lightbox thumbnailPosition="bottom" />` |

### CategoryTree

| Aspect | Details |
|--------|---------|
| **Component** | `<CategoryTree>` |
| **Props** | `categories` (nested category array), `selected` (string — selected category id), `onSelect`, `expanded` (string[]), `onToggle`, `showCount` (boolean — product count per category), `searchable` (boolean — filter categories) |
| **Description** | Hierarchical category browser for marketplace navigation. Expandable nodes with product counts and selection. Built on TreeView. |
| **Usage** | `<CategoryTree categories={categories} selected={catId} onSelect={setCat} showCount searchable />` |

### CartItem

| Aspect | Details |
|--------|---------|
| **Component** | `<CartItem>` |
| **Props** | `item` (CartItem — product, quantity, variant, price, image), `onQuantityChange` (callback), `onRemove`, `onMoveToWishlist`, `maxQuantity` (number — stock limit), `readOnly` (boolean — display mode), `showSeller` (boolean) |
| **Description** | Cart line item with product image, name, variant, quantity stepper, unit price, total, and remove action. |
| **States** | default, quantity-at-limit (max reached, stepper disabled), removing (fade-out animation), out-of-stock-overlay |
| **Usage** | `<CartItem item={item} onQuantityChange={updateQty} onRemove={removeItem} />` |

### OrderSummary

| Aspect | Details |
|--------|---------|
| **Component** | `<OrderSummary>` |
| **Props** | `items` (array of `{ label, amount, isDiscount?, isShipping? }`), `subtotal` (number), `discount` (number), `shipping` (number), `tax` (number), `total` (number), `currency` (string), `loading` (boolean), `action` (ReactNode — checkout button), `showBreakdown` (boolean — expand/collapse details), `coupon` (applied coupon code + discount) |
| **Description** | Order total summary with line items, discounts, shipping, tax, and total. Used in cart page and checkout sidebar. |
| **Usage** | `<OrderSummary subtotal={1500} discount={100} shipping={60} tax={30} total={1490} action={<Button>Proceed to Checkout</Button>} />` |

### AddressForm

| Aspect | Details |
|--------|---------|
| **Component** | `<AddressForm>` |
| **Props** | `value` (Address object), `onChange`, `countries` (array), `loading` (boolean — loading dependent dropdowns), `errors` (validation errors per field), `disabled` (boolean), `hideFields` (string[] — fields to omit), `simplified` (boolean — hide optional fields) |
| **Description** | Address form with country/state/city cascading dropdowns and validation. Auto-populates state/city based on country selection. |
| **Usage** | `<AddressForm value={address} onChange={setAddress} countries={countries} errors={errors} />` |

### PaymentMethodSelector

| Aspect | Details |
|--------|---------|
| **Component** | `<PaymentMethodSelector>` |
| **Props** | `methods` (array of saved payment methods — `{ id, type, last4, expiry, isDefault }`), `selected` (string — selected method id), `onSelect`, `onAddNew` (callback), `onDelete`, `onSetDefault`, `loading`, `adding` (boolean — shows add card form) |
| **Description** | Saved payment method selector with radio selection, add new card option, and method management (delete, set default). |
| **Usage** | `<PaymentMethodSelector methods={paymentMethods} selected={selectedMethod} onSelect={setPaymentMethod} onAddNew={showAddCard} />` |

### FileUploader

| Aspect | Details |
|--------|---------|
| **Component** | `<FileUploader>`, `<FileUploader.DropZone>`, `<FileUploader.FileList>`, `<FileUploader.FileItem>` |
| **Props (FileUploader)** | `accept` (string — MIME types), `maxSize` (number — bytes), `maxFiles` (number), `multiple` (boolean), `files` (controlled File[]), `onFilesChange`, `onError` (callback for validation errors), `validateFile` (custom function), `disabled`, `url` (upload endpoint), `autoUpload` (boolean), `headers` (object — upload request headers) |
| **Props (DropZone)** | `label` (string — "Drag & drop or click to browse"), `hint` (string — "PNG, JPG up to 5MB"), `icon` (Lucide icon — default Upload), `active` (boolean — drag-over state) |
| **Props (FileItem)** | `file` (File), `progress` (0–100), `status` (pending, uploading, uploaded, error), `error` (string), `onRemove`, `preview` (boolean — show image thumbnail) |
| **Description** | Drag-and-drop file upload zone with file validation, upload progress per file, previews for images, and error handling. |
| **States** | idle, drag-over (highlighted), uploading (progress per file), uploaded (success), error (validation or upload), file-limit-reached |
| **Accessibility** | Drop zone has `role="button"` and keyboard activation; `aria-label` on file list; progress updates announced via `aria-live`; file items have remove buttons with `aria-label` |
| **Usage** | `<FileUploader accept="image/*" maxSize={5242880} maxFiles={5} multiple url="/api/upload" autoUpload />` |

### ImageCropper

| Aspect | Details |
|--------|---------|
| **Component** | `<ImageCropper>` |
| **Props** | `src` (string — image URL or File converted to object URL), `aspectRatio` (number — e.g. 1, 4/3, 16/9), `onCropComplete` (callback — returns cropped Blob/File), `cropShape` (rect, round), `minZoom` (number), `maxZoom` (number), `zoom` / `onZoomChange` (controlled), `rotation` / `onRotationChange` (controlled), `showGrid` (boolean), `loading` (boolean) |
| **Description** | Client-side image cropping with zoom, rotate, and aspect ratio lock. Used for profile avatars and product image thumbnails. |
| **Usage** | `<ImageCropper src={imageSrc} aspectRatio={1} cropShape="round" onCropComplete={handleCrop} />` |

### RichTextViewer

| Aspect | Details |
|--------|---------|
| **Component** | `<RichTextViewer>` |
| **Props** | `content` (string — HTML or Markdown), `format` (html, markdown), `className`, `prose` (boolean — apply Tailwind typography prose styles), `maxHeight` (string — scrollable beyond this), `truncate` (number — max characters before "Show more") |
| **Description** | Renders HTML or Markdown content safely (sanitized) with typography styling. Used for product descriptions, seller policies, and terms. |
| **Usage** | `<RichTextViewer content={product.description} format="html" prose truncate={500} />` |

### CouponInput

| Aspect | Details |
|--------|---------|
| **Component** | `<CouponInput>` |
| **Props** | `value` (string — coupon code input), `onChange`, `onApply` (callback — validates and applies), `onRemove` (callback — removes applied coupon), `applied` (boolean — coupon is applied), `appliedCode` (string — the applied code), `discount` (string — "10% off" or "৳50 off"), `loading` (boolean — validating), `error` (string — invalid/expired message), `validating` (boolean — async validation in progress) |
| **Description** | Coupon code input with apply/remove toggle and validation feedback. |
| **States** | empty, typing, validating (async), valid+applied (shows discount), invalid (error message), removed |
| **Usage** | `<CouponInput value={code} onChange={setCode} onApply={applyCoupon} onRemove={removeCoupon} applied={!!coupon} discount={coupon?.description} loading={isValidating} error={couponError} />` |

### ShareButtons

| Aspect | Details |
|--------|---------|
| **Component** | `<ShareButtons>` |
| **Props** | `url` (string — share URL), `title` (string — share title), `description` (string), `image` (string — for OG image), `networks` (array — facebook, twitter, whatsapp, telegram, email, copyLink, embed), `onCopy` (callback), `onShare` (callback — for native share API), `variant` (icon-only, with-label, rounded, squared), `size` (sm, md, lg), `label` (boolean — show label) |
| **Description** | Social share buttons with network-specific URLs and native Web Share API fallback. |
| **Usage** | `<ShareButtons url={productUrl} title={product.name} networks={["facebook","twitter","copyLink"]} />` |

### FollowButton

| Aspect | Details |
|--------|---------|
| **Component** | `<FollowButton>` |
| **Props** | `following` (boolean), `onToggle` (callback), `count` (number — follower count), `showCount` (boolean), `loading` (boolean), `size` (sm, md, lg), `variant` (outline, solid), `labels` (follow text, following text — e.g. { follow: "Follow", following: "Following" }) |
| **Description** | Follow/unfollow toggle button for sellers. Shows follower count, animated transition between states. |
| **States** | not-following, following, hover-on-following ("Unfollow" preview), loading, count-update |
| **Usage** | `<FollowButton following={isFollowing} onToggle={toggleFollow} count={seller.followers} showCount />` |

### WishlistButton

| Aspect | Details |
|--------|---------|
| **Component** | `<WishlistButton>` |
| **Props** | `wishlisted` (boolean), `onToggle` (callback), `loading` (boolean), `size` (sm, md, lg), `variant` (icon-only, with-label), `label` (string or object for add/remove), `count` (number — wishlist count) |
| **Description** | Heart icon button that toggles filled/unfilled. Animates with a brief scale pulse on toggle. |
| **States** | not-wishlisted, wishlisted, wishlisted-hover, loading |
| **Usage** | `<WishlistButton wishlisted={isWishlisted} onToggle={toggleWishlist} size="md" />` |

### ReportButton

| Aspect | Details |
|--------|---------|
| **Component** | `<ReportButton>` |
| **Props** | `onSubmit` (callback — `(reason: string, details: string) => void`), `contentId` (string — the ID of content being reported), `contentType` (product, review, seller), `reasons` (array of reason objects — `{ value, label }`), `loading` (boolean), `submitted` (boolean — thank-you state) |
| **Description** | Content reporting button that opens a modal with reason selector and optional details textarea. |
| **States** | closed, reporting (modal open), submitting, submitted (thank-you message), error |
| **Usage** | `<ReportButton onSubmit={reportContent} contentType="product" reasons={reportReasons} />` |

---

## 9. Chart Components

### Chart Foundation

All chart components share a unified foundation built on a lightweight charting library (e.g., Recharts or a custom SVG-based approach). They share common props:

- `data` (array of data points)
- `dimensions` (width, height, or responsive via container)
- `margin` (top, right, bottom, left)
- `colors` (custom color palette)
- `animate` (boolean — mount animation)
- `theme` (light/dark adaptation)
- `locale` (number/date formatting)
- `ariaLabel` (for accessibility)
- `emptyState` (ReactNode — shown when no data)

### LineChart

| Aspect | Details |
|--------|---------|
| **Component** | `<LineChart>` |
| **Specific Props** | `series` (array of `{ key, name, color?, dashed? }`), `xAxisKey` (string), `yAxisKey` (string), `showDots` (boolean), `dotSize`, `curveType` (monotone, linear, step), `showGrid`, `showLegend`, `showTooltip`, `tooltipFormatter` (custom formatter), `yAxisLabel`, `xAxisLabel`, `syncId` (for syncing with other charts) |
| **Description** | Multi-series line chart with tooltip, legend, and grid lines. |
| **Usage** | `<LineChart data={revenueData} series={[{key:'revenue',name:'Revenue'}]} xAxisKey="date" showLegend />` |

### BarChart

| Aspect | Details |
|--------|---------|
| **Component** | `<BarChart>` |
| **Specific Props** | `orientation` (vertical, horizontal), `stacked` (boolean), `grouped` (boolean), `series` (array of `{ key, name, color? }`), `xAxisKey`, `yAxisKey`, `barSize`, `showValues` (boolean — value labels on bars), `layout` (vertical, horizontal) |
| **Description** | Bar chart supporting vertical/horizontal orientation, stacked and grouped series. |
| **Usage** | `<BarChart data={salesData} series={[{key:'online',name:'Online'},{key:'offline',name:'Offline'}]} stacked xAxisKey="month" />` |

### PieChart

| Aspect | Details |
|--------|---------|
| **Component** | `<PieChart>` |
| **Specific Props** | `dataKey` (string — value field), `nameKey` (string — label field), `donut` (boolean — center hole), `innerRadius` (number), `outerRadius` (number), `showLabels` (boolean — percentage/value labels on slices), `showLegend`, `activeIndex` / `onActiveIndexChange`, `expandOnHover` (boolean — slice expands slightly), `centerLabel` (ReactNode — for donut center text), `padAngle` (number) |
| **Description** | Pie/donut chart with slice labels, legend, and interactive hover expansion. |
| **Usage** | `<PieChart data={categoryBreakdown} nameKey="category" dataKey="count" donut centerLabel={<span>Total<br/>{total}</span>} />` |

### AreaChart

| Aspect | Details |
|--------|---------|
| **Component** | `<AreaChart>` |
| **Specific Props** | `series` (array of `{ key, name, color? }`), `stacked` (boolean), `gradient` (boolean — gradient fill from color to transparent), `xAxisKey`, `showDots`, `curveType`, `showGrid` |
| **Description** | Area chart with optional gradient fill and stacking. Used for cumulative metrics like total users or revenue. |
| **Usage** | `<AreaChart data={userGrowth} series={[{key:'users',name:'Users'}]} xAxisKey="date" gradient />` |

### Sparkline

| Aspect | Details |
|--------|---------|
| **Component** | `<Sparkline>` |
| **Props** | `data` (number[]), `width` (number — default 120), `height` (number — default 30), `color` (string), `highlightColor` (string — for positive/negative), `showArea` (boolean — mini area fill), `curveType`, `animate` (boolean) |
| **Description** | Tiny inline chart for metric cards. Shows trend direction at a glance. |
| **Usage** | `<Sparkline data={[-1, 3, 5, 2, 8]} color="#22c55e" showArea />` |

### RatingDistribution

| Aspect | Details |
|--------|---------|
| **Component** | `<RatingDistribution>` |
| **Props** | `ratings` (array of `{ stars: 1–5, count: number }`), `total` (number — total reviews), `size` (sm, md, lg), `showPercentage` (boolean), `showCount` (boolean) |
| **Description** | Star rating breakdown bar chart. Horizontal bars for each star level with count and percentage. |
| **Usage** | `<RatingDistribution ratings={productRatingDistribution} total={totalReviews} showPercentage />` |

### RevenueChart

| Aspect | Details |
|--------|---------|
| **Component** | `<RevenueChart>` |
| **Props** | `data` (time-series revenue data), `interval` (daily, weekly, monthly, yearly), `onIntervalChange`, `comparison` (show previous period overlay), `currency` (string), `showMovingAverage` (boolean), `movingAverageDays` (number) |
| **Description** | Time-series revenue chart with period selector and previous-period comparison. Built on LineChart or AreaChart. |
| **Usage** | `<RevenueChart data={revenue} interval="monthly" comparison currency="BDT" />` |

### SalesChart

| Aspect | Details |
|--------|---------|
| **Component** | `<SalesChart>` |
| **Props** | `data` (sales data), `aggregation` (daily, weekly, monthly), `onAggregationChange`, `series` (separate lines for different statuses — completed, pending, cancelled), `showTarget` (boolean — target line overlay), `target` (number) |
| **Description** | Sales performance chart with aggregation controls and target comparison. |
| **Usage** | `<SalesChart data={sales} aggregation="weekly" showTarget target={100000} />` |

---

## 10. Component Best Practices

### File Structure

Every component follows a consistent file layout:

```
components/ui/Button/
├── Button.tsx              # Component implementation
├── Button.types.ts         # Props interface + subcomponent types
├── Button.test.tsx         # Unit tests (React Testing Library)
├── Button.stories.tsx      # Storybook stories
└── index.ts                # Re-export
```

For simpler atoms, a single file suffices:

```
components/ui/Badge/
├── Badge.tsx               # Types + implementation + export
├── Badge.test.tsx
└── Badge.stories.tsx
```

### Code Conventions

| Rule | Description |
|------|-------------|
| **Exported Props** | Every component exports its `Props` interface (e.g., `export interface ButtonProps { ... }`) |
| **Default Props** | Default values are assigned via destructuring defaults, not `defaultProps` (deprecated in React 19) |
| **className** | All components accept `className?: string` and merge with internal classes via `cn()` utility (clsx + tailwind-merge) |
| **forwardRef** | All interactive elements (buttons, inputs, triggers) use `forwardRef` to expose the underlying DOM node |
| **as prop** | Polymorphic components use `as` prop (e.g., `<Button as="a" href="...">` or `<Button as={Link} href="...">`). Implemented via a `PolymorphicComponent` type utility. |
| **Semantic HTML** | Buttons render `<button>`, navigation renders `<nav>`, lists render `<ul>`/`<ol>`, tables render `<table>`. Divs are only used when no semantic element applies. |
| **ARIA** | Role, state, and property ARIA attributes are applied based on component state, not hardcoded. |
| **Keyboard Events** | Interactive components handle Enter, Space, Escape, Arrow keys for keyboard-only navigation. |
| **Animation** | Enter/exit animations use Framer Motion's `motion.div` and `AnimatePresence`. Motion is disabled when `prefers-reduced-motion` is set. |
| **Responsive Design** | Tailwind breakpoint classes (`sm:`, `md:`, `lg:`, `xl:`) are used for responsive variants. Components accept responsive prop objects where applicable (e.g., `<Grid cols={{ base: 1, md: 2, lg: 3 }} />`). |

### Polymorphic Component Pattern

```typescript
// Conceptual signature — not real code
type PolymorphicProps<
  T extends React.ElementType,
  P = {}
> = {
  as?: T;
  children?: React.ReactNode;
  className?: string;
} & P &
  React.ComponentPropsWithoutRef<T>;
```

### the `cn()` Utility

A shared utility function that merges Tailwind classes without conflict:

```typescript
// cn('px-4', 'px-2') → 'px-2'
// cn('text-red-500', false && 'text-blue-500') → 'text-red-500'
```

Backed by `clsx` for conditional class logic and `tailwind-merge` for conflict resolution.

### Animation Guidelines

| Pattern | Implementation |
|---------|----------------|
| Mount/Unmount | `AnimatePresence` + `motion.div` with `initial`/`animate`/`exit` |
| Hover | `whileHover` prop on `motion.div` or `motion.button` |
| Tap/Press | `whileTap` prop (subtle scale down) |
| Stagger Children | `variants` with `staggerChildren` on parent |
| Page Transitions | Layout groups via `layout` prop |
| Reduced Motion | `useReducedMotion()` from Framer Motion to conditionally disable |
| Shared Layout | `layoutId` for smooth element transitions between views |

---

## 11. State Management Within Components

### State Decision Matrix

| State Type | Hook | When to Use |
|-----------|------|-------------|
| UI-only toggle | `useState` | Dropdown open/closed, tab selected, accordion expanded |
| Controlled form value | Props (`value` + `onChange`) | Input value managed by parent form library |
| Uncontrolled form value | `useState` (internal) + optional `defaultValue` | Simple forms where parent does not need live value |
| Derived / computed | `useMemo` | Filtered list, sorted data, formatted value |
| Async callback | `useCallback` | Memoized event handlers passed to child components |
| Side effect | `useEffect` | Sync with localStorage, fetch initial data, focus management |
| Complex state | `useReducer` | Multi-field state (e.g., date picker with year/month/day), undo/redo |
| Controllable (dual-mode) | Custom `useControllableState` hook | Components that work both controlled and uncontrolled |
| Composition state | `React.Context` | Compound component state sharing (Tabs, Accordion, Table) |
| Form state | External library (react-hook-form) | Complex forms with validation, touched/dirty tracking |
| Server state | External library (TanStack Query) | Data fetching, caching, optimistic updates |

### Controllable State Pattern

A custom hook `useControllableState` enables the dual-mode pattern:

```typescript
// Conceptual signature
function useControllableState<T>({
  prop?: T,           // Controlled value from parent
  defaultProp?: T,    // Uncontrolled default
  onChange?: (val: T) => void,
  name?: string       // For debugging
}): [T, (val: T) => void]
```

- If `prop` is provided, the component is controlled and `onChange` fires on updates.
- If only `defaultProp` is provided, the component manages its own internal state.
- If neither is provided, the component manages state with a sensible default.

---

## 12. Component Testing Guidelines

### Testing Stack

| Tool | Purpose |
|------|---------|
| Vitest + React Testing Library | Unit and integration tests |
| jest-axe | Automated accessibility audits |
| @storybook/testing-react | Story integration tests |
| MSW (Mock Service Worker) | API mocking for data-driven components |

### Testing Principles

1. **Test behavior, not implementation.** Do not assert on internal state, refs, or class names. Assert on what the user sees and interacts with.

2. **Query by accessibility role, label, or text.** Use `getByRole`, `getByLabelText`, `getByText` over `getByTestId`. Test IDs are a last resort for elements with no semantic role.

3. **Cover every state.** Each component must have tests for:
   - Default / idle state
   - Hover state (if it changes appearance)
   - Focus / focus-visible state
   - Active / pressed state (buttons, toggles)
   - Disabled state (if applicable)
   - Loading state (if applicable)
   - Error state (if applicable)
   - Empty state (data-driven components)
   - Edge cases (very long text, zero values, boundary conditions)

4. **Keyboard interaction tests.** Verify:
   - Tab reaches interactive elements
   - Enter/Space activates buttons and toggles
   - Arrow keys navigate radio groups, tabs, dropdown menus
   - Escape closes modals, popovers, dropdowns
   - Tab cycles through focusable elements inside modals (focus trap)

5. **Accessibility tests.** Run `jest-axe` on every component:
   - `expect(await axe(container)).toHaveNoViolations()`
   - Verify ARIA attributes are correct per state
   - Verify color contrast meets WCAG AA

6. **Snapshot tests are optional.** Prefer behavioral tests. Snapshot only for complex rendered output (e.g., RichTextViewer).

### Test Structure Template

```
describe('ComponentName', () => {
  describe('States', () => {
    it('renders in default state')
    it('renders in disabled state')
    it('renders in loading state')
    it('renders in error state')
    it('renders in empty state')
  })

  describe('Interactions', () => {
    it('responds to click')
    it('responds to keyboard Enter')
    it('responds to keyboard Escape')
    it('calls onChange with expected value')
    it('does not call onChange when disabled')
  })

  describe('Accessibility', () => {
    it('has no accessibility violations')
    it('has correct ARIA roles')
    it('supports keyboard navigation')
  })
})
```

### Mocking Strategy

| Scenario | Approach |
|----------|----------|
| Child components | Mock only when testing integration; prefer real renders for unit tests |
| Router hooks | Mock `next/navigation` (`useRouter`, `usePathname`) |
| API calls | MSW handlers for component integration tests |
| Lucide icons | Do not mock — they are lightweight SVG components |
| Framer Motion | Use `motion()` mock that renders children directly; or use `useReducedMotion` test helper |
| File/Image data | `File` constructor + `URL.createObjectURL` mock |

### Accessibility Checklist

- [ ] Component is keyboard navigable
- [ ] Focus order follows visual order
- [ ] Focus indicator is visible (focus-visible ring)
- [ ] ARIA roles are correct (`button`, `tab`, `dialog`, `menu`, etc.)
- [ ] ARIA states are accurate (`aria-expanded`, `aria-selected`, `aria-checked`, `aria-current`)
- [ ] Live regions (`aria-live`) announce dynamic changes
- [ ] Labels are associated (`aria-labelledby`, `htmlFor`/`id`)
- [ ] Error messages are linked via `aria-describedby`
- [ ] Color contrast meets WCAG AA (4.5:1 normal text, 3:1 large text)
- [ ] Touch targets are at least 44×44px on mobile
- [ ] Reduced motion respected (animations disabled)
- [ ] Screen reader announcements for loading/completion states

---

> **Document Status:** Architecture Reference — v1.0
> **Last Updated:** July 2026
> **Maintainer:** Frontend Architecture Team
