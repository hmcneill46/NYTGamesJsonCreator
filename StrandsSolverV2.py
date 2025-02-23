import random
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches
from tqdm import tqdm

class StrandsSolverV2:
    def __init__(self, themeWords, spangram, grid_dimensions, spangram_direction):
        letterCount = len(spangram)
        for word in themeWords:
            letterCount += len(word)
        if letterCount != grid_dimensions[0] * grid_dimensions[1]:
            raise ValueError(f"The total number of letters in the theme words and spangram must equal the number of cells in the grid. \n Total letters: {letterCount}\n Grid size:{grid_dimensions[0]} x {grid_dimensions[1]} \n Required Letter Total: {grid_dimensions[0] * grid_dimensions[1]}")

        if spangram_direction == "horizontal":
            self.spangramDirection = random.choice([[0, 1], [0, -1]])
            if len(spangram) < grid_dimensions[1]:
                raise ValueError("The spangram must be longer than the grid width when the direction is horizontal.")
        elif spangram_direction == "vertical":
            self.spangramDirection = random.choice([[1, 0], [-1, 0]])
            if len(spangram) < grid_dimensions[0]:
                raise ValueError("The spangram must be longer than the grid height when the direction is vertical.")
        else:
            raise ValueError("Invalid spangram direction. Must be 'horizontal' or 'vertical'.")

        self.themeWords = themeWords
        self.spangram = spangram
        self.grid_dimensions = grid_dimensions
        self.strandLengths = [len(word) for word in themeWords]
        self.spangramLength = len(spangram)
        self.spangramSlack = self.get_initial_spangram_slack()   
        self.possibleStrandStartNodes = self.get_possible_strand_start_nodes()

        self.permittedDirections = [[-1, -1], [-1, 0], [-1, 1],
                                    [0, -1],           [0, 1],
                                    [1, -1],  [1, 0],  [1, 1]]
        
        
        calculatedStrandsGraph = self.calculate_strands_graph(self.spangramSlack, self.spangramDirection, self.grid_dimensions)
        self.grid = calculatedStrandsGraph[0]
        self.strandPaths = calculatedStrandsGraph[1]
        self.spangramPath = calculatedStrandsGraph[2]
        
        #self.test_spanagram_failure_rate(self.spangramSlack, self.spangramDirection, self.grid_dimensions, 1000000)
    
    def calculate_strands_graph(self, spangramSlack, spangramDirection, grid_dimensions):
        grid = {(y, x): None for y in range(grid_dimensions[0]) for x in range(grid_dimensions[1])}
        strandPaths = {themeWord: [] for themeWord in self.themeWords}

        # Calculate Spangram Path
        startingNode = random.choice(self.possibleStrandStartNodes)
        spangramSlack = self.update_spangram_slack(spangramSlack, spangramDirection, startingNode, grid_dimensions)
        spangramPath = self.calculate_spangram_path(self.spangramLength, grid, startingNode, self.calculate_new_permitted_directions(spangramSlack), spangramSlack)
        for index, node in enumerate(spangramPath):
            grid[node] = spangram[index]
        
        # Calculate Strand Paths

        allEdges = spangramPath

        seperateGrids = self.Calculate_seperate_grids(grid, allEdges, grid_dimensions)
        print("Word: ", self.themeWords[0])
        print("All theme words: ", self.themeWords)
        for y in range(grid_dimensions[0]):
            for x in range(grid_dimensions[1]):
                print((y,x) if (y,x) in seperateGrids[0] else "xxxxxx", end=" ")
            print()

        strandPaths[self.themeWords[0]] = self.calculate_strand_path(self.strandLengths[0], seperateGrids[0], random.choice(list(seperateGrids[0].keys())), self.themeWords[0], self.get_illegal_edges(spangramPath))

        for themeWord in self.themeWords:
            for strandPath in strandPaths[themeWord]:
                pass
                #strandPaths[themeWord] = self.calculate_strand_path(themeWord, strandPath, grid, self.permittedDirections)

        for themeWord in self.themeWords:
            for index, node in enumerate(strandPaths[themeWord]):
                grid[node] = themeWord[index]

        return grid, strandPaths, spangramPath
    
    def calculate_strand_path(self, remainingLength, currentGrid, currentPosition, word, disallowedEdges:list, workingStrand=[]):
        print("Disallowed Edges: ", disallowedEdges)
        if remainingLength == 0:
            return workingStrand
        if remainingLength == 1:
            currentGrid[currentPosition] = word[len(word) - 1]
            return workingStrand + [currentPosition]

        legalDirections = []
        for direction in self.permittedDirections:
            newPosition = (currentPosition[0] + direction[0], currentPosition[1] + direction[1])
            if newPosition not in currentGrid or currentGrid[newPosition] != None:
                continue
            if [currentPosition,newPosition] in disallowedEdges:
                continue
            legalDirections.append(direction)
        
        #self.visualise_grid()
        result = None
        newDissallowedEdges = disallowedEdges.copy()
        while result is None:
            if len(legalDirections) == 0:
                return None
                #self.visualise_grid()
            chosenDirection  = random.choice(legalDirections)
            newPosition = (currentPosition[0] + chosenDirection[0], currentPosition[1] + chosenDirection[1])
            if chosenDirection[0] != 0 and chosenDirection[1] != 0: # diagonal rule
                newDissallowedEdges.append([(currentPosition[0]+chosenDirection[0], currentPosition[1]),
                                            (currentPosition[0], currentPosition[1]+chosenDirection[1])])
                newDissallowedEdges.append([(currentPosition[0], currentPosition[1]+chosenDirection[1]),
                                            (currentPosition[0]+chosenDirection[0], currentPosition[1])])
                
            currentGrid[currentPosition] = word[len(word) - remainingLength]
            result = self.calculate_strand_path(remainingLength - 1, dict(currentGrid), newPosition, word, newDissallowedEdges, list(workingStrand + [currentPosition]))
            if result is None:
                legalDirections.remove(chosenDirection)
        return result
    
    def find_valid_grid_sizes(self, themeWords, ):
        letterCount = len(spangram)
        for word in themeWords:
            letterCount += len(word)
        validGridSizes = []
        for rows in range(1, letterCount + 1):
            for cols in range(1, letterCount + 1):
                if rows * cols == letterCount:
                    validGridSizes.append((rows, cols))
        return validGridSizes

    def Calculate_seperate_grids(self, grid, allEdges, grid_dimensions):
        free_spaces = [position for position in grid.keys() if grid[position] is None]
        seperateGrids = []
        
        # Continue until no free spaces remain
        while free_spaces:
            # Start a new grid from the first free space available
            new_grid = self.findable_grid_from_point(grid, allEdges, grid_dimensions, free_spaces[0])
            seperateGrids.append(new_grid)
            
            # Remove positions in the new grid from the list of free spaces
            for position in new_grid.keys():
                if position in free_spaces:
                    free_spaces.remove(position)
        
        return seperateGrids


    def findable_grid_from_point(self, grid, allEdges, grid_dimensions, startingNode, workingGridEdges=[]):
        """
        Returns all connected free cells (i.e. cells where grid[position] is None)
        reachable from startingNode without crossing barrier cells.
        
        Parameters:
            grid: A dictionary mapping positions (row, col) to a value (None for free cells).
            allEdges: A list of positions (or edges) that should be treated as barriers.
                    (In your case, these might be the cells that belong to the spangram path.)
            grid_dimensions: Tuple (rows, cols) giving grid bounds.
            startingNode: The cell (row, col) from which to start the search.
            workingGridEdges: Optional list of edge pairs to block moves (e.g. [[(r1,c1), (r2,c2)], ...]).
            
        Returns:
            A dictionary of positions that are reachable, mapping each cell to its grid value.
        """
        # Initialize the data structure to keep track of visited nodes.
        reachable = {}
        # Use a list as a queue for our BFS.
        queue = [startingNode]

        while queue:
            current = queue.pop(0)
            # If we have already visited this cell, skip it.
            if current in reachable:
                continue
            
            # Mark the current cell as reached.
            reachable[current] = grid[current]
            
            # Check every allowed neighbor based on permitted directions.
            for d in self.permittedDirections:
                neighbor = (current[0] + d[0], current[1] + d[1])
                # Skip if out of grid bounds.
                if not (0 <= neighbor[0] < grid_dimensions[0] and 0 <= neighbor[1] < grid_dimensions[1]):
                    continue
                # Skip if the cell is occupied (for instance, by part of the spangram).
                if grid[neighbor] is not None:
                    continue
                # Optional: Skip if this move is blocked by any extra edge restrictions.
                if [current, neighbor] in workingGridEdges or [neighbor, current] in workingGridEdges:
                    continue
                
                diagonalRuleBroken = False
                if d[0] != 0 and d[1] != 0: # diagonal rule
                    disallowedEdge = [(current[0]+d[0], current[1]),
                                        (current[0], current[1]+d[1])]

                    for index in range(len(allEdges)-1):
                        if (disallowedEdge[0] == allEdges[index] and disallowedEdge[1] == allEdges[index+1]) or (disallowedEdge[1] == allEdges[index] and disallowedEdge[0] == allEdges[index+1]):
                            diagonalRuleBroken = True
                            break
                if diagonalRuleBroken:
                    continue

                if neighbor not in reachable:
                    queue.append(neighbor)
                    
        return reachable
        
    
    def test_spanagram_failure_rate(self, spangramSlack, spangramDirection, grid_dimensions, iterations):
        total_attempts = 0
        correct_attempts = 0
        for n in tqdm(range(iterations)):
            total_attempts += 1
            calculatedStrandsGraph = self.calculate_strands_graph(spangramSlack, spangramDirection,grid_dimensions)

            if calculatedStrandsGraph is not None:
                correct_attempts += 1
        print(f"Total attempts: {total_attempts}")
        print(f"Correct attempts: {correct_attempts}")
        print(f"Success rate: {correct_attempts/total_attempts}")
        

    def calculate_spangram_path(self, remainingLength, currentGrid, currentPosition, permittedDirections, spangramSlack, workingSpangram=[], disallowedEdges:list=[], reverseSlack=0):
        if remainingLength == 0:
            return workingSpangram
        if remainingLength == 1:
            currentGrid[currentPosition] = self.spangram[self.spangramLength - 1]
            return workingSpangram + [currentPosition]
        if spangram_direction == "horizontal" and reverseSlack != float("inf"):
            startingWall = 0 if self.spangramDirection[1] == 1 else self.grid_dimensions[1] - 1
            distanceFromWall = abs(currentPosition[1] - startingWall)
            totalDistanceToGo = distanceFromWall + self.grid_dimensions[1] - 1
            if distanceFromWall == 0:
                reverseSlack = float("inf")
            if remainingLength == totalDistanceToGo:
                reverseSlack = 0
        if spangram_direction == "vertical" and reverseSlack != float("inf"):
            startingWall = 0 if self.spangramDirection[0] == 1 else self.grid_dimensions[0] - 1
            distanceFromWall = abs(currentPosition[0] - startingWall)
            totalDistanceToGo = distanceFromWall + self.grid_dimensions[0] - 1
            if distanceFromWall == 0:
                reverseSlack = float("inf")
            if remainingLength == totalDistanceToGo:
                reverseSlack = 0

        legalDirections = []
        for direction in permittedDirections:
            newPosition = (currentPosition[0] + direction[0], currentPosition[1] + direction[1])
            if newPosition not in currentGrid or currentGrid[newPosition] != None:
                continue
            if [currentPosition,newPosition] in disallowedEdges:
                continue
            if reverseSlack == 0:
                if spangram_direction == "horizontal":
                    if direction[1] == self.spangramDirection[1]:
                        continue
                if spangram_direction == "vertical":
                    if direction[0] == self.spangramDirection[0]:
                        continue
            legalDirections.append(direction)
        
        #self.visualise_grid()
        result = None
        backupSpangramSlack = spangramSlack
        newDissallowedEdges = disallowedEdges.copy()
        while result is None:
            spangramSlack = backupSpangramSlack
            if len(legalDirections) == 0:
                return None
                #self.visualise_grid()
            chosenDirection  = random.choice(legalDirections)
            newPosition = (currentPosition[0] + chosenDirection[0], currentPosition[1] + chosenDirection[1])
            if chosenDirection[0] != 0 and chosenDirection[1] != 0: # diagonal rule
                newDissallowedEdges.append([(currentPosition[0]+chosenDirection[0], currentPosition[1]),
                                            (currentPosition[0], currentPosition[1]+chosenDirection[1])])
                newDissallowedEdges.append([(currentPosition[0], currentPosition[1]+chosenDirection[1]),
                                            (currentPosition[0]+chosenDirection[0], currentPosition[1])])
            if self.spangramDirection[0] == 0: # horizontal
                if chosenDirection[1] == -1*self.spangramDirection[1]:
                    spangramSlack -= 2
                    newPermittedDirections = self.calculate_new_permitted_directions(spangramSlack)
                elif chosenDirection[1] != self.spangramDirection[1]:
                    spangramSlack -= 1
                    newPermittedDirections = self.calculate_new_permitted_directions(spangramSlack)
                else:
                    newPermittedDirections = permittedDirections
            if self.spangramDirection[1] == 0: # vertical
                if chosenDirection[0] == -1*self.spangramDirection[0]:
                    spangramSlack -= 2
                    newPermittedDirections = self.calculate_new_permitted_directions(spangramSlack)
                elif chosenDirection[0] != self.spangramDirection[0]:
                    spangramSlack -= 1
                    newPermittedDirections = self.calculate_new_permitted_directions(spangramSlack)
                else:
                    newPermittedDirections = permittedDirections
            currentGrid[currentPosition] = self.spangram[self.spangramLength - remainingLength]
            result = self.calculate_spangram_path(remainingLength - 1, dict(currentGrid), newPosition, list(newPermittedDirections), spangramSlack, list(workingSpangram + [currentPosition]), newDissallowedEdges, reverseSlack=reverseSlack)
            if result is None:
                legalDirections.remove(chosenDirection)
        return result
        
    
    def calculate_new_permitted_directions(self, spangramSlack):
        if spangramSlack < 0:
            raise ValueError("The spangram slack is negative.")
        elif spangramSlack == 0:
            if spangram_direction == "horizontal":
                return [direction for direction in self.permittedDirections if direction[1] == self.spangramDirection[1]]
            else:
                return[direction for direction in self.permittedDirections if direction[0] == self.spangramDirection[0]]
        elif spangramSlack == 1:
            if spangram_direction == "horizontal":
                return[direction for direction in self.permittedDirections if direction[1] != -1*self.spangramDirection[1]]
            else:
                return[direction for direction in self.permittedDirections if direction[0] != -1*self.spangramDirection[0]]
        else:
            return self.permittedDirections
            

    def get_initial_spangram_slack(self):
        slackValue = 0
        if self.spangramDirection[0] == 0: # horizontal
            slackValue += self.spangramLength - self.grid_dimensions[1]
        elif self.spangramDirection[1] == 0: # vertical
            slackValue += self.spangramLength - self.grid_dimensions[0]
        else:
            raise ValueError(f"Bad spangram direction: {self.spangramDirection}")
        return slackValue
    def update_spangram_slack(self, spangramSlack, spangramDirection, startingNode, grid_dimensions):
        slackValue = spangramSlack
        if spangramDirection[1] == 1: 
            slackValue += startingNode[1]
        elif spangramDirection[1] == -1:
            slackValue += grid_dimensions[1] - (startingNode[1] + 1)
        elif spangramDirection[0] == 1:
            slackValue += startingNode[0]
        elif spangramDirection[0] == -1:
            slackValue += grid_dimensions[0] - startingNode[0] - 1
        return slackValue
    
    def get_illegal_edges(self, strandPath):
        illegalEdges = []
        
        for index in range(len(strandPath)-1):
            direction = [strandPath[index+1][0] - strandPath[index][0], strandPath[index+1][1] - strandPath[index][1]]
            if direction[0] != 0 and direction[1] != 0: # diagonal
                illegalEdges.append([(strandPath[index][0]+direction[0],strandPath[index][1]),
                                     (strandPath[index][0],strandPath[index][1]+direction[1])])
                illegalEdges.append([(strandPath[index][0],strandPath[index][1]+direction[1]),
                                     (strandPath[index][0]+direction[0],strandPath[index][1])])
        return illegalEdges

    def get_possible_strand_start_nodes(self):
        possibleStartNodes = []
        allowedDistance = self.spangramSlack // 2

        if self.spangramDirection == [0, 1]:
            for x in range(allowedDistance+1):
                for y in range(self.grid_dimensions[0]):
                    possibleStartNodes.append((y, x))
        elif self.spangramDirection == [0, -1]:
            for x in range((self.grid_dimensions[1] - allowedDistance)-1, self.grid_dimensions[1]):
                for y in range(self.grid_dimensions[0]):
                    possibleStartNodes.append((y, x))
        elif self.spangramDirection == [1, 0]:
            for y in range(allowedDistance+1):
                for x in range(self.grid_dimensions[1]):
                    possibleStartNodes.append((y, x))
        elif self.spangramDirection == [-1, 0]:
            for y in range((self.grid_dimensions[0] - allowedDistance)-1, self.grid_dimensions[0]):
                for x in range(self.grid_dimensions[1]):
                    possibleStartNodes.append((y, x))
        validPossibleStartNodes = []
        for node in possibleStartNodes:
            if node[0] >= 0 and node[0] <= self.grid_dimensions[0] - 1 and node[1] >= 0 and node[1] <= self.grid_dimensions[1] - 1:
                validPossibleStartNodes.append(node)
        return validPossibleStartNodes
            

    def find_valid_strand_path(self):
        pass
    def getGrid(self):
        return self.grid
    def getStrandPaths(self):
        return self.strandPaths
    def getSpangramPath(self):
        return self.spangramPath
    def visualise_grid(self, grid, strandPaths, spangramPath):
        positions = {}
        for position in grid.keys():
            positions[position] = (position[1], -1*position[0])  # so row 0 is at the top

        G = nx.DiGraph()
        G.add_nodes_from(positions.keys())

        # Define colors for each strand.
        COLOUR_STRINGS = [
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
        spangram_colour = 'yellow'

        strand_colours = {strand: COLOUR_STRINGS[i] for i, (strand, _) in enumerate(strandPaths.items())}

        strand_colours['spangram'] = spangram_colour

        for strand, path in strandPaths.items():
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                G.add_edge(u, v, strand=strand)
        for i in range(len(spangramPath) - 1):
            u = spangramPath[i]
            v = spangramPath[i + 1]
            G.add_edge(u, v, strand='spangram')

        plt.figure(figsize=(6, 10))  # Increase figure size to provide more space
        nx.draw_networkx_nodes(G, pos=positions, node_size=500, node_color='lightgray')
        nx.draw_networkx_edges(G, pos=positions, edge_color='lightgray', alpha=0.3, arrows=True)
        for strand, color in strand_colours.items():
            strand_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('strand') == strand]
            if strand_edges:
                nx.draw_networkx_edges(G, pos=positions, edgelist=strand_edges,
                                        edge_color=color, width=2, arrows=True,
                                        arrowstyle='->', connectionstyle='arc3,rad=0.1')
        
        # Create a dictionary for node labels using gridLabels
        node_labels = {}
        for position in grid.keys():
            node_labels[position] = grid[position] if grid[position] is not None else position

        nx.draw_networkx_labels(G, pos=positions, labels=node_labels)
        #nx.draw_networkx_labels(G, pos=positions)
        #patches = [mpatches.Patch(color=color, label=strand) for strand, color in strand_colors.items()]
        #plt.legend(handles=patches, loc='lower right', bbox_to_anchor=(1, -0.18))  # Moves the legend outside the plot
        plt.title("Strands Puzzle Solution")
        plt.axis("off")
        plt.show() 
# Example Usage:
if __name__ == "__main__":
    themeWords = ["purple","grape","stain","slate","plant","tee"]
    spangram = "accommodativenesses"
    grid_dimensions = (8, 6) # 8 rows, 6 columns
    spangram_direction = "vertical"
    solver = StrandsSolverV2(themeWords, spangram, grid_dimensions, spangram_direction)
    strand_path = solver.find_valid_strand_path()
    solver.visualise_grid(solver.getGrid(), solver.getStrandPaths(), solver.getSpangramPath())
    print(strand_path)