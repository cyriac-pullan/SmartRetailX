import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import platform
import subprocess
import os

class StoreVisualizer:
    def __init__(self, partition_map):
        """
        partition_map: dict of {position_tag: (x, y)}
        """
        self.node_positions = partition_map
        self.aisle_width = 3
        self.aisle_height = 8
        self.padding = 2

    def generate_map(self, path_nodes_list, start_node, target_node, rec_node=None):
        fig, ax = plt.subplots(figsize=(8, 10))
        
        # 1. DRAW LAYOUT (Simplistic Grid)
        # We assume 5 Aisles
        aisle_configs = [
            (1, "Impulse/Snacks", 2, 2, "red"),
            (2, "Staples", 6, 2, "orange"),
            (3, "Personal/Home", 10, 2, "blue"),
            (4, "Dairy/Bakery", 14, 2, "green"),
            (5, "Fresh Produce", 18, 2, "purple"),
        ]
        
        for num, name, x, y, color in aisle_configs:
            # Draw Aisle Rect
            rect = patches.Rectangle((x, y), 2, 10, linewidth=1, edgecolor=color, facecolor='none')
            ax.add_patch(rect)
            ax.text(x+1, y+11, f"Aisle {num}\n{name}", ha='center', fontsize=8, color=color, weight='bold')
            
        # 2. DRAW PATH
        xs = []
        ys = []
        
        for node in path_nodes_list:
            if node in self.node_positions:
                pos = self.node_positions[node]
                xs.append(pos[0])
                ys.append(pos[1])
                
        if xs:
            ax.plot(xs, ys, color='black', linestyle='--',  linewidth=2, marker='o', markersize=4, label='Path')
            
        # 3. HIGHLIGHT POINTS
        if start_node in self.node_positions:
            sx, sy = self.node_positions[start_node]
            ax.plot(sx, sy, marker='o', color='blue', markersize=10)
            ax.text(sx+0.5, sy, "YOU", fontsize=9, color='blue', weight='bold')

        if target_node in self.node_positions:
            tx, ty = self.node_positions[target_node]
            ax.plot(tx, ty, marker='*', color='red', markersize=15)
            ax.text(tx+0.5, ty, "TARGET", fontsize=9, color='red', weight='bold')

        if rec_node and rec_node in self.node_positions:
            rx, ry = self.node_positions[rec_node]
            ax.plot(rx, ry, marker='D', color='gold', markersize=10)
            ax.text(rx+0.5, ry, "SUGGESTION", fontsize=8, color='darkgoldenrod', weight='bold')

        # Formatting
        ax.set_xlim(0, 22)
        ax.set_ylim(0, 15)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("Store Navigation Map")
        ax.legend(loc='lower right')
        
        # Save
        filename = "navigation_map.png"
        plt.savefig(filename)
        plt.close()
        print(f"🗺️  Map generated: {filename}")
        
        # Open
        self.open_image(filename)

    def open_image(self, path):
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        elif platform.system() == "Windows":
            os.startfile(path)
        else:  # Linux
            subprocess.run(["xdg-open", path])
