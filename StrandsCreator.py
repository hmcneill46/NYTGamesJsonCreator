import random
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches
import StrandsSolver
import StrandsWordFinder
from WordTrie import WordTrie

class StrandsPuzzle:
    def __init__(self, print_date, editor):
        self.status = "OK"
        self.id = random.randint(100, 999)
        self.print_date = print_date
        self.themeWords = []
        self.editor = editor
        self.constructors = editor
        self.spangram = ""
        self.clue = ""
        self.startingBoard = []
        self.solutions = []
        self.themeCoords = {}
        self.spangramCoords = []
        self.strandsSolution = None
        self.board = [[None for _ in range(6)] for _ in range(8)]
        self.wordLenMax = 19
        self.wordLenMin = 4
        self.board_2d_list = []

        self.wordTrie = WordTrie()
        self.reducedWordTrie = WordTrie()
        with open("english_words.txt", "r") as file:
            for line in file:
                word = line.strip()
                if not word:  # Skip empty lines.
                    continue
                if len(word) > self.wordLenMax:
                    continue
                if len(word) < self.wordLenMin:
                    continue
                self.wordTrie.insert(word)

    def add_theme_words(self, themeWords: list):
        self.themeWords = themeWords
        for themeWord in themeWords:
            self.reducedWordTrie.insert(themeWord)
            self.themeCoords[themeWord] = [[None, None] for _ in range(len(themeWord))]

    def add_spangram(self, spangram):
        self.spangram = spangram
        self.reducedWordTrie.insert(spangram)
        self.spangramCoords = [[None, None] for _ in range(len(spangram))]

    def add_clue(self, clue):
        self.clue = clue

    def load_solution(self, file_path, objective_value):
        with open(file_path, 'r') as file:
            data = json.load(file)
        for entry in data:
            if entry["objective"] == objective_value:
                print("Using solution with objective value: ", objective_value)
                self.strandsSolution = entry["solution"]
                return self.strandsSolution
        return None

    def solve_for_strands(self, spangram_direction):
        grid = [
            [1, 2, 3, 4, 5, 6],
            [7, 8, 9, 10, 11, 12],
            [13, 14, 15, 16, 17, 18],
            [19, 20, 21, 22, 23, 24],
            [25, 26, 27, 28, 29, 30],
            [31, 32, 33, 34, 35, 36],
            [37, 38, 39, 40, 41, 42],
            [43, 44, 45, 46, 47, 48]
        ]
        strands = [[word, len(word)] for word in self.themeWords]
        strands.append(["SPANGRAM", len(self.spangram)])
        print(strands)
        print(f"{sum([strand[1] for strand in strands])} letters in total")
        while self.validate_found_solution() == False:
            self.strandsSolution = None
            while self.strandsSolution == None:
                self.strandsSolution = StrandsSolver.solve_partition(strands, grid, spangram_direction)
            self.calculate_theme_coords()
            self.calculate_spangram_coords()
            self.calculate_starting_board()
        print(self.strandsSolution)
        return(self.strandsSolution)

    def calculate_starting_board(self):
        startingBoardGrid = [[None for _ in range(6)] for _ in range(8)]
        for word_index, word in enumerate(self.themeWords):
            for coord_index, coord in enumerate(self.themeCoords[word]):
                startingBoardGrid[coord[0]][coord[1]] = word[coord_index]
        for coord_index, coord in enumerate(self.spangramCoords):
            startingBoardGrid[coord[0]][coord[1]] = self.spangram[coord_index]
        self.startingBoard = ["".join(row) for row in startingBoardGrid]
        self.board_2d_list = [list(row) for row in self.startingBoard]

    def calculate_theme_coords(self):
        for themeWord in self.themeWords:
            for index, node in enumerate(self.strandsSolution[themeWord]):
                self.themeCoords[themeWord][index] = index_to_coordinates(node, 6)

    def calculate_spangram_coords(self):
        for index, node in enumerate(self.strandsSolution["SPANGRAM"]):
            self.spangramCoords[index] = index_to_coordinates(node, 6)

    def to_dict(self):
        return {
            "status": self.status,
            "id": self.id,
            "print_date": self.print_date.strftime("%Y-%m-%d"),
            "themeWords": self.themeWords,
            "editor": self.editor,
            "constructors": self.constructors,
            "spangram": self.spangram,
            "clue": self.clue,
            "startingBoard": self.startingBoard,
            "solutions": self.solutions,
            "themeCoords": self.themeCoords,
            "spangramCoords": self.spangramCoords
        }

    def dump_json(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def get_loaded_solution(self):
        return self.strandsSolution

    def validate_found_solution(self):
        return StrandsWordFinder.validatePuzzle(self.board_2d_list, self.reducedWordTrie, self.themeWords + [self.spangram])
    def find_all_possible_words(self):
        self.solutions = sorted(list(StrandsWordFinder.calculateSetOfWords(self.board_2d_list, self.wordTrie)))


def preview_puzzle_solution(puzzle: StrandsPuzzle):
    solution = puzzle.get_loaded_solution()
    grid = [
        [1, 2, 3, 4, 5, 6],
        [7, 8, 9, 10, 11, 12],
        [13, 14, 15, 16, 17, 18],
        [19, 20, 21, 22, 23, 24],
        [25, 26, 27, 28, 29, 30],
        [31, 32, 33, 34, 35, 36],
        [37, 38, 39, 40, 41, 42],
        [43, 44, 45, 46, 47, 48]
    ]

    gridLabels = []
    for row in puzzle.startingBoard:
        gridLabels.append([cell if cell is not None else '' for cell in row])

    for strand, path in solution.items():
        print(f"Strand {strand}: {path}")

    positions = {}
    for i, row in enumerate(grid):
        for j, node in enumerate(row):
            positions[node] = (j, -i)  # so row 0 is at the top

    G = nx.DiGraph()
    G.add_nodes_from(positions.keys())

    # Define colors for each strand.
    TABLEAU_COLORS = [
        'blue',
        'orange',
        'green',
        'red',
        'purple',
        'brown',
        'pink',
        'gray',
        'olive',
        'cyan'
    ]

    strand_colors = {strand: TABLEAU_COLORS[i] for i, (strand, _) in enumerate(solution.items())}

    for strand, path in solution.items():
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            G.add_edge(u, v, strand=strand)

    plt.figure(figsize=(6, 10))  # Increase figure size to provide more space
    nx.draw_networkx_nodes(G, pos=positions, node_size=500, node_color='lightgray')
    nx.draw_networkx_edges(G, pos=positions, edge_color='lightgray', alpha=0.3, arrows=True)
    for strand, color in strand_colors.items():
        strand_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('strand') == strand]
        if strand_edges:
            nx.draw_networkx_edges(G, pos=positions, edgelist=strand_edges,
                                    edge_color=color, width=2, arrows=True,
                                    arrowstyle='->', connectionstyle='arc3,rad=0.1')
    
    # Create a dictionary for node labels using gridLabels
    node_labels = {}
    for i, row in enumerate(grid):
        for j, node in enumerate(row):
            node_labels[node] = gridLabels[i][j]

    nx.draw_networkx_labels(G, pos=positions, labels=node_labels)
    #patches = [mpatches.Patch(color=color, label=strand) for strand, color in strand_colors.items()]
    #plt.legend(handles=patches, loc='lower right', bbox_to_anchor=(1, -0.18))  # Moves the legend outside the plot
    plt.title("Strands Puzzle Solution")
    plt.axis("off")
    plt.show()


