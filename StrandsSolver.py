import random
import time
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Global counter for monitoring progress.
global_iterations = 0
start_time = time.time()

# ---------------------
# DFS/backtracking functions
# ---------------------

def dfs_extend(path, used, target_length, node_to_coord, grid, prev_direction, prefer_turn, diagonals_used):
    global global_iterations, start_time
    global_iterations += 1
    if global_iterations % 1000000 == 0:
        elapsed = time.time() - start_time
        print(f"[PID {time.process_time()}] Iterations: {global_iterations}, Elapsed: {elapsed:.2f}s")
    
    if len(path) == target_length:
        return list(path)
    
    current = path[-1]
    grid_rows = len(grid)
    grid_cols = len(grid[0])
    r, c = node_to_coord[current]
    
    # All 8 possible moves.
    directions = [(-1, 0), (-1, 1), (0, 1), (1, 1),
                  (1, 0), (1, -1), (0, -1), (-1, -1)]
    neighbors = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < grid_rows and 0 <= nc < grid_cols:
            neighbor = grid[nr][nc]
            if neighbor not in used:
                neighbors.append((neighbor, (dr, dc)))
    
    # Optionally favor moves that change direction.
    if prev_direction is not None and prefer_turn:
        turning = []
        straight = []
        for neighbor, direction in neighbors:
            if direction == prev_direction:
                straight.append((neighbor, direction))
            else:
                turning.append((neighbor, direction))
        random.shuffle(turning)
        random.shuffle(straight)
        neighbors = turning + straight
    else:
        random.shuffle(neighbors)
    
    for neighbor, direction in neighbors:
        is_diagonal = (abs(direction[0]) == 1 and abs(direction[1]) == 1)
        diag_set_here = False
        square_key = None
        diag_type = None
        if is_diagonal:
            # Identify the 2x2 square (if it exists) where this diagonal move lies.
            r_min = min(r, node_to_coord[neighbor][0])
            c_min = min(c, node_to_coord[neighbor][1])
            if r_min <= grid_rows - 2 and c_min <= grid_cols - 2:
                square_key = (r_min, c_min)
                # Determine diagonal type:
                if (r, c) == (r_min, c_min) or node_to_coord[neighbor] == (r_min, c_min):
                    diag_type = 1
                elif (r, c) == (r_min, c_min+1) or node_to_coord[neighbor] == (r_min, c_min+1):
                    diag_type = 2
                else:
                    if (r, c) == (r_min+1, c_min+1) or node_to_coord[neighbor] == (r_min+1, c_min+1):
                        diag_type = 1
                    elif (r, c) == (r_min+1, c_min) or node_to_coord[neighbor] == (r_min+1, c_min):
                        diag_type = 2
                # Enforce diagonal constraint.
                if square_key in diagonals_used and diagonals_used[square_key] != diag_type:
                    continue
                if square_key not in diagonals_used:
                    diagonals_used[square_key] = diag_type
                    diag_set_here = True

        # Extend the path.
        path.append(neighbor)
        used.add(neighbor)
        result = dfs_extend(path, used, target_length, node_to_coord, grid, direction, prefer_turn, diagonals_used)
        if result is not None:
            return result
        # Backtrack.
        path.pop()
        used.remove(neighbor)
        if diag_set_here:
            del diagonals_used[square_key]
    return None

def dfs_for_strand(strand_name, strand_length, start_node, used, node_to_coord, grid, prefer_turn, diagonals_used):
    path = [start_node]
    used.add(start_node)
    result = dfs_extend(path, used, strand_length, node_to_coord, grid, None, prefer_turn, diagonals_used)
    if result is None:
        used.remove(start_node)
    return result

def check_spangram_constraint(path, grid, spangram_direction):
    """
    Existing spangram rule: enforce that the path touches both boundaries
    (either left/right or top/bottom as specified).
    """
    top_nodes = set(grid[0])
    bottom_nodes = set(grid[-1])
    left_nodes = set(row[0] for row in grid)
    right_nodes = set(row[-1] for row in grid)
    path_set = set(path)

    if spangram_direction == "left-right":
        return path_set & left_nodes and path_set & right_nodes
    elif spangram_direction == "top-bottom":
        return path_set & top_nodes and path_set & bottom_nodes
    else:
        raise ValueError("Invalid spangram_direction. Use 'left-right' or 'top-bottom'.")

