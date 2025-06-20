import networkx as nx
import matplotlib.pyplot as plt

# Hanya sebagai contoh dikarenakan Tonnetz tidak berhingga
triads = [
    ('C', 'E', 'G'),
    ('A', 'C', 'E'),
    ('F', 'A', 'C'),
    ('D', 'F', 'A')
]

G = nx.Graph()

for triad in triads:
    for note in triad:
        G.add_node(note)

for triad in triads:
    a, b, c = triad
    G.add_edge(a, b)
    G.add_edge(b, c)
    G.add_edge(c, a)

is_planar, _ = nx.check_planarity(G)

# Testing
if is_planar:
    print("Graf Tonnetz lokal (triad) ini adalah planar.")
    pos = nx.planar_layout(G)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', node_size=1000, font_size=12)
    plt.title("Subset Tonnetz sebagai Graf Planar")
    plt.show()
else:
    print("Graf ini tidak planar.")


