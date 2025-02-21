import networkx as nx
import matplotlib.pyplot as plt

class TrieNode:
    def __init__(self):
        self.children = {}  # Maps a letter to the next TrieNode.
        self.is_word = False  # True if this node marks the end of a word.

class WordTrie:
    def __init__(self):
        self.root = TrieNode()
        self.valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    
    def insert(self, word: str):
        node = self.root
        for char in word.upper():
            if char not in self.valid_chars:
                continue
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
    
    def search(self, prefix: str):
        """
        Returns a tuple:
         - A boolean indicating if the prefix itself is a complete word.
         - A list of characters that represent the immediate branches from that prefix.
        """
        node = self.root
        for char in prefix.upper():
            if char not in node.children:
                return (False, [])
            node = node.children[char]
        return (node.is_word, list(node.children.keys()))
    
    def _build_graph(self, node: TrieNode, current_prefix: str, graph: nx.DiGraph, node_info: dict):
        """
        Recursively builds a directed graph representing the trie subtree.
        
        - node: current trie node.
        - current_prefix: string accumulated so far.
        - graph: the NetworkX DiGraph being built.
        - node_info: a dict mapping node labels to a boolean indicating if the node marks a complete word.
        """
        for letter, child in node.children.items():
            new_prefix = current_prefix + letter
            graph.add_edge(current_prefix, new_prefix, label=letter)
            node_info[new_prefix] = child.is_word
            self._build_graph(child, new_prefix, graph, node_info)
    
    def visualize(self, prefix: str):
        """
        Visualizes the subtree of the trie starting from the given prefix.
        Complete words are shown in red; intermediate nodes are in blue.
        """
        prefix = prefix.upper()
        node = self.root
        for char in prefix:
            if char in node.children:
                node = node.children[char]
            else:
                print(f"Prefix '{prefix}' not found in trie.")
                return
        
        # Build the graph from the node corresponding to the prefix.
        G = nx.DiGraph()
        node_info = {}  # Maps node labels (prefix strings) to is_word boolean.
        G.add_node(prefix)
        node_info[prefix] = node.is_word
        self._build_graph(node, prefix, G, node_info)
        
        # Set colors: red if the node is a complete word, blue otherwise.
        colors = ['red' if node_info.get(n, False) else 'blue' for n in G.nodes()]
        
        pos = nx.spring_layout(G)
        plt.figure(figsize=(10, 8))
        nx.draw(G, pos, with_labels=True, node_color=colors, node_size=1500, font_color='white', arrows=True)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.title(f"Trie Visualization from Prefix: {prefix}")
        plt.show()

# Example usage:
if __name__ == "__main__":
    # Build the trie from a file
    trie = WordTrie()
    with open("english_words.txt", "r") as file:
        for line in file:
            word = line.strip()
            if word:  # Skip empty lines.
                trie.insert(word)
    
    # Visualize the trie subtree starting from the prefix "race".
    print(trie.search("jazzyj"))
