# ASTA / PEIS Frontend — Personal Engineering Intelligence System

[![Vite](https://img.shields.io/badge/Vite-6.0+-blue?style=flat-square&logo=vite)](https://vite.dev/)
[![React](https://img.shields.io/badge/React-18.0+-blue?style=flat-square&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-blue?style=flat-square&logo=tailwindcss)](https://tailwindcss.com/)

The premium React client interface for **ASTA (Personal Engineering Intelligence System)**. It features a calm, modern, and dark-themed engineering mentor workspace with glassmorphism, responsive canvas diagrams, and real-time streaming chat boxes.

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
│   │   ├── DiagramViewer.tsx     # Mermaid.js architecture vector canvas
│   │   ├── SearchPanel.tsx       # Local keyword/symbol metadata explorer
│   │   ├── WorkspaceManager.tsx  # Workspace project directory registrar
│   │   ├── WorkspaceStats.tsx    # Workspace file counters & token profiler cards
│   │   └── SettingsDrawer.tsx    # LLM keys and configurations panel
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

## ⚡ Key Frontend Features & Micro-Animations
*   **Floating Chat Capsule**: A floating glassmorphic input panel at the bottom of the chat viewport with real-time streaming typewriter rendering.
*   **Streaming Loader Pulse**: Shows a loading indicator (`Formulating suggested follow-ups...`) only *after* the core explanation finishes and during the Interview Agent's query generation phase.
*   **Suggested Questions Fallback**: A trailing list parser automatically extracts numbered questions (e.g. `1. Why... \n 2. How...`) from response text and converts them into interactive buttons.
*   **Symbol Tabs Segment Control**: Upgrades generic lists into elegant pill-like navigation chips (All, Files, Classes, Functions, Routes) inside the search panel.
*   **Mermaid Render Canvas**: Fits vector diagrams cleanly inside borders with soft opacity levels.

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
The optimized bundle will be compiled into the `dist/` folder, ready for deployment.