# ---------------------
# New function: additional spangram separation check
# ---------------------
def check_spangram_separation_rule(path, grid, node_to_coord, remaining_strands, min_free=10):
    """
    After placing the spangram, ensure that removing its nodes splits the grid into exactly two 
    connected free regions, each with at least min_free nodes, and that the free regions can be 
    exactly filled by some combination of the remaining strands.
    """
    used = set(path)
    all_nodes = set(node for row in grid for node in row)
    free_nodes = all_nodes - used
    free_components = []
    visited = set()
    directions = [(-1, 0), (-1, 1), (0, 1), (1, 1),
                  (1, 0), (1, -1), (0, -1), (-1, -1)]
    for node in free_nodes:
        if node in visited:
            continue
        comp_size = 0
        stack = [node]
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            comp_size += 1
            r, c = node_to_coord[cur]
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    neighbor = grid[nr][nc]
                    if neighbor in free_nodes and neighbor not in visited:
                        stack.append(neighbor)
        free_components.append(comp_size)
    # The spangram must split the grid into exactly two free regions.
    if len(free_components) != 2:
        return False
    # Each region must have at least min_free nodes.
    if any(comp_size < min_free for comp_size in free_components):
        return False
    # Ensure that the free regions can be exactly filled by the remaining strands.
    if not can_partition_components(free_components, remaining_strands):
        return False
    return True

# ---------------------
# Connectivity and feasibility checks
# ---------------------

def get_free_components(used, grid, node_to_coord):
    all_nodes = set(node for row in grid for node in row)
    free_nodes = all_nodes - used
    components = []
    visited = set()
    directions = [(-1, 0), (-1, 1), (0, 1), (1, 1),
                  (1, 0), (1, -1), (0, -1), (-1, -1)]
    for node in free_nodes:
        if node in visited:
            continue
        comp_size = 0
        stack = [node]
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            comp_size += 1
            r, c = node_to_coord[cur]
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    neighbor = grid[nr][nc]
                    if neighbor in free_nodes and neighbor not in visited:
                        stack.append(neighbor)
        components.append(comp_size)
    return components

def can_partition_components(component_sizes, strands):
    if not component_sizes:
        return len(strands) == 0
    component_sizes = sorted(component_sizes, reverse=True)
    target = component_sizes[0]
    
    subsets = []
    def find_subsets(i, current, current_sum):
        if current_sum == target:
            subsets.append(current[:])
            return
        if i >= len(strands) or current_sum > target:
            return
        current.append(i)
        find_subsets(i+1, current, current_sum + strands[i])
        current.pop()
        find_subsets(i+1, current, current_sum)
    find_subsets(0, [], 0)
    if not subsets:
        return False
    for subset in subsets:
        remaining = [strands[i] for i in range(len(strands)) if i not in subset]
        if can_partition_components(component_sizes[1:], remaining):
            return True
    return False

# ---------------------
# Backtracking with connectivity pruning (single-threaded)
# ---------------------

def backtrack_solve(sorted_strands, index, used, diagonals_used, solution, node_to_coord, grid, all_nodes, spangram_direction):
    if index == len(sorted_strands):
        return True

    # Connectivity lookahead.
    remaining_strands_lengths = [length for (_, length) in sorted_strands[index:]]
    free_components = get_free_components(used, grid, node_to_coord)
    if free_components and min(free_components) < min(remaining_strands_lengths):
        return False
    if not can_partition_components(free_components, remaining_strands_lengths):
        return False

    name, length = sorted_strands[index]
    remaining_candidates = list(all_nodes - used)
    random.shuffle(remaining_candidates)
    for start in remaining_candidates:
        path = dfs_for_strand(name, length, start, used, node_to_coord, grid, prefer_turn=True, diagonals_used=diagonals_used)
        if path is not None:
            # --- If this is the spangram, apply both the original and new rules ---
            if name.upper() == "SPANGRAM":
                if not check_spangram_constraint(path, grid, spangram_direction):
                    for node in path:
                        used.remove(node)
                    continue
                # Compute remaining strands (all except the spangram).
                remaining_strands = [length for (nm, length) in sorted_strands if nm.upper() != "SPANGRAM"]
                if not check_spangram_separation_rule(path, grid, node_to_coord, remaining_strands, min_free=10):
                    for node in path:
                        used.remove(node)
                    continue

            solution[name] = path
            if backtrack_solve(sorted_strands, index + 1, used, diagonals_used, solution, node_to_coord, grid, all_nodes, spangram_direction):
                return True
            # Backtrack.
            for node in path:
                used.remove(node)
            solution.pop(name, None)
    return False

