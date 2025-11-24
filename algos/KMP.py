import tkinter as tk
from time import perf_counter

class KMPVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("KMP String Search Visualization")
        self.root.configure(bg="#1e1e1e")

        # Title
        tk.Label(root, text="KMP String Search Visualization", font=("Helvetica", 18, "bold"), fg="#FFD700", bg="#1e1e1e").pack(pady=10)

        # Input Frame
        input_frame = tk.Frame(root, bg="#1e1e1e")
        input_frame.pack()

        tk.Label(input_frame, text="Text:", fg="white", bg="#1e1e1e", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.text_entry = tk.Entry(input_frame, width=40, font=("Helvetica", 12))
        self.text_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Pattern:", fg="white", bg="#1e1e1e", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.pattern_entry = tk.Entry(input_frame, width=40, font=("Helvetica", 12))
        self.pattern_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(root, text="Start Visualization", command=self.start_visualization, bg="#00ADB5", fg="blue",
                  font=("Helvetica", 12, "bold")).pack(pady=10)

        # Canvas
        self.canvas = tk.Canvas(root, width=1000, height=300, bg="#2e2e2e", highlightthickness=0)
        self.canvas.pack(pady=10)

        # LPS Label
        self.lps_label = tk.Label(root, text="LPS: []", fg="#00FFFF", bg="#1e1e1e", font=("Helvetica", 12, "bold"))
        self.lps_label.pack(pady=5)

        # Result Label
        self.result_label = tk.Label(root, text="", fg="white", bg="#1e1e1e", font=("Helvetica", 14, "bold"))
        self.result_label.pack(pady=10)

        # Legend
        legend_frame = tk.Frame(root, bg="#1e1e1e")
        legend_frame.pack(pady=10)
        legends = [
            ("🟠", "Currently compared", "#FFA500"),
            ("🟢", "Matched", "#00FF00"),
            ("🔴", "Mismatch", "#FF4444"),
            ("🟣", "Pattern found", "#B366FF")
        ]
        for icon, text, color in legends:
            tk.Label(legend_frame, text=f"{icon} {text}", fg=color, bg="#1e1e1e", font=("Helvetica", 11)).pack(side="left", padx=15)

    def compute_lps(self, pattern):
        lps = [0] * len(pattern)
        length = 0
        i = 1
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    def start_visualization(self):
        text = self.text_entry.get()
        pattern = self.pattern_entry.get()
        if not text or not pattern:
            self.result_label.config(text="Please enter both text and pattern.", fg="red")
            return

        self.canvas.delete("all")
        self.result_label.config(text="")
        self.visualize_kmp(text, pattern)

    def visualize_kmp(self, text, pattern):
        # Compute actual algorithm time (no animation)
        start_algo = perf_counter()
        matches, comparisons = self.kmp_algorithm(text, pattern)
        end_algo = perf_counter()
        algo_time = (end_algo - start_algo) * 1000

        # Now start visualization
        lps = self.compute_lps(pattern)
        self.lps_label.config(text=f"LPS: {lps}")

        x_start = 50
        y_text = 100
        y_pattern = 160

        text_labels = []
        for i, ch in enumerate(text):
            lbl = self.canvas.create_text(x_start + i * 25, y_text, text=ch, fill="white", font=("Helvetica", 14, "bold"))
            text_labels.append(lbl)

        pattern_labels = []
        for i, ch in enumerate(pattern):
            lbl = self.canvas.create_text(x_start + i * 25, y_pattern, text=ch, fill="gray", font=("Helvetica", 14, "bold"))
            pattern_labels.append(lbl)

        self.root.update()

        i = j = 0
        delay = 500
        comparisons_visual = 0
        matches_found = []

        def step():
            nonlocal i, j, comparisons_visual, matches_found

            if i < len(text):
                comparisons_visual += 1

                # Reset pattern colors
                for lbl in pattern_labels:
                    self.canvas.itemconfig(lbl, fill="gray")

                # Highlight current char in text
                self.canvas.itemconfig(text_labels[i], fill="#FFA500")  # orange

                # If match
                if text[i] == pattern[j]:
                    self.canvas.itemconfig(text_labels[i], fill="#00FF00")
                    self.canvas.itemconfig(pattern_labels[j], fill="#00FF00")
                    i += 1
                    j += 1
                else:
                    self.canvas.itemconfig(pattern_labels[j], fill="#FF4444")
                    if j != 0:
                        j = lps[j - 1]
                    else:
                        i += 1

                # Full pattern match
                if j == len(pattern):
                    start_index = i - j
                    matches_found.append(start_index)

                    # Highlight match in purple
                    for k in range(len(pattern)):
                        self.canvas.itemconfig(text_labels[start_index + k], fill="#B366FF")
                        self.canvas.itemconfig(pattern_labels[k], fill="#B366FF")

                    j = lps[j - 1]  # Continue searching

                self.root.after(delay, step)

            else:
                if matches_found:
                    self.result_label.config(
                        text=f"✅ Pattern found at indices: {matches_found}\n⏱ Time: {algo_time:.3f} ms\n🔁 Comparisons: {comparisons}",
                        fg="#B366FF"
                    )
                else:
                    self.result_label.config(
                        text=f"❌ Pattern not found\n⏱ Time: {algo_time:.3f} ms\n🔁 Comparisons: {comparisons}",
                        fg="#FF4444"
                    )

        self.root.after(delay, step)

    def kmp_algorithm(self, text, pattern):
        lps = self.compute_lps(pattern)
        i = j = comparisons = 0
        matches = []

        while i < len(text):
            comparisons += 1

            if text[i] == pattern[j]:
                i += 1
                j += 1

            if j == len(pattern):
                matches.append(i - j)
                j = lps[j - 1]  # continue searching

            elif i < len(text) and text[i] != pattern[j]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1

        return matches, comparisons


if __name__ == "__main__":
    root = tk.Tk()
    app = KMPVisualizer(root)
    root.mainloop()
