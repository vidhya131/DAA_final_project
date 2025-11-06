import tkinter as tk
from tkinter import messagebox
from time import perf_counter
import math

class GraphColoringVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Coloring Visualization")
        self.root.configure(bg="#1e1e1e")

        tk.Label(root, text="Graph Coloring Visualization",
                 font=("Helvetica", 18, "bold"), fg="#FFD700", bg="#1e1e1e").pack(pady=10)

        # Input frame
        input_frame = tk.Frame(root, bg="#1e1e1e")
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="Vertices:", fg="white", bg="#1e1e1e", font=("Helvetica", 12)).grid(row=0, column=0, padx=5)
        self.vertex_entry = tk.Entry(input_frame, width=5, font=("Helvetica", 12))
        self.vertex_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Edges (e.g. 0-1,0-2,1-3):", fg="white", bg="#1e1e1e", font=("Helvetica", 12)).grid(row=0, column=2, padx=5)
        self.edge_entry = tk.Entry(input_frame, width=30, font=("Helvetica", 12))
        self.edge_entry.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="No. of colors:", fg="white", bg="#1e1e1e", font=("Helvetica", 12)).grid(row=0, column=4, padx=5)
        self.color_entry = tk.Entry(input_frame, width=5, font=("Helvetica", 12))
        self.color_entry.grid(row=0, column=5, padx=5)

        # Algorithm selection dropdown
        tk.Label(input_frame, text="Algorithm:", fg="white", bg="#1e1e1e", font=("Helvetica", 12)).grid(row=0, column=6, padx=5)
        self.algorithm_var = tk.StringVar(value="Greedy")
        self.algorithm_menu = tk.OptionMenu(input_frame, self.algorithm_var, "Greedy", "Backtracking")
        self.algorithm_menu.config(font=("Helvetica", 12), bg="#00ADB5", fg="white")
        self.algorithm_menu.grid(row=0, column=7, padx=5)

        tk.Button(root, text="Start Visualization", command=self.start_visualization,
                  bg="#00A9B5", fg="blue", font=("Helvetica", 12, "bold")).pack(pady=10)

        # Canvas for drawing graph
        self.canvas = tk.Canvas(root, width=900, height=500, bg="#2e2e2e", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Result label
        self.result_label = tk.Label(root, text="", fg="white", bg="#1e1e1e", font=("Helvetica", 14, "bold"))
        self.result_label.pack(pady=10)

        # Legend
        legend_frame = tk.Frame(root, bg="#1e1e1e")
        legend_frame.pack(pady=10)
        legends = [
            ("🟠", "Currently processing vertex", "#FFA500"),
            ("🟢", "Colored successfully", "#00FF00"),
            ("🔴", "Conflict (no available color)", "#FF4444")
        ]
        for icon, text, color in legends:
            tk.Label(legend_frame, text=f"{icon} {text}", fg=color, bg="#1e1e1e", font=("Helvetica", 11)).pack(side="left", padx=15)

    def start_visualization(self):
        self.canvas.delete("all")
        self.result_label.config(text="")

        try:
            n = int(self.vertex_entry.get())
            k = int(self.color_entry.get())
            if n <= 0 or k <= 0:
                raise ValueError

            edges_input = self.edge_entry.get().strip()
            edges = []
            if edges_input:
                for e in edges_input.split(","):
                    parts = e.strip().split("-")
                    if len(parts) != 2:
                        raise ValueError
                    u, v = map(int, parts)
                    if u >= n or v >= n or u == v or u < 0 or v < 0:
                        raise ValueError
                    edges.append((u, v))
            else:
                messagebox.showerror("Input Error", "Please provide valid edges.")
                return
        except Exception:
            messagebox.showerror("Input Error", "Invalid input format for vertices, edges, or color count.")
            return

        algorithm = self.algorithm_var.get().lower()  # "greedy" or "backtracking"
        self.visualize_graph_coloring(n, edges, k, algorithm)

    # Visualization code remains same
    def visualize_graph_coloring(self, n, edges, max_colors, algorithm="greedy"):
        start_algo = perf_counter()
        if algorithm == "backtracking":
            coloring, steps = self.backtracking_coloring(n, edges, max_colors)
        else:
            coloring, steps = self.greedy_coloring(n, edges, max_colors)
        end_algo = perf_counter()
        algo_time = (end_algo - start_algo) * 1000.0

        # Layout positions for nodes
        radius = 180
        center_x, center_y = 450, 250
        self.node_positions = [
            (center_x + radius * math.cos(2 * math.pi * i / n),
             center_y + radius * math.sin(2 * math.pi * i / n)) for i in range(n)
        ]

        # Draw edges
        for u, v in edges:
            x1, y1 = self.node_positions[u]
            x2, y2 = self.node_positions[v]
            self.canvas.create_line(x1, y1, x2, y2, fill="#AAAAAA", width=2)

        # Draw nodes
        self.node_circles = []
        for i, (x, y) in enumerate(self.node_positions):
            circle = self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill="#808080", outline="white", width=2)
            label = self.canvas.create_text(x, y, text=str(i), fill="white", font=("Helvetica", 14, "bold"))
            self.node_circles.append((circle, label))

        base_palette = ["#FF6347", "#4682B4", "#32CD32", "#FFD700", "#DA70D6", "#FF8C00", "#00CED1", "#ADFF2F",
                        "#FF69B4", "#8A2BE2"]
        palette = base_palette[:max_colors] if max_colors <= len(base_palette) else (
            base_palette + ["#%06x" % (0x100000 + i) for i in range(max_colors - len(base_palette))])[:max_colors]

        delay = 800  # ms per node
        index = 0
        total_conflicts = sum(1 for c in coloring if c == -1)

        def animate_apply():
            nonlocal index
            if index >= n:
                used_colors = len({c for c in coloring if c != -1})
                conflict_text = f" (conflicts: {total_conflicts})" if total_conflicts > 0 else ""
                if conflict_text:
                    self.result_label.config(
                        text=(f"⚠️ Could not color using {max_colors} colors:{conflict_text}\n"),
                        fg="#FF0000"
                    )
                else:
                    self.result_label.config(
                        text=(f"✅ Colored using {used_colors} out of {max_colors} colors\n"
                              f"⏱ Algorithm time: {algo_time:.3f} ms\n"
                              f"🔁 Steps: {steps}"),
                        fg="#00FF00"
                    )
                return

            circle, label = self.node_circles[index]
            self.canvas.itemconfig(circle, fill="#FFA500")
            self.root.update()

            assigned = coloring[index]
            if assigned == -1:
                self.canvas.itemconfig(circle, fill="#FF4444")
            else:
                color_hex = palette[assigned % len(palette)]
                self.canvas.itemconfig(circle, fill=color_hex)

            index += 1
            self.root.after(delay, animate_apply)

        self.root.after(delay, animate_apply)

    #--------------------------------------------------------------
    # Backtracking algorithm
    def backtracking_coloring(self, n, edges, max_colors):
        adjacency = {i: [] for i in range(n)}
        for u, v in edges:
            adjacency[u].append(v)
            adjacency[v].append(u)

        result = [-1] * n
        steps = 0

        def is_safe(v, c):
            return all(result[neighbor] != c for neighbor in adjacency[v])

        def solve(v):
            nonlocal steps
            if v == n:
                return True
            steps += 1
            for c in range(max_colors):
                if is_safe(v, c):
                    result[v] = c
                    if solve(v + 1):
                        return True
                    result[v] = -1
            return False

        solve(0)
        return result, steps

    #--------------------------------------------------------------
    # Greedy algorithm
    def greedy_coloring(self, n, edges, max_colors):
        adjacency = {i: [] for i in range(n)}
        for u, v in edges:
            adjacency[u].append(v)
            adjacency[v].append(u)

        result = [-1] * n
        steps = 0
        for u in range(n):
            steps += 1
            used = [False] * max_colors
            for v in adjacency[u]:
                if result[v] != -1 and result[v] < max_colors:
                    used[result[v]] = True
            color = 0
            while color < max_colors and used[color]:
                color += 1
            if color < max_colors:
                result[u] = color
            else:
                result[u] = -1
        return result, steps

#--------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphColoringVisualizer(root)
    root.mainloop()