def index_to_coordinates(index, num_columns):
    row = (index - 1) // num_columns
    col = (index - 1) % num_columns
    return (row, col)

# Global variable to store the generated puzzle for previewing
current_puzzle = None

def select_file(root, file_label):
    file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                             filetypes=[("JSON files", "*.json")])
    if file_path:
        file_label.config(text=file_path)
        root.selected_file_path = file_path

def generate_json(date_entry, editor_entry, theme_entry, spangram_entry, clue_entry, direction_var, file_label, root):
    global current_puzzle

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

    theme_words_raw = theme_entry.get()
    if not theme_words_raw:
        messagebox.showerror("Error", "Theme words are required. Please enter a comma-separated list.")
        return
    theme_words = [word.strip().upper() for word in theme_words_raw.split(",") if word.strip()]
    if not theme_words:
        messagebox.showerror("Error", "Please enter valid theme words.")
        return

    spangram = spangram_entry.get().upper()
    if not spangram:
        messagebox.showerror("Error", "Spangram is required.")
        return

    clue = clue_entry.get()
    if not clue:
        messagebox.showerror("Error", "Clue is required.")
        return

    total_letters = len(spangram) + sum(len(word) for word in theme_words)
    if total_letters != 48:
        messagebox.showerror("Error", f"Total letters count is {total_letters}, but it must be 48.")
        return
    if len(spangram) < 6:
        messagebox.showerror("Error", "Spangram must be at least 6 letters long.")
        return
    for word in theme_words:
        if len(word) < 4:
            messagebox.showerror("Error", "All theme words must be at least 4 letters long.")
            return

    try:
        puzzle = StrandsPuzzle(print_date, editor_name)
        puzzle.add_theme_words(theme_words)
        puzzle.add_spangram(spangram)
        puzzle.add_clue(clue)
        direction = direction_var.get()
        puzzle.solve_for_strands(direction)
        puzzle.find_all_possible_words()
    except Exception as e:
        messagebox.showerror("Error", f"Error creating puzzle instance: {e}")
        return

    file_path = getattr(root, "selected_file_path", None)
    if not file_path:
        messagebox.showerror("Error", "Please select a file location to save the JSON file.")
        return

    try:
        puzzle.dump_json(file_path)
        messagebox.showinfo("Success", f"JSON file created at:\n{file_path}")
        current_puzzle = puzzle
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create JSON file:\n{e}")

