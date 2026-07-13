# SubBot Admin Panel — Professional UI/UX Guide

## 🎨 Design System Overview

The admin panel has been completely redesigned with modern, professional UI components and patterns. This guide documents the improvements and features available.

## 📋 Table of Contents

1. [Visual Design](#visual-design)
2. [Component Library](#component-library)
3. [JavaScript Features](#javascript-features)
4. [Templates](#templates)
5. [Best Practices](#best-practices)
6. [Responsive Design](#responsive-design)

---

## 🎨 Visual Design

### Color Palette

The panel uses a carefully curated color system:

```css
Primary:      #4f46e5 (Indigo)
Success:      #10b981 (Emerald)
Warning:      #f59e0b (Amber)
Danger:       #ef4444 (Red)
Info:         #0ea5e9 (Sky)
Neutral:      #f1f5f9 to #0f172a (Gray scale)
```

### Typography

- **Font Family**: Inter (system fallback: -apple-system, BlinkMacSystemFont, Segoe UI)
- **Font Weights**: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)
- **Base Size**: 14px (0.875rem)

### Spacing System

```
xs:  4px   (0.25rem)
sm:  8px   (0.5rem)
md:  16px  (1rem)
lg:  24px  (1.5rem)
xl:  28px  (1.75rem)
```

### Shadows

```css
--shadow:     0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)
--shadow-md:  0 4px 16px rgba(15, 23, 42, 0.08)
--shadow-lg:  0 10px 40px rgba(15, 23, 42, 0.12)
```

### Border Radius

```css
--radius:     12px
--radius-sm:  8px
```

---

## 📦 Component Library

### 1. Cards & Containers

#### Basic Card
```html
<div class="card">
  <div class="card-header">
    <h5>Card Title</h5>
  </div>
  <div class="card-body">
    Content here
  </div>
</div>
```

#### Stat Cards
```html
<div class="stats-grid">
  <div class="stat-card">
    <div>
      <div class="stat-label">Label</div>
      <div class="stat-value">1,234</div>
      <div class="stat-hint">Additional info</div>
    </div>
    <div class="stat-card-icon blue"><i class="bi bi-icon"></i></div>
  </div>
</div>
```

Icon classes: `.blue`, `.green`, `.orange`, `.red`, `.purple`, `.teal`

### 2. Detail Sections

For detail/show pages:

```html
<div class="detail-header">
  <div class="detail-title">Page Title</div>
  <div class="detail-meta">
    <span class="detail-meta-item">Meta info</span>
  </div>
</div>

<div class="detail-grid">
  <div class="detail-section">
    <div class="detail-section-title">Section Title</div>
    <div class="detail-content">
      <div class="detail-row">
        <div class="detail-label">Label</div>
        <div class="detail-value">Value</div>
      </div>
    </div>
  </div>
</div>
```

### 3. Tables

#### Data Tables
```html
<div class="card">
  <div class="table-wrapper">
    <table class="data-table" id="my-table">
      <thead>
        <tr>
          <th data-sortable="0">Column 1</th>
          <th>Column 2</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Data 1</td>
          <td>Data 2</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

**Features**:
- Sortable columns (add `data-sortable="index"`)
- Hover effects
- Responsive wrapper
- Zebra striping

### 4. Forms

#### Basic Form Group
```html
<div class="form-group">
  <label class="form-label required">Field Label</label>
  <input type="text" class="form-control" placeholder="Enter value..." required />
  <div class="help-text">Optional help text</div>
</div>
```

#### Form with Validation
```html
<form method="post" data-validate>
  <div class="form-group">
    <label class="form-label required">Name</label>
    <input type="text" class="form-control" name="name" required />
    <div class="invalid-feedback">This field is required</div>
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

#### File Upload
```html
<div class="file-upload" id="my-upload">
  <div class="file-upload-icon"><i class="bi bi-cloud-arrow-up"></i></div>
  <div class="file-upload-text">Drag files here or click to upload</div>
  <div class="file-upload-hint">Max 10MB, JPG/PNG only</div>
  <input type="file" hidden />
</div>
```

#### Toggle/Switch
```html
<div class="form-check form-switch">
  <input class="form-check-input" type="checkbox" id="toggle" />
  <label class="form-check-label" for="toggle">Enable feature</label>
</div>
```

### 5. Buttons & Action Menus

#### Button Variants
```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-danger">Danger</button>
<button class="btn btn-outline-primary">Outline</button>

<!-- Sizes -->
<button class="btn btn-sm">Small</button>
<button class="btn">Normal</button>
<button class="btn btn-lg">Large</button>

<!-- Icon button -->
<button class="btn btn-icon btn-outline-secondary">
  <i class="bi bi-pencil"></i>
</button>
```

#### Action Menus
```html
<div class="action-menu">
  <a href="#" class="action-menu-item">
    <i class="bi bi-pencil"></i> Edit
  </a>
  <a href="#" class="action-menu-item danger">
    <i class="bi bi-trash"></i> Delete
  </a>
</div>
```

### 6. Badges & Status

#### Status Badges
```html
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-danger">Failed</span>
<span class="badge badge-info">Info</span>
```

#### Status Indicators
```html
<div class="status-indicator">
  <div class="status-dot success"></div>
  Active
</div>
```

### 7. Alerts & Modals

#### Alert Messages
```html
<div class="alert alert-success alert-dismissible fade show">
  <i class="bi bi-check-circle"></i>
  Success message
  <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

#### Modals
```html
<div class="modal fade" id="myModal" tabindex="-1">
  <div class="modal-dialog modal-sm">
    <div class="modal-content">
      <div class="modal-header">
        <h6 class="modal-title">Modal Title</h6>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        Content here
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-primary">Save</button>
      </div>
    </div>
  </div>
</div>
```

### 8. Filter Bar
```html
<div class="filter-bar">
  <form class="d-flex gap-2 flex-wrap">
    <div class="flex-grow-1">
      <select class="form-select form-select-sm">
        <option>All</option>
      </select>
    </div>
    <button type="submit" class="btn btn-primary btn-sm">Filter</button>
    <a href="?" class="btn btn-outline-secondary btn-sm">Clear</a>
  </form>
</div>
```

### 9. Empty States
```html
<div class="empty-state">
  <div class="empty-state-icon"><i class="bi bi-inbox"></i></div>
  <div class="empty-state-title">No Data</div>
  <div class="empty-state-text">Start by creating your first item</div>
  <a href="#" class="btn btn-primary mt-3">Create Item</a>
</div>
```

### 10. Loading & Progress

#### Spinner
```html
<div class="spinner-sm"></div>
```

#### Loading Skeleton
```html
<div class="loading-skeleton" style="height: 40px; border-radius: 8px;"></div>
```

#### Progress Bar
```html
<div class="progress-bar-custom">
  <div class="progress-bar-fill" style="width: 65%;"></div>
</div>
```

### 11. Timeline
```html
<div class="timeline">
  <div class="timeline-item">
    <div class="timeline-date">2024-07-11</div>
    <div class="timeline-title">Payment Received</div>
    <div class="timeline-desc">User completed payment</div>
  </div>
  <div class="timeline-item">
    <div class="timeline-date">2024-07-10</div>
    <div class="timeline-title">Subscription Started</div>
    <div class="timeline-desc">User activated subscription</div>
  </div>
</div>
```

---

## 🎯 JavaScript Features

### Form Validation
Automatically validate forms with `data-validate` attribute:

```html
<form method="post" data-validate>
  <input type="email" required />
  <!-- Validation happens automatically -->
</form>
```

### Table Sorting
Enable column sorting with `data-sortable`:

```html
<th data-sortable="0">Name</th>
```

### Table Filtering
Filter table with search:

```html
<input type="text" data-table-filter="table-id" />
```

### Copy to Clipboard
```html
<code data-copy>value-to-copy</code>
```

### Confirmation Dialogs
```html
<button data-confirm="Are you sure?">Delete</button>
```

### Tooltips
```html
<button data-bs-toggle="tooltip" title="Help text">Hover me</button>
```

### Available Functions

```javascript
// Format currency
formatUzs(1000000) // Returns: "1 000 000 so'm"

// Sort table
sortTable(tableElement, columnIndex)

// Filter table
filterTable(searchTerm, tableId)

// Show toast notification
showToast("Success!", "success", 3000)

// Copy to clipboard
navigator.clipboard.writeText("text")
```

---

## 📄 Templates Structure

### Page Layout
All pages extend `panel/base.html` and follow this structure:

```html
{% extends "panel/base.html" %}
{% block title %}Page Title{% endblock %}
{% block page_title %}Page Title{% endblock %}
{% block page_subtitle %}<p class="topbar-subtitle">Subtitle</p>{% endblock %}

{% block topbar_actions %}
<!-- Action buttons here -->
{% endblock %}

{% block content %}
<!-- Page content here -->
{% endblock %}

{% block extra_js %}
<!-- Additional JS here -->
{% endblock %}
```

### Template Files

| Template | Purpose | Features |
|----------|---------|----------|
| `base.html` | Layout wrapper | Sidebar, topbar, content area |
| `dashboard.html` | Dashboard | Stats cards, quick actions |
| `users/list.html` | Users listing | Search, filter, statistics |
| `users/detail.html` | User profile | Subscriptions, transactions, stats |
| `channels/list.html` | Channels & tariffs | Channel cards, tariff tables |
| `transactions/list.html` | Payment list | Status filtering, statistics |
| `broadcast/list.html` | Broadcast messages | Status, statistics, progress |

---

## 🎓 Best Practices

### 1. Consistent Spacing
Use the spacing system:
```html
<div class="mb-4"><!-- margin-bottom: 24px --></div>
<div class="gap-2"><!-- gap: 8px --></div>
<div class="mt-3"><!-- margin-top: 16px --></div>
```

### 2. Icon Usage
Always use Bootstrap Icons (CDN included):
```html
<i class="bi bi-pencil"></i>
<i class="bi bi-trash"></i>
<i class="bi bi-check-circle"></i>
```

### 3. Color Coding
- Green: Success, active, positive
- Blue: Info, neutral, primary action
- Orange: Warning, pending
- Red: Danger, error, negative

### 4. Loading States
Always provide feedback for async actions:
```javascript
showLoading(button)
// ... do work ...
hideLoading(button, "Done")
showToast("Operation completed!", "success")
```

### 5. Confirmation for Destructive Actions
```html
<button onclick="return confirm('Are you sure?')">Delete</button>
```

### 6. Responsive Tables
Always wrap tables in `.table-wrapper`:
```html
<div class="table-wrapper">
  <table class="data-table">...</table>
</div>
```

### 7. Empty States
Always provide helpful empty states with action buttons.

### 8. Form Labels
Always mark required fields:
```html
<label class="form-label required">Field Name</label>
```

### 9. Data Attributes
Use data attributes for JavaScript features:
```html
data-sortable="0"
data-table-filter="table-id"
data-copy
data-bs-toggle="modal"
data-format-number
data-format-date
```

### 10. Accessibility
- Use semantic HTML
- Include `aria-label` on icon buttons
- Ensure color contrast
- Support keyboard navigation

---

## 📱 Responsive Design

### Breakpoints
```css
Mobile:  < 576px
Tablet:  ≥ 576px to < 992px
Desktop: ≥ 992px
```

### Mobile Optimizations
- Sidebar becomes offcanvas
- Tables stack vertically
- Grid columns collapse
- Buttons become full-width

### Responsive Classes
```html
<div class="d-flex flex-column gap-2 gap-md-3">
  <!-- Stack on mobile, use more space on desktop -->
</div>
```

---

## 🚀 Performance Tips

1. **Lazy Load Images**
   ```html
   <img src="image.jpg" loading="lazy" />
   ```

2. **Minimize Modals**
   Only show what's necessary

3. **Debounce Search**
   JavaScript handles this automatically

4. **Use Data Attributes**
   Less CSS, more performant

5. **Cache Selectors**
   Don't query DOM repeatedly

---

## 🔧 Customization Guide

### Change Primary Color
Edit `/static/panel/css/panel.css`:
```css
:root {
  --primary: #your-color;
  --primary-hover: #your-dark-color;
  --primary-light: #your-light-color;
}
```

### Add New Status Badge
```css
.badge-custom {
  background: #custom-color;
  color: #custom-text-color;
}
```

### Add New Card Type
```css
.card-special {
  background: linear-gradient(...);
  border: none;
}
```

---

## 📚 Resource Links

- **Bootstrap Icons**: https://icons.getbootstrap.com
- **Inter Font**: https://fonts.google.com/specimen/Inter
- **Bootstrap Docs**: https://getbootstrap.com/docs
- **MDN Web Docs**: https://developer.mozilla.org

---

## ✨ Features Implemented

- ✅ Modern, professional design system
- ✅ Responsive layout (mobile, tablet, desktop)
- ✅ Advanced form validation
- ✅ Table sorting and filtering
- ✅ Status indicators and badges
- ✅ Loading and skeleton states
- ✅ Toast notifications
- ✅ Modal dialogs
- ✅ Keyboard shortcuts (Ctrl+K for search)
- ✅ Accessibility improvements
- ✅ Performance optimizations
- ✅ Dark mode ready (uses CSS variables)

---

## 📞 Support

For questions or improvements, contact the development team.

---

**Last Updated**: July 11, 2024  
**Version**: 1.0.0
