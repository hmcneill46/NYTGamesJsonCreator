import random
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches

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
        
        self.grid = {(y, x): None for y in range(grid_dimensions[0]) for x in range(grid_dimensions[1])}

        self.strandPaths = {themeWord: [] for themeWord in self.themeWords}
        

        self.spangramPath = self.calculate_spangram_path(self.spangramLength, self.grid, random.choice(self.possibleStrandStartNodes), self.calculate_new_permitted_directions())
        

    def calculate_spangram_path(self, remainingLength, currentGrid, currentPosition, permittedDirections):
        if remainingLength == 0:
            return []
        if remainingLength == 1:
            currentGrid[currentPosition] = self.spangram[self.spangramLength - 1]
            return [currentPosition]
        legalDirections = []
        for direction in permittedDirections:
            newPosition = (currentPosition[0] + direction[0], currentPosition[1] + direction[1])
            if newPosition in currentGrid.keys() and currentGrid[newPosition] is None:
                legalDirections.append(direction)
        chosenDirection  = random.choice(legalDirections)
        newPosition = (currentPosition[0] + chosenDirection[0], currentPosition[1] + chosenDirection[1])
        while newPosition not in currentGrid.keys() or currentGrid[newPosition] is not None:
            chosenDirection = random.choice(permittedDirections)
            newPosition = (currentPosition[0] + chosenDirection[0], currentPosition[1] + chosenDirection[1])
        if self.spangramDirection[0] == 0: # horizontal
            if chosenDirection[1] == -1*self.spangramDirection[1]:
                self.spangramSlack -= 2
                newPermittedDirections = self.calculate_new_permitted_directions()
            elif chosenDirection[1] != self.spangramDirection[1]:
                self.spangramSlack -= 1
                newPermittedDirections = self.calculate_new_permitted_directions()
            else:
                newPermittedDirections = permittedDirections
        if self.spangramDirection[1] == 0: # vertical
            if chosenDirection[0] == -1*self.spangramDirection[0]:
                self.spangramSlack -= 2
                newPermittedDirections = self.calculate_new_permitted_directions()
            elif chosenDirection[0] != self.spangramDirection[0]:
                self.spangramSlack -= 1
                newPermittedDirections = self.calculate_new_permitted_directions()
            else:
                newPermittedDirections = permittedDirections
        currentGrid[currentPosition] = self.spangram[self.spangramLength - remainingLength]
        return [currentPosition] + self.calculate_spangram_path(remainingLength - 1, dict(currentGrid), newPosition, newPermittedDirections)
        
    
    def calculate_new_permitted_directions(self):
        if self.spangramSlack < 0:
            raise ValueError("The spangram slack is negative.")
        elif self.spangramSlack == 0:
            if spangram_direction == "horizontal":
                return [direction for direction in self.permittedDirections if direction[1] == self.spangramDirection[1]]
            else:
                return[direction for direction in self.permittedDirections if direction[0] == self.spangramDirection[0]]
        elif self.spangramSlack == 1:
            if spangram_direction == "horizontal":
                return[direction for direction in self.permittedDirections if direction[1] != -1*self.spangramDirection[1]]
            else:
                return[direction for direction in self.permittedDirections if direction[0] != -1*self.spangramDirection[0]]
        else:
            return self.permittedDirections
            
        

    def get_initial_spangram_slack(self):
        if self.spangramDirection[0] == 0: # horizontal
            return(self.spangramLength - self.grid_dimensions[1])
        elif self.spangramDirection[1] == 0: # vertical
            return(self.spangramLength - self.grid_dimensions[0])
        else:
            raise ValueError(f"Bad spangram direction: {self.spangramDirection}")

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
        return possibleStartNodes
            

    def find_valid_strand_path(self):
        pass
    def getGrid(self):
        return self.grid
    def getStrandPaths(self):
        return self.strandPaths
    def getSpangramPath(self):
        return self.spangramPath
    def visualise_grid(self):
        grid = self.getGrid()
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

        strand_colours = {strand: COLOUR_STRINGS[i] for i, (strand, _) in enumerate(self.strandPaths.items())}

        strand_colours['spangram'] = spangram_colour

        for strand, path in self.strandPaths.items():
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                G.add_edge(u, v, strand=strand)
        for i in range(len(self.spangramPath) - 1):
            u = self.spangramPath[i]
            v = self.spangramPath[i + 1]
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
    themeWords = ["scaret","grape","stain","slate","plant","bright","four", "part"]
    spangram = "purpleee"
    grid_dimensions = (8, 6) # 8 rows, 6 columns
    spangram_direction = "horizontal"
    solver = StrandsSolverV2(themeWords, spangram, grid_dimensions, spangram_direction)
    strand_path = solver.find_valid_strand_path()
    solver.visualise_grid()
    print(strand_path)