import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class ChordNode:
    def __init__(self, root, quality):
        self.root = root
        self.quality = quality  # 'major', 'minor', 'dim', 'aug'
    
    def __str__(self):
        if self.quality == 'major':
            return self.root
        elif self.quality == 'minor':  
            return f"{self.root}m"
        elif self.quality == 'dim':
            return f"{self.root}°"
        elif self.quality == 'aug':
            return f"{self.root}+"
        return f"{self.root}{self.quality}"
    
    def __hash__(self):
        return hash((self.root, self.quality))
    
    def __eq__(self, other):
        if not isinstance(other, ChordNode):
            return False
        return self.root == other.root and self.quality == other.quality

class TonnetzGraph:    
    def __init__(self):
        self.graph = nx.Graph()
        self.notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.chord_nodes = {}
        self.genre_weights = self._initialize_genre_weights()
        self._build_tonnetz()
        
    def _initialize_genre_weights(self):
        weights = {}

        # Jazz - lebih banyak diminished dan transisi kompleks
        weights['jazz'] = {
            ('major', 'minor'): 0.8, ('minor', 'major'): 0.7,
            ('major', 'dim'): 0.9, ('dim', 'major'): 0.8,
            ('minor', 'minor'): 0.6, ('major', 'major'): 0.4,
            ('dim', 'minor'): 0.7, ('minor', 'dim'): 0.8,
            ('major', 'aug'): 0.3, ('aug', 'minor'): 0.5
        }
        
        # Rock - dominasi major chord
        weights['rock'] = {
            ('major', 'major'): 0.9, ('minor', 'major'): 0.8,
            ('major', 'minor'): 0.7, ('minor', 'minor'): 0.6,
            ('major', 'dim'): 0.3, ('dim', 'major'): 0.4,
            ('dim', 'minor'): 0.2, ('minor', 'dim'): 0.2,
            ('major', 'aug'): 0.1, ('aug', 'minor'): 0.2
        }
        
        # Pop - balanced
        weights['pop'] = {
            ('major', 'major'): 0.8, ('major', 'minor'): 0.9,
            ('minor', 'major'): 0.8, ('minor', 'minor'): 0.5,
            ('major', 'dim'): 0.4, ('dim', 'major'): 0.5,
            ('dim', 'minor'): 0.3, ('minor', 'dim'): 0.3,
            ('major', 'aug'): 0.2, ('aug', 'minor'): 0.3
        }
        
        # Hip-hop - dominasi minor
        weights['hiphop'] = {
            ('minor', 'minor'): 0.9, ('minor', 'major'): 0.7,
            ('major', 'minor'): 0.8, ('major', 'major'): 0.5,
            ('minor', 'dim'): 0.4, ('dim', 'minor'): 0.6,
            ('major', 'dim'): 0.3, ('dim', 'major'): 0.3,
            ('major', 'aug'): 0.1, ('aug', 'minor'): 0.2
        }
        
        # Classical - harmoni kompleks
        weights['classical'] = {
            ('major', 'major'): 0.7, ('major', 'minor'): 0.8,
            ('minor', 'major'): 0.8, ('minor', 'minor'): 0.6,
            ('major', 'dim'): 0.9, ('dim', 'major'): 0.8,
            ('dim', 'minor'): 0.9, ('minor', 'dim'): 0.8,
            ('major', 'aug'): 0.4, ('aug', 'minor'): 0.5
        }
        
        return weights
    
    def _build_tonnetz(self):
        for note in self.notes:
            for quality in ['major', 'minor', 'dim']:
                chord = ChordNode(note, quality)
                self.chord_nodes[str(chord)] = chord
                self.graph.add_node(chord)
        self._add_tonnetz_edges()
        
    def _add_tonnetz_edges(self):
        for chord in self.chord_nodes.values():
            if chord.quality == 'major':
                parallel_chord = ChordNode(chord.root, 'minor')
                if parallel_chord in self.graph.nodes:
                    self.graph.add_edge(chord, parallel_chord, transform='P', weight=1.0)
            if chord.quality == 'major':
                rel_root = self._get_relative_minor(chord.root)
                rel_chord = ChordNode(rel_root, 'minor')
                if rel_chord in self.graph.nodes:
                    self.graph.add_edge(chord, rel_chord, transform='R', weight=0.9)
            if chord.quality == 'minor':
                lead_root = self._get_leading_tone_major(chord.root)
                lead_chord = ChordNode(lead_root, 'major')
                if lead_chord in self.graph.nodes:
                    self.graph.add_edge(chord, lead_chord, transform='L', weight=0.8)
            fifth_root = self._get_fifth(chord.root)
            fifth_chord = ChordNode(fifth_root, chord.quality)
            if fifth_chord in self.graph.nodes:
                self.graph.add_edge(chord, fifth_chord, transform='V', weight=0.9)
            fourth_root = self._get_fourth(chord.root)
            fourth_chord = ChordNode(fourth_root, chord.quality)
            if fourth_chord in self.graph.nodes:
                self.graph.add_edge(chord, fourth_chord, transform='IV', weight=0.7)
    
    def _get_relative_minor(self, major_root):
        idx = self.notes.index(major_root)
        return self.notes[(idx - 3) % 12]
    
    def _get_leading_tone_major(self, minor_root):
        idx = self.notes.index(minor_root)
        return self.notes[(idx + 3) % 12]
    
    def _get_fifth(self, root):
        idx = self.notes.index(root)
        return self.notes[(idx + 7) % 12]
    
    def _get_fourth(self, root):
        idx = self.notes.index(root)
        return self.notes[(idx + 5) % 12]
    
    def _parse_chord(self, chord_str):
        chord_str = chord_str.strip()

        if chord_str.endswith('°'):
            return ChordNode(chord_str[:-1], 'dim')
        elif chord_str.endswith('+'):
            return ChordNode(chord_str[:-1], 'aug')
        elif chord_str.endswith('m'):
            return ChordNode(chord_str[:-1], 'minor')
        else:
            return ChordNode(chord_str, 'major')
    
    def generate_progression(self, start_chord, length, genre='pop'):
        try:
            current_chord = self._parse_chord(start_chord)
            if current_chord not in self.graph.nodes:
                raise ValueError(f"Chord {start_chord} tidak ditemukan dalam graf")
            
            progression = [str(current_chord)]
            genre_weights = self.genre_weights.get(genre, self.genre_weights['pop'])
            
            for _ in range(length - 1):
                neighbors = list(self.graph.neighbors(current_chord))
                if not neighbors:
                    break
                
                # Hitung bobot untuk setiap neighbor berdasarkan genre
                weighted_neighbors = []
                for neighbor in neighbors:
                    base_weight = self.graph[current_chord][neighbor].get('weight', 0.5)
                    
                    # Aplikasikan bobot genre
                    transition_key = (current_chord.quality, neighbor.quality)
                    genre_weight = genre_weights.get(transition_key, 0.5)
                    
                    final_weight = base_weight * (genre_weight**2)
                    weighted_neighbors.append((neighbor, final_weight))
                
                # Pilih chord berikutnya berdasarkan weighted random selection
                if weighted_neighbors:
                    neighbors_list = [item[0] for item in weighted_neighbors]
                    weights = [item[1] for item in weighted_neighbors]
                    total_weight = sum(weights)
                    if total_weight > 0:
                        probs = [w/total_weight for w in weights]
                        choice_idx = np.random.choice(len(neighbors_list), p=probs)
                        current_chord = neighbors_list[choice_idx]
                    else:
                        current_chord = neighbors_list[np.random.randint(len(neighbors_list))]
                    
                    progression.append(str(current_chord))
            
            return progression
            
        except Exception as e:
            print(f"Error generating progression: {e}")
            return [start_chord]
    
    def classify_genre(self, progression):
        if len(progression) < 2:
            return {genre: 0.0 for genre in self.genre_weights.keys()}
        
        genre_scores = {}
        for genre in self.genre_weights.keys():
            genre_scores[genre] = 0.0
        
        for i in range(len(progression) - 1):
            try:
                current = self._parse_chord(progression[i])
                next_chord = self._parse_chord(progression[i + 1])
                
                transition = (current.quality, next_chord.quality)
                
                for genre, weights in self.genre_weights.items():
                    genre_scores[genre] += weights.get(transition, 0.1)
                    
            except Exception:
                continue
        
        total_transitions = len(progression) - 1
        if total_transitions > 0:
            for genre in genre_scores:
                genre_scores[genre] /= total_transitions
        
        return genre_scores
    
    def visualize_graph(self, highlight_progression=None):
        plt.figure(figsize=(15, 12))
        pos = nx.spring_layout(self.graph, k=3, iterations=50)
        nx.draw_networkx_edges(self.graph, pos, alpha=0.3, edge_color='gray')
        node_colors = []
        for node in self.graph.nodes():
            if node.quality == 'major':
                node_colors.append('lightblue')
            elif node.quality == 'minor':
                node_colors.append('lightcoral')
            else:  # diminished
                node_colors.append('lightgreen')
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, node_size=800, alpha=0.8)
        labels = {node: str(node) for node in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
        if highlight_progression:
            try:
                prog_nodes = [self._parse_chord(chord) for chord in highlight_progression]
                nx.draw_networkx_nodes(self.graph, pos, nodelist=prog_nodes,
                                     node_color='yellow', node_size=1000, alpha=0.7)
                for i in range(len(prog_nodes) - 1):
                    if self.graph.has_edge(prog_nodes[i], prog_nodes[i+1]):
                        nx.draw_networkx_edges(self.graph, pos, 
                                             edgelist=[(prog_nodes[i], prog_nodes[i+1])],
                                             edge_color='red', width=3)
            except Exception:
                pass
        
        plt.title("Tonnetz Graph Representation")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def analyze_progression(self, progression):
        print(f"Chord Progression: {' -> '.join(progression)}")
        print(f"Length: {len(progression)} chords")
        
        # Klasifikasi genre
        genre_scores = self.classify_genre(progression)
        print("\nGenre Classification:")
        
        # Sort genre scores
        sorted_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)
        for genre, score in sorted_genres:
            print(f"  {genre.capitalize()}: {score:.3f}")
        
        # Analisis transisi
        print("\nChord Transitions:")
        for i in range(len(progression) - 1):
            try:
                current = self._parse_chord(progression[i])
                next_chord = self._parse_chord(progression[i + 1])
                
                if self.graph.has_edge(current, next_chord):
                    edge_data = self.graph[current][next_chord]
                    transform = edge_data.get('transform', 'Unknown')
                    weight = edge_data.get('weight', 0.0)
                    print(f"  {progression[i]} -> {progression[i+1]} (Transform: {transform}, Weight: {weight:.2f})")
                else:
                    print(f"  {progression[i]} -> {progression[i+1]} (No direct connection)")
            except Exception:
                print(f"  {progression[i]} -> {progression[i+1]} (Parse error)")