def solve_partition(strands, grid, spangram_direction):
    """
    Partition the grid into disjoint paths for each strand. The strands are reordered so that
    the spangram is placed first.
    """
    node_to_coord = {}
    for i, row in enumerate(grid):
        for j, node in enumerate(row):
            node_to_coord[node] = (i, j)
    all_nodes = set(node for row in grid for node in row)
    # --- Reorder strands so that SPANGRAM is always first ---
    spangram_strands = [s for s in strands if s[0].upper() == "SPANGRAM"]
    other_strands = [s for s in strands if s[0].upper() != "SPANGRAM"]
    # You can still sort the remaining strands by descending length.
    other_strands = sorted(other_strands, key=lambda x: x[1], reverse=True)
    sorted_strands = spangram_strands + other_strands

    used = set()
    diagonals_used = {}
    solution = {}
    if backtrack_solve(sorted_strands, 0, used, diagonals_used, solution, node_to_coord, grid, all_nodes, spangram_direction):
        return solution
    else:
        return None

# ---------------------
# Main block: example data, solving, and visualization
# ---------------------

if __name__ == "__main__":
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
    
    # Define words and a spangram so that total letters equal 48.
    words = [
        "CARROTS",
        "CELERY",
        "NOODLES",
        "ONIONS",
        "PEPPER",
        "STOCK"
    ]
    spangram = "CHICKENSOUP"  # Special strand with extra wall constraint

    # Build strands list as [name, length].
    strands = [[word, len(word)] for word in words]
    strands.append(["SPANGRAM", len(spangram)])
    
    print("Starting improved search with connectivity pruning...")
    solution = solve_partition(strands, grid, spangram_direction="top-bottom")
    if solution is None:
        print("No solution found.")
    else:
        for strand, path in solution.items():
            print(f"Strand {strand}: {path}")
        
        # ---------------------
        # Visualization using networkx
        # ---------------------
        positions = {}
        for i, row in enumerate(grid):
            for j, node in enumerate(row):
                positions[node] = (j, -i)  # so that row 0 is at the top

        G = nx.DiGraph()
        G.add_nodes_from(positions.keys())

        strand_colors = {
            'CARROTS': 'red',
            'CELERY': 'blue',
            'NOODLES': 'green',
            'ONIONS': 'orange',
            'PEPPER': 'purple',
            'STOCK': 'brown',
            'SPANGRAM': 'cyan'
        }

        for strand, path in solution.items():
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i+1]
                G.add_edge(u, v, strand=strand)

        plt.figure(figsize=(8, 6))
        nx.draw_networkx_nodes(G, pos=positions, node_size=500, node_color='lightgray')
        nx.draw_networkx_edges(G, pos=positions, edge_color='lightgray', alpha=0.3, arrows=True)
        for strand, color in strand_colors.items():
            strand_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('strand') == strand]
            if strand_edges:
                nx.draw_networkx_edges(G, pos=positions, edgelist=strand_edges,
                                       edge_color=color, width=2, arrows=True,
                                       arrowstyle='->', connectionstyle='arc3,rad=0.1')
        nx.draw_networkx_labels(G, pos=positions)
        patches = [mpatches.Patch(color=color, label=strand) for strand, color in strand_colors.items()]
        plt.title("Improved Grid Partitioning with Connectivity Pruning")
        plt.axis("off")
        plt.show()