def preview_puzzle():
    if current_puzzle is None:
        messagebox.showerror("Error", "No puzzle generated yet. Please generate a puzzle first.")
        return
    try:
        preview_puzzle_solution(current_puzzle)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to preview puzzle:\n{e}")

def run_gui():
    root = ttk.Window("Strands Puzzle Creator", "flatly")
    root.geometry("640x520")

    canvas = tk.Canvas(root)
    vsb = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scrollable_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scrollable_frame.bind("<Configure>", on_frame_configure)

    ttk.Label(scrollable_frame, text="Editor Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    editor_entry = ttk.Entry(scrollable_frame)
    editor_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(scrollable_frame, text="Publish Date:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    date_entry = DateEntry(scrollable_frame, bootstyle="info", dateformat='%Y-%m-%d')
    date_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(scrollable_frame, text="Theme Words (comma-separated):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    theme_entry = ttk.Entry(scrollable_frame, width=40)
    theme_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(scrollable_frame, text="Spangram:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    spangram_entry = ttk.Entry(scrollable_frame, width=40)
    spangram_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(scrollable_frame, text="Clue:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    clue_entry = ttk.Entry(scrollable_frame, width=40)
    clue_entry.grid(row=4, column=1, padx=5, pady=5)

    ttk.Label(scrollable_frame, text="Spangram Direction:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
    direction_var = tk.StringVar(value="left-right")
    direction_dropdown = ttk.Combobox(scrollable_frame, textvariable=direction_var, values=["left-right", "top-bottom"], state="readonly")
    direction_dropdown.grid(row=5, column=1, padx=5, pady=5)

    ttk.Button(scrollable_frame, text="Select File Location", command=lambda: select_file(root, file_label)).grid(row=6, column=0, columnspan=2, padx=5, pady=5)
    file_label = ttk.Label(scrollable_frame, text="No file selected", bootstyle="secondary")
    file_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    ttk.Button(scrollable_frame, text="Generate JSON File", command=lambda: generate_json(date_entry, editor_entry, theme_entry, spangram_entry, clue_entry, direction_var, file_label, root)).grid(row=8, column=0, columnspan=2, padx=5, pady=10)

    ttk.Button(scrollable_frame, text="Preview Puzzle", command=preview_puzzle).grid(row=9, column=0, columnspan=2, padx=5, pady=10)

    root.mainloop()


# --- Entry Point ---

if __name__ == '__main__':
    run_gui()