# Testing
def main():
    print("=== TONNETZ GRAPH IMPLEMENTATION ===")
    print("Implementasi Tonnetz sebagai Graf Planar untuk Generasi Progresi Chord\n")

    tonnetz = TonnetzGraph()
    
    print(f"Graf berhasil dibuat dengan {tonnetz.graph.number_of_nodes()} nodes dan {tonnetz.graph.number_of_edges()} edges")

    print("\n=== TESTING ===")
    while True:
        try:
            start = input("\nMasukkan chord awal (atau 'quit' untuk keluar): ").strip()
            if start.lower() == 'quit':
                break
                
            length = int(input("Masukkan panjang progresi: "))
            genre = input("Masukkan genre (jazz/rock/pop/hiphop/classical): ").strip().lower()
            
            if genre not in tonnetz.genre_weights:
                genre = 'pop'
                print(f"Genre tidak dikenali, menggunakan 'pop' sebagai default")
            
            progression = tonnetz.generate_progression(start, length, genre)
            print(f"\nGenerated Progression: {' -> '.join(progression)}")
 
            viz = input("Visualisasi graf? (y/n): ").strip().lower()
            if viz == 'y':
                tonnetz.visualize_graph(progression)
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nTerima kasih telah menggunakan Tonnetz Graph Implementation!")

if __name__ == "__main__":
        np.random.seed(42)  
main()