import json
import random
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
from tkinter import filedialog, messagebox

class WordlePuzzle:
    launch_date = datetime(2021, 6, 19)
    
    def __init__(self, solution, print_date, editor):
        self.id = random.randint(100, 999)
        self.solution = solution
        self.print_date = print_date
        self.days_since_launch = (self.print_date - self.launch_date).days
        self.editor = editor

    def to_dict(self):
        return {
            "id": self.id,
            "solution": self.solution,
            "print_date": self.print_date.strftime("%Y-%m-%d"),
            "days_since_launch": self.days_since_launch,
            "editor": self.editor
        }
    
    def dump_json(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

def select_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                             filetypes=[("JSON files", "*.json")])
    if file_path:
        file_label.config(text=file_path)
        root.selected_file_path = file_path

def create_json():
    # Access the underlying entry widget to get the date string
    date_str = date_entry.entry.get()
    try:
        print_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        messagebox.showerror("Error", "Selected date is not in the expected format (YYYY-MM-DD).")
        return

    solution_word = word_entry.get()
    editor_name = editor_entry.get()
    file_path = getattr(root, "selected_file_path", None)
    
    if not (solution_word and editor_name and file_path):
        messagebox.showerror("Error", "Please fill in all fields and select a file location.")
        return
    
    puzzle = WordlePuzzle(solution_word, print_date, editor_name)
    try:
        puzzle.dump_json(file_path)
        messagebox.showinfo("Success", f"JSON file created at:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create JSON file:\n{e}")

# Create the main window using ttkbootstrap's Window for a modern look
root = ttk.Window("Wordle Puzzle JSON Creator", "flatly")

# Publish Date using ttkbootstrap's DateEntry widget (without textvariable)
ttk.Label(root, text="Publish Date:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
date_entry = DateEntry(root, bootstyle="info", dateformat='%Y-%m-%d')
date_entry.grid(row=0, column=1, padx=5, pady=5)

# Solution Word input
ttk.Label(root, text="Solution Word:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
word_entry = ttk.Entry(root)
word_entry.grid(row=1, column=1, padx=5, pady=5)

# Editor Name input
ttk.Label(root, text="Editor Name:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
editor_entry = ttk.Entry(root)
editor_entry.grid(row=2, column=1, padx=5, pady=5)

# File location selection
ttk.Button(root, text="Select File Location", command=select_file).grid(row=3, column=0, columnspan=2, padx=5, pady=5)
file_label = ttk.Label(root, text="No file selected", bootstyle="secondary")
file_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# Create JSON File button
ttk.Button(root, text="Create JSON File", command=create_json).grid(row=5, column=0, columnspan=2, padx=5, pady=10)

root.mainloop()
