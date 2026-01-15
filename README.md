# ⬡ MATRIX TASKS SYS v2.0

> *"There is no spoon... only tasks."*

A sleek, cyberpunk-themed task management application built with Python and CustomTkinter. Features animated neon borders, Matrix-style boot sequences, and a retro-futuristic terminal aesthetic.

![Python](https://img.shields.io/badge/Python-3.11+-00FF41?style=flat-square&logo=python&logoColor=00FF41)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.0+-00FF41?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-00FF41?style=flat-square&logo=windows)
![License](https://img.shields.io/badge/License-MIT-00FF41?style=flat-square)

---

## ✨ Features

### 🎨 **Aesthetic Design**
- **Matrix/Cyberpunk theme** with neon green, cyan, gold, and red accents
- **Animated pulsing borders** that glow based on task priority
- **Startup boot sequence** with randomized console-style text animation
- **Monospace terminal aesthetic** using Consolas font throughout

### 📋 **Task Management**
- Create, edit, and delete tasks with confirmation dialogs
- **Priority levels**: HIGH (🔴), MED (🟡), LOW (🔵), NONE (🟢)
- **Due dates** with quick-select buttons (Today, +1 Day, +7 Days)
- **Overdue detection** with visual warnings
- Persistent storage via JSON

### 🔍 **Organization**
- **Real-time search** filtering
- **Filter tabs**: All, Active, Done, High Priority, Overdue
- **Statistics dashboard** with completion progress bar
- Auto-sorting and visual hierarchy

### 🔔 **Notifications & Sound**
- **Windows toast notifications** for overdue tasks on startup
- **Matrix-style beep sounds** for actions (toggleable)
- Audio feedback for add, complete, and delete actions

### ⌨️ **Keyboard Shortcuts**
| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Focus new task input |
| `Ctrl+F` | Focus search bar |
| `Ctrl+1` | Show all tasks |
| `Ctrl+2` | Show pending tasks |
| `Ctrl+3` | Show completed tasks |
| `Ctrl+M` | Toggle sound effects |

---

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- Windows OS (for sound effects and notifications)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Zeretsu/Matrix-Style-To-Do-App.git
   cd matrix-tasks
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install customtkinter win10toast
   ```

4. **Run the application**
   ```bash
   python todo_app.py
   ```

---

## 📁 Project Structure

```
ToDoApp/
├── todo_app.py      # Main application code
├── tasks.json       # Persistent task storage (auto-generated)
├── README.md        # This file
└── .venv/           # Virtual environment
```

---

## 🎮 Usage

### Adding a Task
1. Type your task in the input field marked with `>`
2. Select a priority level from the dropdown (optional)
3. Click **EXEC** or press **Enter**

### Editing a Task
1. Click the **EDIT** button on any task
2. Modify the text, priority, or due date
3. Use quick date buttons for fast scheduling
4. Click **SAVE CHANGES**

### Completing a Task
- Click the `[ ]` checkbox to mark as complete `[X]`
- Click again to uncomplete

### Deleting a Task
- Click **DEL** → Confirm in the warning dialog

---

## 🎨 Color Palette

| Element | Color | Hex |
|---------|-------|-----|
| Background | Black | `#000000` |
| Accent (Primary) | Matrix Green | `#00FF41` |
| High Priority | Neon Red | `#FF0F55` |
| Medium Priority | Neon Gold | `#FFB200` |
| Low Priority | Neon Cyan | `#00E0FF` |
| Dimmed Text | Dark Green | `#008F11` |

---

## 🔧 Configuration

Tasks are stored in `tasks.json` in the same directory as the script. The file is automatically created on first run.

### Task Data Structure
```json
{
  "id": "timestamp",
  "text": "Task description",
  "completed": false,
  "priority": "HIGH|MED|LOW|NONE",
  "due_date": "YYYY-MM-DD",
  "created_at": "ISO timestamp",
  "completed_at": "ISO timestamp"
}
```

---

## 📸 Screenshots

*Boot Sequence*
```
MATRIX_TASKS_SYS v2.0
========================

[INIT] Loading kernel modules...
[OK] Core systems online
[INIT] Establishing neural link...
[OK] Connection secured
[INIT] Loading task database...
[OK] Data integrity verified

SYSTEM READY.
Entering main interface...
```

---

## 🛠️ Dependencies

| Package | Purpose |
|---------|---------|
| `customtkinter` | Modern themed UI widgets |
| `win10toast` | Windows desktop notifications |
| `winsound` | System beep sounds (built-in) |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🙏 Acknowledgments

- Inspired by *The Matrix* (1999)
- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Font: Consolas (Microsoft)

---

<p align="center">
  <code>SYSTEM :: TASKS v2.0</code><br>
  <sub>Made with 💚 in the Matrix</sub>
</p>
