# 📢 Digital Notice Board System

A modern, full-featured Python-based Digital Notice Board System where administrators can post, update, delete, and view notices sorted by date, category, or priority.

---

## 🌟 Key Features

- **Administrator Capabilities**:
  - **Post Announcements**: Create notices with title, category, priority (Urgent, High, Normal, Low), author/department, expiration dates, and pin-to-top option.
  - **Update Notices**: Edit any existing notice details in real time.
  - **Delete Notices**: Safe deletion with confirmation.
  - **Pin to Top**: Highlight critical announcements at the top of the board.
- **Viewing & Sorting**:
  - **Sort by Date**: View newest first or oldest first.
  - **Sort by Category**: Browse notices alphabetically by category or group.
  - **Sort by Priority**: Instant visibility for urgent emergency bulletins.
  - **Filter by Category**: Interactive pill tabs with real-time counters.
  - **Live Search**: Instant keyword search matching titles, body text, and departments.
- **Dual Interface**:
  - **Modern Web Application**: Glassmorphic dark/light UI, responsive card grid, breaking news live ticker, clock, and full-screen **Kiosk / Digital Signage Mode** for campus/office display TVs.
  - **Interactive CLI (Command-Line Interface)**: Full-featured terminal console for quick headless administration and viewing.
- **Persistence**: Built-in SQLite database with auto-initialization and realistic seed announcements.

---

## 🚀 Quick Start

### 1. Prerequisites & Environment
From the repository root:
```bash
# Activate the existing virtual environment or create one
source ../.venv/bin/activate   # or .venv/bin/activate
```

### 2. Run the Web Application
```bash
# Run web server
python3 app.py
# or using the virtualenv:
../.venv/bin/python app.py
```
Open your browser at: **`http://127.0.0.1:5001`**

#### Web Features:
- Click **"Admin Mode: OFF"** in the top-right header to activate Admin Mode.
- Click **"➕ Post Notice"** to open the announcement modal.
- Click **"🖥️ Kiosk Mode"** to launch full-screen digital signage view with live ticker.
- Use the **Category pills**, **Sort By** dropdown, and **Search bar** to instantly organize notices.

---

### 3. Run the Command-Line Interface (CLI)
```bash
python3 cli.py
# or using the virtualenv:
../.venv/bin/python cli.py
```

#### CLI Menu Options:
1. `📋 View Notices`: Sort by date (newest/oldest), category, or priority, or filter by category.
2. `➕ Post New Notice (Admin)`: Interactive prompts to publish a new notice.
3. `✏️ Update Existing Notice (Admin)`: Edit title, category, priority, pin status, or content.
4. `🗑️ Delete Notice (Admin)`: Remove unwanted notices with confirmation.
5. `🔍 Quick Search Notices`: Search by keyword.
6. `ℹ️ System Info`: View database statistics.

---

## 🧪 Running Tests
```bash
python3 test_notice_board.py
# or
../.venv/bin/python test_notice_board.py
```
