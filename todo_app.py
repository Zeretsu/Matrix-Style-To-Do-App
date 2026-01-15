import customtkinter as ctk
from datetime import datetime, date
import json
import os
import random
import threading

# Try to import winsound for sound effects (Windows only)
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

# Try to import Windows toast notifications
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False

# Configure appearance
ctk.set_appearance_mode("dark")

# Matrix Color Palette
COLOR_BG = "#000000"
COLOR_CARD = "#050505"
COLOR_ACCENT = "#00FF41"
COLOR_DIM = "#008F11"
COLOR_BORDER = "#003B00"

# Aesthetic Neon Colors
COLOR_HIGH = "#FF0F55"  # Neon Red/Pink
COLOR_MED = "#FFB200"   # Neon Gold/Orange
COLOR_LOW = "#00E0FF"   # Neon Cyan
COLOR_NONE = "#008F11"  # Standard Matrix Green

FONT_MONO = "Consolas"

# Priority config with "Pulse" target colors (brighter versions)
PRIORITIES = {
    "HIGH": {"color": COLOR_HIGH, "pulse": "#FF80A0", "label": "HIGH"},
    "MED": {"color": COLOR_MED, "pulse": "#FFE080", "label": "MED"},
    "LOW": {"color": COLOR_LOW, "pulse": "#AAFFFF", "label": "LOW"},
    "NONE": {"color": COLOR_NONE, "pulse": COLOR_ACCENT, "label": "NONE"}
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def interpolate_color(c1, c2, t):
    """Interpolate between two hex colors. t is between 0.0 and 1.0"""
    try:
        rgb1 = hex_to_rgb(c1)
        rgb2 = hex_to_rgb(c2)
        rgb = tuple(int(rgb1[i] + (rgb2[i] - rgb1[i]) * t) for i in range(3))
        return rgb_to_hex(rgb)
    except:
        return c1


def play_sound(sound_type="click"):
    """Play Matrix-style beep sounds"""
    if not SOUND_AVAILABLE:
        return
    try:
        if sound_type == "click":
            winsound.Beep(800, 50)
        elif sound_type == "complete":
            winsound.Beep(1000, 80)
            winsound.Beep(1200, 80)
        elif sound_type == "delete":
            winsound.Beep(400, 100)
        elif sound_type == "add":
            winsound.Beep(600, 50)
            winsound.Beep(900, 50)
    except:
        pass  # Sound not available


class MatrixButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(
            font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_DIM,
            text_color=COLOR_ACCENT,
            corner_radius=0,
            hover_color=COLOR_DIM
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.configure(border_color=COLOR_ACCENT, text_color=COLOR_BG)

    def on_leave(self, e):
        self.configure(border_color=COLOR_DIM, text_color=COLOR_ACCENT)


class EditDialog(ctk.CTkToplevel):
    def __init__(self, parent, task_data, on_save):
        super().__init__(parent)
        self.task_data = task_data.copy()
        self.on_save = on_save
        
        self.title("EDIT_PROTOCOL")
        self.geometry("500x420")
        self.configure(fg_color=COLOR_BG)
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Title
        ctk.CTkLabel(
            content,
            text="MODIFY TASK DATA:",
            font=ctk.CTkFont(family=FONT_MONO, size=16, weight="bold"),
            text_color=COLOR_ACCENT
        ).pack(anchor="w", pady=(0, 20))
        
        # Task text
        ctk.CTkLabel(
            content,
            text="> OBJECTIVE:",
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            text_color=COLOR_DIM
        ).pack(anchor="w")
        
        self.text_entry = ctk.CTkEntry(
            content,
            font=ctk.CTkFont(family=FONT_MONO, size=14),
            height=42,
            corner_radius=0,
            border_width=1,
            fg_color=COLOR_CARD,
            border_color=COLOR_DIM,
            text_color=COLOR_ACCENT
        )
        self.text_entry.pack(fill="x", pady=(5, 18))
        self.text_entry.insert(0, task_data["text"])
        
        # Priority - use segmented button style
        ctk.CTkLabel(
            content,
            text="> PRIORITY LEVEL:",
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            text_color=COLOR_DIM
        ).pack(anchor="w")
        
        priority_frame = ctk.CTkFrame(content, fg_color="transparent")
        priority_frame.pack(fill="x", pady=(8, 18))
        
        self.priority_var = ctk.StringVar(value=task_data.get("priority", "NONE"))
        self.priority_buttons = {}
        
        for p_id in ["NONE", "LOW", "MED", "HIGH"]:
            p_config = PRIORITIES[p_id]
            is_selected = self.priority_var.get() == p_id
            
            btn = ctk.CTkButton(
                priority_frame,
                text=p_id,
                width=95,
                height=32,
                corner_radius=0,
                font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
                fg_color=p_config["color"] if is_selected else COLOR_CARD,
                text_color=COLOR_BG if is_selected else p_config["color"],
                text_color_disabled=COLOR_BG,
                border_width=1,
                border_color=p_config["color"],
                hover_color=p_config["pulse"],  # Use lighter pulse color for hover
                command=lambda pid=p_id: self._select_priority(pid)
            )
            btn.pack(side="left", padx=(0, 8))
            self.priority_buttons[p_id] = btn
            
            # Bind hover events to ensure text stays visible
            btn.bind("<Enter>", lambda e, b=btn: b.configure(text_color=COLOR_BG))
            btn.bind("<Leave>", lambda e, b=btn, pid=p_id: b.configure(
                text_color=COLOR_BG if self.priority_var.get() == pid else PRIORITIES[pid]["color"]
            ))
        
        # Due date with quick buttons
        ctk.CTkLabel(
            content,
            text="> DUE DATE:",
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            text_color=COLOR_DIM
        ).pack(anchor="w")
        
        date_frame = ctk.CTkFrame(content, fg_color="transparent")
        date_frame.pack(fill="x", pady=(8, 8))
        
        self.due_entry = ctk.CTkEntry(
            date_frame,
            font=ctk.CTkFont(family=FONT_MONO, size=14),
            height=38,
            width=150,
            corner_radius=0,
            border_width=1,
            fg_color=COLOR_CARD,
            border_color=COLOR_DIM,
            text_color=COLOR_ACCENT,
            placeholder_text="YYYY-MM-DD"
        )
        self.due_entry.pack(side="left", padx=(0, 10))
        if task_data.get("due_date"):
            self.due_entry.insert(0, task_data["due_date"])
        
        # Quick date buttons
        quick_dates = [
            ("TODAY", 0),
            ("+1 DAY", 1),
            ("+7 DAYS", 7),
            ("CLEAR", -1)
        ]
        
        for label, days in quick_dates:
            btn = ctk.CTkButton(
                date_frame,
                text=label,
                width=70,
                height=38,
                corner_radius=0,
                font=ctk.CTkFont(family=FONT_MONO, size=10),
                fg_color=COLOR_CARD,
                text_color=COLOR_DIM,
                border_width=1,
                border_color=COLOR_BORDER,
                hover_color=COLOR_DIM,
                command=lambda d=days: self._set_quick_date(d)
            )
            btn.pack(side="left", padx=(0, 5))
        
        # Spacer
        ctk.CTkFrame(content, fg_color="transparent", height=20).pack(fill="x")
        
        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        MatrixButton(
            btn_frame,
            text="CANCEL",
            width=120,
            height=38,
            command=self.destroy
        ).pack(side="left")
        
        MatrixButton(
            btn_frame,
            text="SAVE CHANGES",
            width=140,
            height=38,
            command=self._save
        ).pack(side="right")
        
        self.text_entry.focus()
        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())
    
    def _select_priority(self, p_id):
        self.priority_var.set(p_id)
        # Update button visuals
        for pid, btn in self.priority_buttons.items():
            p_config = PRIORITIES[pid]
            is_selected = pid == p_id
            btn.configure(
                fg_color=p_config["color"] if is_selected else COLOR_CARD,
                text_color=COLOR_BG if is_selected else p_config["color"]
            )
    
    def _set_quick_date(self, days):
        self.due_entry.delete(0, "end")
        if days >= 0:
            from datetime import timedelta
            target = date.today() + timedelta(days=days)
            self.due_entry.insert(0, target.strftime("%Y-%m-%d"))
    
    def _save(self):
        new_text = self.text_entry.get().strip()
        if not new_text:
            return
        
        due_date = self.due_entry.get().strip()
        # Validate date format
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                due_date = ""
        
        self.on_save(
            self.task_data["id"],
            new_text,
            self.priority_var.get(),
            due_date if due_date else None
        )
        self.destroy()


class ConfirmDialog(ctk.CTkToplevel):
    """Matrix-style confirmation dialog"""
    def __init__(self, parent, title, message, on_confirm):
        super().__init__(parent)
        self.on_confirm = on_confirm
        self.result = False
        
        self.title(title)
        self.geometry("380x180")
        self.configure(fg_color=COLOR_BG)
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Warning icon/text
        ctk.CTkLabel(
            content,
            text="⚠ WARNING",
            font=ctk.CTkFont(family=FONT_MONO, size=16, weight="bold"),
            text_color=COLOR_HIGH
        ).pack(anchor="w", pady=(0, 15))
        
        # Message
        ctk.CTkLabel(
            content,
            text=message,
            font=ctk.CTkFont(family=FONT_MONO, size=13),
            text_color=COLOR_ACCENT,
            wraplength=330,
            justify="left"
        ).pack(anchor="w", pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="ABORT",
            width=100,
            height=36,
            corner_radius=0,
            font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
            fg_color="transparent",
            text_color=COLOR_DIM,
            border_width=1,
            border_color=COLOR_DIM,
            hover_color="#002200",
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="CONFIRM",
            width=100,
            height=36,
            corner_radius=0,
            font=ctk.CTkFont(family=FONT_MONO, size=12, weight="bold"),
            fg_color=COLOR_HIGH,
            text_color=COLOR_BG,
            border_width=1,
            border_color=COLOR_HIGH,
            hover_color="#AA0033",
            command=self._confirm
        ).pack(side="right")
        
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self._confirm())
    
    def _confirm(self):
        self.result = True
        self.on_confirm()
        self.destroy()


