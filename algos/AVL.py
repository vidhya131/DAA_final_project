import tkinter as tk
from tkinter import messagebox
from time import perf_counter, sleep

# ---------------- NODE STRUCTURE ----------------
class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1

# ---------------- AVL TREE LOGIC ----------------
class AVLTree:
    def insert(self, root, key, canvas=None, draw_callback=None, speed=1.0, highlight_node=None):
        """Insert key into AVL tree with optional visualization callbacks."""
        if not root:
            if draw_callback:
                draw_callback(f"Inserting {key}")
                sleep(1.0 / speed)
            return Node(key)

        if key < root.key:
            root.left = self.insert(root.left, key, canvas, draw_callback, speed, highlight_node)
        elif key > root.key:
            root.right = self.insert(root.right, key, canvas, draw_callback, speed, highlight_node)
        else:
            return root  # Duplicate keys not allowed

        # Update height
        root.height = 1 + max(self.getHeight(root.left), self.getHeight(root.right))
        balance = self.getBalance(root)

        # Balancing cases
        if balance > 1 and key < root.left.key:
            if draw_callback:
                draw_callback(f"LL Rotation at {root.key}", root)
                sleep(1.0 / speed)
            return self.rightRotate(root)

        if balance < -1 and key > root.right.key:
            if draw_callback:
                draw_callback(f"RR Rotation at {root.key}", root)
                sleep(1.0 / speed)
            return self.leftRotate(root)

        if balance > 1 and key > root.left.key:
            if draw_callback:
                draw_callback(f"LR Rotation at {root.key}", root)
                sleep(1.0 / speed)
            root.left = self.leftRotate(root.left)
            return self.rightRotate(root)

        if balance < -1 and key < root.right.key:
            if draw_callback:
                draw_callback(f"RL Rotation at {root.key}", root)
                sleep(1.0 / speed)
            root.right = self.rightRotate(root.right)
            return self.leftRotate(root)

        if draw_callback:
            draw_callback(f"Inserting {key}", root)
            sleep(1.0 / speed)
        return root

    # Rotation helpers
    def leftRotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.getHeight(z.left), self.getHeight(z.right))
        y.height = 1 + max(self.getHeight(y.left), self.getHeight(y.right))
        return y

    def rightRotate(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self.getHeight(z.left), self.getHeight(z.right))
        y.height = 1 + max(self.getHeight(y.left), self.getHeight(y.right))
        return y

    def getHeight(self, node):
        return 0 if not node else node.height

    def getBalance(self, node):
        return 0 if not node else self.getHeight(node.left) - self.getHeight(node.right)

# ---------------- VISUALIZATION ----------------
class AVLVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("AVL Tree Visualization")
        self.tree = AVLTree()
        self.root_node = None
        self.speed = tk.DoubleVar(value=1.0)

        # Canvas
        self.canvas = tk.Canvas(root, width=950, height=550, bg="#1e1e1e")
        self.canvas.pack(pady=10)

        # Controls
        frame = tk.Frame(root, bg="#2d2d2d")
        frame.pack(pady=10, fill="x")

        tk.Label(frame, text="Insert List (comma-separated):", bg="#2d2d2d", fg="white").pack(side="left", padx=5)
        self.entry = tk.Entry(frame, width=40)
        self.entry.pack(side="left", padx=5)

        tk.Button(frame, text="Insert All", command=self.insert_list, bg="#4a90e2", fg="black").pack(side="left", padx=5)

        tk.Label(frame, text="Speed (1x - 5x):", bg="#2d2d2d", fg="white").pack(side="left", padx=5)
        tk.Scale(frame, from_=0.5, to=5.0, resolution=0.1, orient="horizontal", variable=self.speed).pack(side="left")

        # Info
        self.info_label = tk.Label(root, text="", fg="#ffcc00", bg="#1e1e1e", font=("Arial", 12))
        self.info_label.pack()
        self.time_label = tk.Label(root, text="", fg="#00ff99", bg="#1e1e1e", font=("Arial", 12))
        self.time_label.pack()
        self.final_list_label = tk.Label(root, text="", fg="#00bfff", bg="#1e1e1e", font=("Arial", 12))
        self.final_list_label.pack()

    # Recursive draw
    def draw_tree(self, node=None, highlight_node=None, x=475, y=60, dx=180):
        self.canvas.delete("all")
        if node:
            self._draw(node, x, y, dx, highlight_node)

    def _draw(self, node, x, y, dx, highlight_node):
        if node.left:
            self.canvas.create_line(x, y, x - dx, y + 80, fill="white", width=2)
            self._draw(node.left, x - dx, y + 80, dx / 1.6, highlight_node)
        if node.right:
            self.canvas.create_line(x, y, x + dx, y + 80, fill="white", width=2)
            self._draw(node.right, x + dx, y + 80, dx / 1.6, highlight_node)

        # Node color highlighting
        fill_color = "#4a90e2"
        outline_color = "white"
        if highlight_node and node.key == highlight_node.key:
            fill_color = "#ff4444"  # red for rotation
            outline_color = "#ffcc00"

        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=fill_color, outline=outline_color, width=2)
        self.canvas.create_text(x, y, text=str(node.key), fill="white", font=("Helvetica", 14, "bold"))
        bf = self.tree.getBalance(node)
        self.canvas.create_text(x, y + 30, text=f"BF={bf}", fill="#ffcc00", font=("Arial", 10))

    # Callback for drawing + messages
    def draw_callback(self, msg=None, highlight_node=None):
        if msg:
            self.info_label.config(text=msg)
        self.draw_tree(self.root_node, highlight_node)
        self.root.update()

    # Insert list of nodes
    def insert_list(self):
        # Clear previous results
        self.info_label.config(text="")
        self.time_label.config(text="")
        self.final_list_label.config(text="")
        self.canvas.delete("all")
        self.root_node = None

        raw_input = self.entry.get().strip()
        if not raw_input:
            messagebox.showerror("Error", "Please enter a list of numbers (e.g. 10,20,30,40).")
            return

        try:
            keys = [int(x.strip()) for x in raw_input.split(",")]
        except ValueError:
            messagebox.showerror("Error", "All inputs must be integers separated by commas.")
            return

        # Measure actual runtime (no animation)
        start_algo = perf_counter()
        temp_tree = None
        for k in keys:
            temp_tree = self.tree.insert(temp_tree, k)
        end_algo = perf_counter()
        actual_time_ms = (end_algo - start_algo) * 1000
        print(f"Actual AVL Algorithm Time (no animation): {actual_time_ms:.3f} ms")

        # Now perform visualized insertions
        self.root_node = None
        for k in keys:
            self.info_label.config(text=f"Inserting {k} ...")
            self.root_node = self.tree.insert(
                self.root_node, k, self.canvas, self.draw_callback, self.speed.get()
            )
            self.draw_tree(self.root_node)
            self.root.update()

        # Compute final AVL tree list (level order)
        final_list = self.level_order(self.root_node)
        self.info_label.config(text="All insertions complete.")
        self.time_label.config(text=f"Actual AVL Algorithm Time: {actual_time_ms:.3f} ms")
        self.final_list_label.config(text=f"Final AVL Tree (Level Order): {final_list}")
        self.entry.delete(0, "end")

    # Level order traversal
    def level_order(self, root):
        if not root:
            return []
        queue = [root]
        result = []
        while queue:
            node = queue.pop(0)
            result.append(node.key)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result

# ---------------- MAIN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AVLVisualizer(root)
    root.mainloop()
