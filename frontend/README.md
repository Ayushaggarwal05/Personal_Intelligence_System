# ASTA / PEIS Frontend — Personal Engineering Intelligence System

[![Vite](https://img.shields.io/badge/Vite-6.0+-blue?style=flat-square&logo=vite)](https://vite.dev/)
[![React](https://img.shields.io/badge/React-18.0+-blue?style=flat-square&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-blue?style=flat-square&logo=tailwindcss)](https://tailwindcss.com/)

The premium React client interface for **PEIS (Personal Engineering Intelligence System)**. It features a calm, modern, dark-themed engineering mentor workspace with glassmorphism, responsive architectural diagram canvas, and real-time streaming chat boxes.

---

## 🎨 Premium Visual Theme
Governed by a curated carbon and sage green palette, configuring the workspace for long, comfortable engineering sessions:

- **App Background**: `#131816` (Deep Obsidian)
- **Sidebar & Header**: `#1A211E` (Warm Carbon)
- **Section Cards**: `#202824` (Elevated Sage)
- **Elevated Surfaces**: `#262F2A` (Focus Cards)
- **Hover Surfaces**: `#313B35` (Accent Highlighting)
- **Primary Accent**: `#4D7C73` (Deep Sage Teal)
- **Secondary Accent**: `#98B6A7` (Muted Olive Green)

---

## 📐 Components & Directory Structure
```text
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWindow.tsx        # Stream explainer interface & follow-up suggestions
│   │   ├── DiagramViewer.tsx     # Responsive Mermaid.js vector canvas & alert cards
│   │   ├── SearchPanel.tsx       # Local keyword/symbol metadata explorer
│   │   ├── WorkspaceManager.tsx  # Workspace project directory registrar
│   │   ├── WorkspaceStats.tsx    # Workspace file counters & token profiler cards
│   │   └── SettingsDrawer.tsx    # Scoped LLM keys panel with "── OR ──" divider
│   │
│   ├── App.tsx                   # Core layout controller and tab navigations
│   ├── index.css                 # Premium styling variables, animations & scrollbars
│   └── main.tsx                  # Vite React launchpad
│
├── public/                       # Logos and static media assets
├── index.html                    # HTML entrypoint
├── tailwind.config.js            # Tailwind layout and transitions
└── tsconfig.json                 # TypeScript build configurations
```

---

## ⚡ Key Frontend Features & Responsive Viewports
*   **Architectural Diagram Canvas (`DiagramViewer.tsx`)**:
    - **Tab 1: Controller Sequence**: Traces the overall end-to-end request flow (Frontend UI ➔ Controller/Router ➔ Service ➔ SQLite Storage).
    - **Tab 2: Database Schema ER**: Displays a detailed Entity-Relationship schema containing all data models and field attributes.
    - **Tab 3: Backend Routes Flow**: Displays a complete flowchart map of all backend API endpoints and handler functions.
    - **Responsive Viewport SVG Scaling**: Automatically scales sequence diagrams and flowcharts to fill 100% of the canvas with clear, legible text.
    - **Alert Card Navigation**: Displays clear UI alert cards if an API key is missing or rate limited, with a direct button leading to Settings.
*   **Settings Drawer (`SettingsDrawer.tsx`)**:
    - Features a visual `── OR ─` divider between Gemini and Groq API key inputs to clearly show that only one key is required.
    - Filters out dummy placeholder keys (`AIzaSyTestKey`/`gsk_TestKey`) automatically.
*   **Floating Chat Capsule (`ChatWindow.tsx`)**:
    - Real-time SSE typewriter streaming with auto-scroll.
    - Interactive suggested follow-up study question buttons.

---

## 🚀 Getting Started

### 1. Prerequisites
*   **Node.js (v18+)**
*   **npm or yarn**

### 2. Installation & Run
1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install project dependencies**:
    ```bash
    npm install
    ```

3.  **Launch the Vite Dev Server**:
    ```bash
    npm run dev
    ```
    The application will run locally at **`http://localhost:5173`**. Ensure your backend server is active on `http://localhost:8000`.

---

## 🔒 Build for Production
To build and optimize the React files for production:
```bash
npm run build
```
The optimized bundle will be compiled into the `dist/` folder.
