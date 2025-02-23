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
        
        self.grid = {(y, x): None for y in range(grid_dimensions[0]) for x in range(grid_dimensions[1])}

        self.strandPaths = {themeWord: [] for themeWord in self.themeWords}

        self.startingNode = random.choice(self.possibleStrandStartNodes)
        
        self.spangramSlack = self.update_spangram_slack()  

        self.spangramPath = []

        # TESTING STUFF CAN DELETE LATER
        oldGrid = self.grid.copy()

        self.spangramPath = self.calculate_spangram_path(self.spangramLength, self.grid, self.startingNode, self.calculate_new_permitted_directions(self.spangramSlack), self.spangramSlack)
  
        #self.grid = oldGrid.copy()
        
        #self.test_spanagram_failure_rate(1000000)
        ################################


              
        
    
    def test_spanagram_failure_rate(self, iterations):
        oldGrid = self.grid.copy()
        total_attempts = 0
        correct_attempts = 0
        total_attempts += 1
        if self.spangramPath is not None:
            correct_attempts += 1
        
        for n in tqdm(range(iterations)):
            total_attempts += 1
            self.grid = oldGrid.copy()
            self.spangramSlack = self.get_initial_spangram_slack()
            self.startingNode = random.choice(self.possibleStrandStartNodes)
            self.spangramSlack = self.update_spangram_slack()
            self.spangramPath = []
            
            self.spangramPath = self.calculate_spangram_path(self.spangramLength, self.grid, self.startingNode, self.calculate_new_permitted_directions(self.spangramSlack), self.spangramSlack)

            if self.spangramPath is not None:
                correct_attempts += 1
        print(f"Total attempts: {total_attempts}")
        print(f"Correct attempts: {correct_attempts}")
        print(f"Success rate: {correct_attempts/total_attempts}")
        

    def calculate_spangram_path(self, remainingLength, currentGrid, currentPosition, permittedDirections, spangramSlack, workingSpangram=[], disallowedEdges:list=[], reverseSlack=0):
        if remainingLength == 0:
            self.grid = currentGrid.copy()
            return workingSpangram
        if remainingLength == 1:
            currentGrid[currentPosition] = self.spangram[self.spangramLength - 1]
            self.grid = currentGrid.copy()
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
            if newPosition not in currentGrid.keys() or currentGrid[newPosition] != None:
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
    def update_spangram_slack(self):
        slackValue = self.spangramSlack
        if self.spangramDirection[1] == 1: 
            slackValue += self.startingNode[1]
        elif self.spangramDirection[1] == -1:
            slackValue += self.grid_dimensions[1] - (self.startingNode[1] + 1)
        elif self.spangramDirection[0] == 1:
            slackValue += self.startingNode[0]
        elif self.spangramDirection[0] == -1:
            slackValue += self.grid_dimensions[0] - self.startingNode[0] - 1
        return slackValue

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
    themeWords = ["scaret","grape","stain","slate","plant","tee","", ""]
    spangram = "abcdefghijklmnopr"
    grid_dimensions = (8, 6) # 8 rows, 6 columns
    themeWords = [((grid_dimensions[0]*grid_dimensions[1])-len(spangram))*" "] # just for testing spangram
    spangram_direction = "vertical"
    solver = StrandsSolverV2(themeWords, spangram, grid_dimensions, spangram_direction)
    strand_path = solver.find_valid_strand_path()
    solver.visualise_grid()
    print(strand_path)