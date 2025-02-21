import random
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---------------------
# DFS/backtracking functions (module level for multiprocessing)
# ---------------------

# Global counter for monitoring progress (each process has its own)
global_iterations = 0
start_time = time.time()

def dfs_extend(path, used, target_length, node_to_coord, grid, prev_direction, prefer_turn, diagonals_used):
    """
    Recursively extend path to the required target_length.
    - used: set of nodes already used.
    - prev_direction: the (dr, dc) of the last move (or None at start).
    - prefer_turn: if True, favor moves that change direction.
    - diagonals_used: dictionary mapping a square’s top-left coordinate to which diagonal type (1 or 2) is used.
    """
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
    
    # All 8 possible moves (N, NE, E, SE, S, SW, W, NW).
    directions = [(-1, 0), (-1, 1), (0, 1), (1, 1),
                  (1, 0), (1, -1), (0, -1), (-1, -1)]
    neighbors = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < grid_rows and 0 <= nc < grid_cols:
            neighbor = grid[nr][nc]
            if neighbor not in used:
                neighbors.append((neighbor, (dr, dc)))
    
    # Optionally prefer moves that change direction (to get a "squiggly" look)
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
            # Identify the 2x2 square (if one exists) where this diagonal move lies.
            r_min = min(r, node_to_coord[neighbor][0])
            c_min = min(c, node_to_coord[neighbor][1])
            if r_min <= grid_rows - 2 and c_min <= grid_cols - 2:
                square_key = (r_min, c_min)
                # Determine diagonal type:
                # Type 1: from top-left to bottom-right.
                # Type 2: from top-right to bottom-left.
                if (r, c) == (r_min, c_min) or node_to_coord[neighbor] == (r_min, c_min):
                    diag_type = 1
                elif (r, c) == (r_min, c_min+1) or node_to_coord[neighbor] == (r_min, c_min+1):
                    diag_type = 2
                else:
                    if (r, c) == (r_min+1, c_min+1) or node_to_coord[neighbor] == (r_min+1, c_min+1):
                        diag_type = 1
                    elif (r, c) == (r_min+1, c_min) or node_to_coord[neighbor] == (r_min+1, c_min):
                        diag_type = 2
                # Enforce the constraint: if a square already has a diagonal, it must match.
                if square_key in diagonals_used and diagonals_used[square_key] != diag_type:
                    continue
                if square_key not in diagonals_used:
                    diagonals_used[square_key] = diag_type
                    diag_set_here = True

        # Extend the path
        path.append(neighbor)
        used.add(neighbor)
        result = dfs_extend(path, used, target_length, node_to_coord, grid, direction, prefer_turn, diagonals_used)
        if result is not None:
            return result
        # Backtrack
        path.pop()
        used.remove(neighbor)
        if diag_set_here:
            del diagonals_used[square_key]
    return None

def dfs_for_strand(strand_name, strand_length, start_node, used, node_to_coord, grid, prefer_turn, diagonals_used):
    """
    Attempt to find a path of exactly strand_length for a given strand starting at start_node.
    """
    path = [start_node]
    used.add(start_node)
    result = dfs_extend(path, used, strand_length, node_to_coord, grid, None, prefer_turn, diagonals_used)
    if result is None:
        used.remove(start_node)
    return result

def check_spangram_constraint(path, grid):
    """
    For the "SPANGRAM" strand, require that the path touches either
    both the top and bottom or both the left and right boundaries.
    """
    top_nodes = set(grid[0])
    bottom_nodes = set(grid[-1])
    left_nodes = set(row[0] for row in grid)
    right_nodes = set(row[-1] for row in grid)
    path_set = set(path)
    return (path_set & top_nodes and path_set & bottom_nodes) or (path_set & left_nodes and path_set & right_nodes)

def backtrack_solve(sorted_strands, index, used, diagonals_used, solution, node_to_coord, grid, all_nodes):
    """
    Recursive backtracking to assign paths for strands starting at sorted_strands[index].
    """
    if index == len(sorted_strands):
        return True
    name, length = sorted_strands[index]
    remaining = list(all_nodes - used)
    random.shuffle(remaining)
    for start in remaining:
        path = dfs_for_strand(name, length, start, used, node_to_coord, grid, prefer_turn=True, diagonals_used=diagonals_used)
        if path is not None:
            if name.upper() == "SPANGRAM" and not check_spangram_constraint(path, grid):
                for node in path:
                    used.remove(node)
                continue
            solution[name] = path
            if backtrack_solve(sorted_strands, index + 1, used, diagonals_used, solution, node_to_coord, grid, all_nodes):
                return True
            for node in path:
                used.remove(node)
            solution.pop(name, None)
    return False

def search_from_first_start(first_start, sorted_strands, all_nodes, node_to_coord, grid):
    """
    This function fixes the starting node for the first (longest) strand
    and then runs backtracking for the remaining strands.
    Returns a solution dictionary if found; otherwise None.
    """
    used = set()
    diagonals_used = {}
    solution = {}
    name, length = sorted_strands[0]
    path = dfs_for_strand(name, length, first_start, used, node_to_coord, grid, prefer_turn=True, diagonals_used=diagonals_used)
    if path is None:
        return None
    if name.upper() == "SPANGRAM" and not check_spangram_constraint(path, grid):
        for node in path:
            used.remove(node)
        return None
    solution[name] = path
    if backtrack_solve(sorted_strands, 1, used, diagonals_used, solution, node_to_coord, grid, all_nodes):
        return solution
    else:
        return None

def solve_partition_parallel(strands, grid):
    """
    Partition the grid into disjoint paths for each strand.
    This version parallelizes the search over candidate starting nodes for the first strand.
    Returns a dictionary mapping strand names to paths, or None if no solution is found.
    """
    node_to_coord = {}
    for i, row in enumerate(grid):
        for j, node in enumerate(row):
            node_to_coord[node] = (i, j)
    all_nodes = set(node_to_coord.keys())
    # Sort strands by descending length (longer, more-constrained strands first)
    sorted_strands = sorted(strands, key=lambda x: x[1], reverse=True)
    candidates = list(all_nodes)
    random.shuffle(candidates)
    with ProcessPoolExecutor() as executor:
        futures = []
        for cand in candidates:
            futures.append(executor.submit(search_from_first_start, cand, sorted_strands, all_nodes, node_to_coord, grid))
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                # Found a solution; cancel remaining tasks.
                for f in futures:
                    f.cancel()
                return result
    return None

# ---------------------
# Main block: example data, solving, and visualization
# ---------------------
if __name__ == "__main__":
    # Define grid (8 rows x 6 columns)
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

    # Build strands list as [name, length]
    strands = [[word, len(word)] for word in words]
    strands.append(["SPANGRAM", len(spangram)])

    print("Starting parallel search...")
    solution = solve_partition_parallel(strands, grid)
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
                positions[node] = (j, -i)  # so row 0 is at the top

        G = nx.DiGraph()
        G.add_nodes_from(positions.keys())

        # Define colors for each strand.
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
        plt.legend(handles=patches, loc='upper right')
        plt.title("Parallel Partitioning of the Grid into Squiggly Strands")
        plt.axis("off")
        plt.show()