class TaskItem(ctk.CTkFrame):
    def __init__(self, parent, task_data, on_toggle, on_delete, on_edit, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.task_data = task_data
        self.on_toggle = on_toggle
        self.on_delete = on_delete
        self.on_edit = on_edit
        
        is_done = task_data["completed"]
        priority = task_data.get("priority", "NONE")
        due_date = task_data.get("due_date")
        
        # Check if overdue
        self.is_overdue = False
        if due_date and not is_done:
            try:
                due = datetime.strptime(due_date, "%Y-%m-%d").date()
                if due < date.today():
                    self.is_overdue = True
            except:
                pass
        
        # Determine colors
        self.base_color = COLOR_BORDER
        self.pulse_target = None
        
        if self.is_overdue:
            self.base_color = PRIORITIES["HIGH"]["color"]
            self.pulse_target = PRIORITIES["HIGH"]["pulse"]
        elif priority != "NONE" and not is_done:
            self.base_color = PRIORITIES[priority]["color"]
            self.pulse_target = PRIORITIES[priority]["pulse"]
        
        # Animation state
        self.pulse_phase = 0.0
        self.pulse_direction = 1
        self.anim_running = False
        
        self.configure(
            fg_color=COLOR_CARD,
            corner_radius=0,
            border_width=1,
            border_color=self.base_color if not is_done else "#001100"
        )
        
        # Main row
        main_row = ctk.CTkFrame(self, fg_color="transparent")
        main_row.pack(fill="x", padx=10, pady=(10, 5))
        
        # Checkbox
        self.status_label = ctk.CTkLabel(
            main_row,
            text="[X]" if is_done else "[ ]",
            font=ctk.CTkFont(family=FONT_MONO, size=16, weight="bold"),
            text_color=COLOR_ACCENT if is_done else COLOR_DIM,
            width=40
        )
        self.status_label.pack(side="left", padx=(0, 10))
        self.status_label.bind("<Button-1>", lambda e: self._on_toggle())
        
        # Priority badge
        if priority != "NONE":
            p_config = PRIORITIES[priority]
            ctk.CTkLabel(
                main_row,
                text=f"[{p_config['label']}]",
                font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
                text_color=p_config["color"] if not is_done else COLOR_DIM,
                width=50
            ).pack(side="left", padx=(0, 8))
        
        # Task text
        text_color = COLOR_DIM if is_done else COLOR_ACCENT
        self.task_label = ctk.CTkLabel(
            main_row,
            text=task_data["text"],
            font=ctk.CTkFont(family=FONT_MONO, size=14),
            text_color=text_color,
            anchor="w"
        )
        self.task_label.pack(side="left", fill="x", expand=True)
        
        # Edit button
        self.edit_btn = ctk.CTkButton(
            main_row,
            text="EDIT",
            width=40,
            height=24,
            corner_radius=0,
            fg_color="transparent",
            text_color=COLOR_DIM,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color="#001122",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            command=self._on_edit
        )
        self.edit_btn.pack(side="right", padx=(5, 0))
        
        # Delete button
        self.delete_btn = ctk.CTkButton(
            main_row,
            text="DEL",
            width=40,
            height=24,
            corner_radius=0,
            fg_color="transparent",
            text_color=COLOR_DIM,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color="#220000",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            command=self._on_delete
        )
        self.delete_btn.pack(side="right", padx=(5, 0))
        
        # Metadata row (due date, created time)
        meta_row = ctk.CTkFrame(self, fg_color="transparent")
        meta_row.pack(fill="x", padx=10, pady=(0, 8))
        
        meta_parts = []
        
        # Created timestamp
        created = task_data.get("created_at", "")
        if created:
            try:
                dt = datetime.fromisoformat(created)
                meta_parts.append(f"CREATED: {dt.strftime('%Y-%m-%d %H:%M')}")
            except:
                pass
        
        # Due date
        if due_date:
            due_text = f"DUE: {due_date}"
            if self.is_overdue:
                due_text += " [OVERDUE]"
            meta_parts.append(due_text)
        
        # Completed timestamp
        if is_done and task_data.get("completed_at"):
            try:
                dt = datetime.fromisoformat(task_data["completed_at"])
                meta_parts.append(f"COMPLETED: {dt.strftime('%Y-%m-%d %H:%M')}")
            except:
                pass
        
        if meta_parts:
            meta_color = COLOR_HIGH if self.is_overdue else "#004400"
            ctk.CTkLabel(
                meta_row,
                text="  |  ".join(meta_parts),
                font=ctk.CTkFont(family=FONT_MONO, size=9),
                text_color=meta_color,
                anchor="w"
            ).pack(side="left", padx=(50, 0))
        
        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.task_label.bind("<Enter>", self._on_enter)
        self.task_label.bind("<Leave>", self._on_leave)
        
        # Start animation if needed
        if self.pulse_target and not is_done:
            self.anim_running = True
            self.animate_border()

    def animate_border(self):
        if not self.anim_running or not self.winfo_exists():
            return

        # Calculate phase (0.0 to 1.0)
        step = 0.05
        if self.pulse_direction == 1:
            self.pulse_phase += step
            if self.pulse_phase >= 1.0:
                self.pulse_phase = 1.0
                self.pulse_direction = -1
        else:
            self.pulse_phase -= step
            if self.pulse_phase <= 0.0:
                self.pulse_phase = 0.0
                self.pulse_direction = 1
        
        # Interpolate
        current_color = interpolate_color(self.base_color, self.pulse_target, self.pulse_phase)
        self.configure(border_color=current_color)
        
        # Schedule next frame (50ms interval = ~20fps)
        self.after(50, self.animate_border)

    def _on_enter(self, e=None):
        if not self.task_data["completed"]:
            self.anim_running = False  # Pause animation on hover
            self.configure(border_color=COLOR_ACCENT)
            self.status_label.configure(text_color=COLOR_ACCENT)

    def _on_leave(self, e=None):
        if not self.task_data["completed"]:
            self.status_label.configure(text_color=COLOR_DIM)
            # If we were animating, resume
            if self.pulse_target:
                self.anim_running = True
                self.animate_border()
            else:
                self.configure(border_color=self.base_color)

    def _on_toggle(self):
        self.on_toggle(self.task_data["id"])
    
    def _on_delete(self):
        self.on_delete(self.task_data["id"])
    
    def _on_edit(self):
        self.on_edit(self.task_data)


class BootScreen(ctk.CTkToplevel):
    """Matrix-style boot animation"""
    def __init__(self, parent, on_complete):
        super().__init__(parent)
        self.on_complete = on_complete
        
        self.title("SYSTEM_BOOT")
        self.geometry("500x350")
        self.configure(fg_color=COLOR_BG)
        self.resizable(False, False)
        self.overrideredirect(True)  # No window decorations
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 350) // 2
        self.geometry(f"500x350+{x}+{y}")
        
        # Border frame
        border = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG,
            border_width=2,
            border_color=COLOR_ACCENT,
            corner_radius=0
        )
        border.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Console output
        self.console = ctk.CTkLabel(
            border,
            text="",
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            text_color=COLOR_ACCENT,
            justify="left",
            anchor="nw"
        )
        self.console.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Boot messages
        self.boot_lines = [
            "MATRIX_TASKS_SYS v2.0",
            "========================",
            "",
            "[INIT] Loading kernel modules...",
            "[OK] Core systems online",
            "[INIT] Establishing neural link...",
            "[OK] Connection secured",
            "[INIT] Loading task database...",
            "[OK] Data integrity verified",
            "[INIT] Initializing UI renderer...",
            "[OK] Display matrix active",
            "",
            "SYSTEM READY.",
            "Entering main interface..."
        ]
        self.current_line = 0
        self.current_text = ""
        
        self.after(300, self.animate_boot)
    
    def animate_boot(self):
        if self.current_line < len(self.boot_lines):
            line = self.boot_lines[self.current_line]
            self.current_text += line + "\n"
            self.console.configure(text=self.current_text)
            self.current_line += 1
            
            # Randomize delay for effect
            delay = random.randint(80, 200)
            if "[OK]" in line:
                delay = random.randint(150, 300)
            
            self.after(delay, self.animate_boot)
        else:
            # Boot complete
            self.after(600, self._finish)
    
    def _finish(self):
        self.destroy()
        self.on_complete()


