import random
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry

class ConnectionsPuzzle:
    def __init__(self, print_date, editor):
        self.status = "OK"
        self.id = random.randint(100, 999)
        self.print_date = print_date
        self.editor = editor
        self.categories = [{}, {}, {}, {}]
        self.avaliableGridPositions = [i for i in range(16)]
        self.catagoryPointer = 0

    def add_category(self, category_title, cards: list):
        if self.catagoryPointer > 3:
            self.status = "Error: Too many categories"
            return
        if len(cards) != 4:
            self.status = "Error: Incorrect number of cards"
            return
        self.categories[self.catagoryPointer]["title"] = category_title.upper()
        self.categories[self.catagoryPointer]["cards"] = [{}, {}, {}, {}]
        for index, word in enumerate(cards):
            self.categories[self.catagoryPointer]["cards"][index]["content"] = word.upper()
            self.categories[self.catagoryPointer]["cards"][index]["position"] = random.choice(self.avaliableGridPositions)
            self.avaliableGridPositions.remove(self.categories[self.catagoryPointer]["cards"][index]["position"])
        self.catagoryPointer += 1

    def to_dict(self):
        return {
            "status": self.status,
            "id": self.id,
            "print_date": self.print_date.strftime("%Y-%m-%d"),
            "editor": self.editor,
            "categories": self.categories
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
    # Retrieve the date string from the underlying entry widget of DateEntry.
    date_str = date_entry.entry.get()
    try:
        print_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        messagebox.showerror("Error", "Selected date is not in the expected format (YYYY-MM-DD).")
        return

    editor_name = editor_entry.get()
    if not editor_name:
        messagebox.showerror("Error", "Editor Name is required.")
        return

    # Create a puzzle instance
    puzzle = ConnectionsPuzzle(print_date=print_date, editor=editor_name)

    # Retrieve category title and card words for each of the 4 categories.
    for i in range(4):
        cat_title = category_title_entries[i].get()
        card_words = [card_entries[i][j].get() for j in range(4)]
        if not cat_title:
            messagebox.showerror("Error", f"Category {i+1} title is required.")
            return
        if any(not word for word in card_words):
            messagebox.showerror("Error", f"All 4 card words are required for Category {i+1}.")
            return
        puzzle.add_category(cat_title, card_words)

    file_path = getattr(root, "selected_file_path", None)
    if not file_path:
        messagebox.showerror("Error", "Please select a file location to save the JSON file.")
        return

    try:
        puzzle.dump_json(file_path)
        messagebox.showinfo("Success", f"JSON file created at:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create JSON file:\n{e}")

# Create the main window using ttkbootstrap's Window for a modern look.
root = ttk.Window("Connections Puzzle JSON Creator", "flatly")
root.geometry("600x600")  # Set an initial size

# Create a canvas and scrollbar for scrolling support.
canvas = tk.Canvas(root)
vsb = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set)
vsb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Create a frame inside the canvas which will hold all the widgets.
scrollable_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Make sure the canvas scrolls whenever the size of the scrollable frame changes.
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
scrollable_frame.bind("<Configure>", on_frame_configure)

# Now, add widgets to the scrollable_frame instead of root.
# Editor Name and Publish Date
ttk.Label(scrollable_frame, text="Editor Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
editor_entry = ttk.Entry(scrollable_frame)
editor_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(scrollable_frame, text="Publish Date:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
date_entry = DateEntry(scrollable_frame, bootstyle="info", dateformat='%Y-%m-%d')
date_entry.grid(row=1, column=1, padx=5, pady=5)

# Prepare lists to hold the Entry widgets for category titles and cards.
category_title_entries = []
card_entries = []  # List of lists; one list per category

# Create 4 sections for the categories.
for i, difficulty in enumerate(["Easy", "Medium", "Hard", "Very Hard"]):
    frame = ttk.Labelframe(scrollable_frame, text=f"Difficulty {difficulty}", padding=10)
    frame.grid(row=2+i, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    
    # Category title input
    ttk.Label(frame, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    title_entry = ttk.Entry(frame, width=20)
    title_entry.grid(row=0, column=1, padx=5, pady=5)
    category_title_entries.append(title_entry)
    
    # Card words input (4 cards per category)
    cards_for_category = []
    for j in range(4):
        ttk.Label(frame, text=f"Card {j+1}:").grid(row=j+1, column=0, sticky="e", padx=5, pady=2)
        card_entry = ttk.Entry(frame, width=20)
        card_entry.grid(row=j+1, column=1, padx=5, pady=2)
        cards_for_category.append(card_entry)
    card_entries.append(cards_for_category)

# File selection and creation buttons
ttk.Button(scrollable_frame, text="Select File Location", command=select_file)\
    .grid(row=6, column=0, columnspan=2, padx=5, pady=5)
file_label = ttk.Label(scrollable_frame, text="No file selected", bootstyle="secondary")
file_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
ttk.Button(scrollable_frame, text="Create JSON File", command=create_json)\
    .grid(row=8, column=0, columnspan=2, padx=5, pady=10)

root.mainloop()