def check_overdue_notifications(tasks):
    """Send Windows toast notification for overdue tasks"""
    if not TOAST_AVAILABLE:
        return
    
    today = date.today()
    overdue_tasks = []
    
    for task in tasks:
        if task["completed"]:
            continue
        due = task.get("due_date")
        if due:
            try:
                due_date = datetime.strptime(due, "%Y-%m-%d").date()
                if due_date < today:
                    overdue_tasks.append(task["text"][:40])
            except:
                pass
    
    if overdue_tasks:
        try:
            toaster = ToastNotifier()
            count = len(overdue_tasks)
            title = f"⚠ {count} OVERDUE TASK{'S' if count > 1 else ''}"
            msg = "\n".join(overdue_tasks[:3])
            if count > 3:
                msg += f"\n...and {count - 3} more"
            
            # Run in thread to not block UI
            threading.Thread(
                target=lambda: toaster.show_toast(title, msg, duration=5, threaded=True),
                daemon=True
            ).start()
        except:
            pass


class ToDoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ZERETSU_TASKS_SYS_V2")
        self.geometry("580x820")
        self.minsize(500, 650)
        self.configure(fg_color=COLOR_BG)
        
        # Data
        self.data_file = os.path.join(os.path.dirname(__file__), "tasks.json")
        self.tasks = self.load_tasks()
        self.current_filter = "all"
        self.search_query = ""
        self.sound_enabled = True
        
        self.create_ui()
        self.render_tasks()
        self.setup_keybindings()
    
    def setup_keybindings(self):
        """Setup keyboard shortcuts"""
        self.bind("<Control-n>", lambda e: self.task_entry.focus())
        self.bind("<Control-f>", lambda e: self.search_entry.focus())
        self.bind("<Control-1>", lambda e: self.set_filter("all"))
        self.bind("<Control-2>", lambda e: self.set_filter("pending"))
        self.bind("<Control-3>", lambda e: self.set_filter("completed"))
        self.bind("<Control-m>", lambda e: self.toggle_sound())
    
    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        status = "ON" if self.sound_enabled else "OFF"
        self.sound_btn.configure(text=f"SND:{status}")
    
    def create_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header row
        header_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            header_row,
            text="ZERETSU MATRIX TASKS SYS v2.0",
            font=ctk.CTkFont(family=FONT_MONO, size=22, weight="bold"),
            text_color=COLOR_ACCENT
        ).pack(side="left")
        
        # Sound toggle
        self.sound_btn = ctk.CTkButton(
            header_row,
            text="SND:ON",
            width=70,
            height=24,
            corner_radius=0,
            fg_color="transparent",
            text_color=COLOR_DIM,
            border_width=1,
            border_color=COLOR_BORDER,
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            command=self.toggle_sound
        )
        self.sound_btn.pack(side="right")
        
        # Separator
        ctk.CTkFrame(self.main_frame, height=2, fg_color=COLOR_DIM).pack(fill="x", pady=(0, 15))
        
        # Keyboard shortcuts hint
        ctk.CTkLabel(
            self.main_frame,
            text="HOTKEYS: Ctrl+N=New | Ctrl+F=Search | Ctrl+1/2/3=Filter | Ctrl+M=Sound",
            font=ctk.CTkFont(family=FONT_MONO, size=9),
            text_color="#003300"
        ).pack(anchor="w", pady=(0, 10))
        
        # Stats Console
        self.stats_box = ctk.CTkFrame(
            self.main_frame,
            fg_color="#000500",
            corner_radius=0,
            border_width=1,
            border_color=COLOR_DIM
        )
        self.stats_box.pack(fill="x", pady=(0, 15))
        
        stats_inner = ctk.CTkFrame(self.stats_box, fg_color="transparent")
        stats_inner.pack(fill="x", padx=15, pady=10)
        
        self.stats_label = ctk.CTkLabel(
            stats_inner,
            text="LOADING DATA...",
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            text_color=COLOR_ACCENT,
            justify="left",
            anchor="w"
        )
        self.stats_label.pack(fill="x")
        
        # Search bar
        search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            search_frame,
            text="SEARCH:",
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            text_color=COLOR_DIM
        ).pack(side="left")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="FILTER_BY_KEYWORD...",
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            height=32,
            corner_radius=0,
            border_width=1,
            fg_color=COLOR_BG,
            border_color=COLOR_BORDER,
            text_color=COLOR_ACCENT,
            placeholder_text_color="#003300"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        MatrixButton(
            search_frame,
            text="CLEAR",
            width=60,
            height=32,
            command=self._clear_search
        ).pack(side="right")

        # Input Prompt with priority
        input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=(5, 10))
        
        ctk.CTkLabel(
            input_frame, 
            text="> ", 
            font=ctk.CTkFont(family=FONT_MONO, size=16),
            text_color=COLOR_ACCENT
        ).pack(side="left")

        self.task_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="INIT_NEW_OBJECTIVE...",
            font=ctk.CTkFont(family=FONT_MONO, size=14),
            height=40,
            corner_radius=0,
            border_width=1,
            fg_color=COLOR_BG,
            border_color=COLOR_DIM,
            text_color=COLOR_ACCENT,
            placeholder_text_color=COLOR_DIM
        )
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        self.task_entry.bind("<FocusIn>", lambda e: self.task_entry.configure(border_color=COLOR_ACCENT))
        self.task_entry.bind("<FocusOut>", lambda e: self.task_entry.configure(border_color=COLOR_DIM))
        
        # Priority selector
        self.new_priority = ctk.StringVar(value="NONE")
        priority_menu = ctk.CTkOptionMenu(
            input_frame,
            variable=self.new_priority,
            values=["NONE", "LOW", "MED", "HIGH"],
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            width=80,
            height=40,
            corner_radius=0,
            fg_color=COLOR_CARD,
            button_color=COLOR_DIM,
            button_hover_color=COLOR_ACCENT,
            dropdown_fg_color=COLOR_BG,
            dropdown_text_color=COLOR_ACCENT,
            dropdown_hover_color=COLOR_DIM,
            text_color=COLOR_ACCENT
        )
        priority_menu.pack(side="left", padx=(0, 10))
        
        self.add_btn = MatrixButton(
            input_frame,
            text="EXEC",
            width=60,
            height=40,
            command=self.add_task
        )
        self.add_btn.pack(side="right")
        
        # Filter Tabs
        filter_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(5, 12))
        
        self.filter_btns = {}
        filters = [
            ("all", "ALL"),
            ("pending", "ACTIVE"),
            ("completed", "DONE"),
            ("high", "!HIGH"),
            ("overdue", "OVERDUE")
        ]
        
        for fid, text in filters:
            btn = ctk.CTkButton(
                filter_frame,
                text=text,
                font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
                height=28,
                width=70,
                corner_radius=0,
                fg_color=COLOR_BG,
                text_color=COLOR_DIM,
                border_width=1,
                border_color=COLOR_BORDER,
                command=lambda f=fid: self.set_filter(f)
            )
            btn.pack(side="left", padx=(0, 4))
            self.filter_btns[fid] = btn

        # Task List
        self.list_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=COLOR_DIM,
            scrollbar_button_hover_color=COLOR_ACCENT,
            border_width=1,
            border_color=COLOR_BORDER
        )
        self.list_frame.pack(fill="both", expand=True)

        # Footer
        self.clear_btn = MatrixButton(
            self.main_frame,
            text="PURGE COMPLETED PROTOCOLS",
            height=35,
            command=self.clear_completed
        )

    def _on_search(self, e=None):
        self.search_query = self.search_entry.get().strip().lower()
        self.render_tasks()
    
    def _clear_search(self):
        self.search_entry.delete(0, "end")
        self.search_query = ""
        self.render_tasks()

    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Migrate old tasks to new format
                    for task in data:
                        if "priority" not in task:
                            task["priority"] = "NONE"
                        if "due_date" not in task:
                            task["due_date"] = None
                    return data
            except Exception as e:
                print(f"Error loading tasks: {e}")
                return []
        return []
    
    def save_tasks(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task(self):
        text = self.task_entry.get().strip()
        if not text:
            return
        
        task = {
            "id": str(datetime.now().timestamp()),
            "text": text,
            "completed": False,
            "priority": self.new_priority.get(),
            "due_date": None,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        self.tasks.insert(0, task)
        self.save_tasks()
        self.task_entry.delete(0, "end")
        self.new_priority.set("NONE")
        
        if self.sound_enabled:
            play_sound("add")
        
        self.render_tasks()
    
    def toggle_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = not task["completed"]
                if task["completed"]:
                    task["completed_at"] = datetime.now().isoformat()
                    if self.sound_enabled:
                        play_sound("complete")
                else:
                    task["completed_at"] = None
                break
        self.save_tasks()
        self.render_tasks()
    
    def delete_task(self, task_id):
        # Find the task to get its name for the dialog
        task_text = "this task"
        for t in self.tasks:
            if t["id"] == task_id:
                task_text = t["text"][:35] + "..." if len(t["text"]) > 35 else t["text"]
                break
        
        def do_delete():
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            self.save_tasks()
            if self.sound_enabled:
                play_sound("delete")
            self.render_tasks()
        
        ConfirmDialog(
            self,
            "DELETE_PROTOCOL",
            f"Permanently delete task:\n'{task_text}'?",
            do_delete
        )
    
    def edit_task(self, task_data):
        EditDialog(self, task_data, self._save_edit)
    
    def _save_edit(self, task_id, new_text, new_priority, new_due):
        for task in self.tasks:
            if task["id"] == task_id:
                task["text"] = new_text
                task["priority"] = new_priority
                task["due_date"] = new_due
                break
        self.save_tasks()
        if self.sound_enabled:
            play_sound("add")
        self.render_tasks()
    
    def clear_completed(self):
        self.tasks = [t for t in self.tasks if not t["completed"]]
        self.save_tasks()
        if self.sound_enabled:
            play_sound("delete")
        self.render_tasks()
    
    def set_filter(self, fid):
        self.current_filter = fid
        for key, btn in self.filter_btns.items():
            is_active = key == fid
            btn.configure(
                border_color=COLOR_ACCENT if is_active else COLOR_BORDER,
                text_color=COLOR_ACCENT if is_active else COLOR_DIM,
                fg_color="#002200" if is_active else COLOR_BG
            )
        if self.sound_enabled:
            play_sound("click")
        self.render_tasks()
    
    def get_filtered_tasks(self):
        filtered = self.tasks
        
        # Apply status filter
        if self.current_filter == "pending":
            filtered = [t for t in filtered if not t["completed"]]
        elif self.current_filter == "completed":
            filtered = [t for t in filtered if t["completed"]]
        elif self.current_filter == "high":
            filtered = [t for t in filtered if t.get("priority") == "HIGH" and not t["completed"]]
        elif self.current_filter == "overdue":
            today = date.today()
            result = []
            for t in filtered:
                if t["completed"]:
                    continue
                due = t.get("due_date")
                if due:
                    try:
                        due_date = datetime.strptime(due, "%Y-%m-%d").date()
                        if due_date < today:
                            result.append(t)
                    except:
                        pass
            filtered = result
        
        # Apply search filter
        if self.search_query:
            filtered = [t for t in filtered if self.search_query in t["text"].lower()]
        
        return filtered
    
    def update_stats(self):
        total = len(self.tasks)
        done = len([t for t in self.tasks if t["completed"]])
        pending = total - done
        high_priority = len([t for t in self.tasks if t.get("priority") == "HIGH" and not t["completed"]])
        
        # Count overdue
        today = date.today()
        overdue = 0
        for t in self.tasks:
            if t["completed"]:
                continue
            due = t.get("due_date")
            if due:
                try:
                    due_date = datetime.strptime(due, "%Y-%m-%d").date()
                    if due_date < today:
                        overdue += 1
                except:
                    pass
        
        percentage = int((done / total) * 100) if total > 0 else 0
        bar = ('=' * int(percentage/10)).ljust(10)
        
        stats_text = (
            f"{'='*50}\n"
            f"  TOTAL PROTOCOLS  : {total:03d}    |    HIGH PRIORITY : {high_priority:03d}\n"
            f"  ACTIVE THREADS   : {pending:03d}    |    OVERDUE       : {overdue:03d}\n"
            f"  COMPLETED        : {done:03d}    |    COMPLETION    : [{bar}] {percentage}%\n"
            f"{'='*50}"
        )
        self.stats_label.configure(text=stats_text)
        
        if done > 0:
            self.clear_btn.pack(fill="x", pady=(10, 0))
        else:
            self.clear_btn.pack_forget()

    def render_tasks(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        filtered = self.get_filtered_tasks()
        
        if not filtered:
            msg = "NO MATCHING RECORDS"
            if not self.tasks:
                msg = "SYSTEM IDLE. AWAITING INPUT."
            elif self.search_query:
                msg = f"NO RESULTS FOR: '{self.search_query.upper()}'"
            
            ctk.CTkLabel(
                self.list_frame,
                text=msg,
                font=ctk.CTkFont(family=FONT_MONO, size=14),
                text_color=COLOR_DIM
            ).pack(pady=40)
        else:
            for task in filtered:
                TaskItem(
                    self.list_frame,
                    task,
                    self.toggle_task,
                    self.delete_task,
                    self.edit_task
                ).pack(fill="x", pady=(0, 2))
        
        self.update_stats()


if __name__ == "__main__":
    # Create app but hide it initially
    app = ToDoApp()
    app.withdraw()  # Hide main window
    
    def on_boot_complete():
        app.deiconify()  # Show main window
        app.lift()
        app.focus_force()
        # Check for overdue notifications
        check_overdue_notifications(app.tasks)
    
    # Show boot screen
    boot = BootScreen(app, on_boot_complete)
    
    app.mainloop()
