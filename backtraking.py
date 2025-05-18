import tkinter as tk
from tkinter import messagebox
import random
import time

#  Backtracking  
def solve_latin_square(size):
    square = [[0 for _ in range(size)] for _ in range(size)]

    def is_valid(r, c, val):
        for i in range(size):
            if square[r][i] == val or square[i][c] == val:
                return False
        return True

    def backtrack(r, c):
        if r == size:
            return True
        if c == size:
            return backtrack(r + 1, 0)

        for val in range(1, size + 1):
            if is_valid(r, c, val):
                square[r][c] = val
                if backtrack(r, c + 1):
                    return True
                square[r][c] = 0
        return False

    if backtrack(0, 0):
        return square
    else:
        return None

#  KenKen Game Functions gui 

colors = [
    "#FFC0CB", "#87CEFA", "#90EE90", "#FFD700",
    "#DDA0DD", "#FFA07A", "#98FB98", "#AFEEEE", "#F08080" ,"#DFFF00" , "#40E0D0" , "#CCCCFF"
]

def generate_regions(size):
    regions = [[-1 for _ in range(size)] for _ in range(size)]
    current_region = 0

    def neighbors(x, y):
        return [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= x + dx < size and 0 <= y + dy < size]

    unvisited = [(x, y) for y in range(size) for x in range(size)]
    random.shuffle(unvisited)

    while unvisited:
        x, y = unvisited.pop()
        if regions[y][x] != -1:
            continue
        region_size = random.choice([1, 2, 3])
        region_cells = [(x, y)]
        regions[y][x] = current_region
        for _ in range(region_size - 1):
            possible = [n for cell in region_cells for n in neighbors(*cell)
                        if regions[n[1]][n[0]] == -1 and n in unvisited]
            if not possible:
                break
            nx, ny = random.choice(possible)
            regions[ny][nx] = current_region
            region_cells.append((nx, ny))
            unvisited.remove((nx, ny))
        current_region += 1
    return regions

def assign_operators(solution, regions):
    size = len(solution)
    ops = []
    for region_id in range(max(max(row) for row in regions) + 1):
        cells = [(x, y) for y in range(size) for x in range(size)
                if regions[y][x] == region_id]
        values = [solution[y][x] for (x, y) in cells]

        if len(values) == 1:
            ops.append((region_id, str(values[0]), ""))
        elif len(values) == 2:
            a, b = values
            if a % b == 0:
                ops.append((region_id, str(a // b), "/"))
            elif b % a == 0:
                ops.append((region_id, str(b // a), "/"))
            elif a - b > 0:
                ops.append((region_id, str(a - b), "-"))
            elif b - a > 0:
                ops.append((region_id, str(b - a), "-"))
            else:
                ops.append((region_id, str(b * a), "*"))
        else:
            total = sum(values)
            ops.append((region_id, str(total), "+"))
    return ops

def get_operator_label(operators, regions, y, x):
    region_id = regions[y][x]
    for rid, val, op in operators:
        if rid == region_id:
            for yy in range(len(regions)):
                for xx in range(len(regions)):
                    if regions[yy][xx] == region_id:
                        if yy == y and xx == x:
                            return val + op
                        else:
                            return ""
    return ""

def create_kenken_ui():
    root = tk.Tk()
    root.title("KenKen with Backtracking")

    timer_label = tk.Label(root, text="Time: 0s", font=("Arial", 12))
    timer_label.pack()

    entries = []
    grid_frame = tk.Frame(root)
    grid_frame.pack()

    size_var = tk.IntVar(value=3)
    def update_timer():
        if start_time[0]:
            elapsed = int(time.time() - start_time[0])
            timer_label.config(text=f"Time: {elapsed}s")
            root.after(1000, update_timer)

    def generate():
        size = size_var.get()
        solution.clear()
        result = solve_latin_square(size)
        if not result:
            messagebox.showerror("Error", "Couldn't generate solution")
            return

        solution.extend(result)
        regions = generate_regions(size)
        operators = assign_operators(solution, regions)

        for widget in grid_frame.winfo_children():
            widget.destroy()

        entries.clear()
        for y in range(size):
            row = []
            for x in range(size):
                frame = tk.Frame(
                    grid_frame,
                    highlightbackground="black",
                    highlightthickness=1,
                    bg=colors[regions[y][x] % len(colors)]
                )
                frame.grid(row=y, column=x, padx=1, pady=1)
                label_text = get_operator_label(operators, regions, y, x)
                if label_text:
                    tk.Label(frame, text=label_text, font=("Arial", 8), bg=frame["bg"]).pack(anchor="nw")
                entry = tk.Entry(frame, width=2, font=("Arial", 20), justify="center")
                entry.pack(padx=5, pady=5)
                row.append(entry)
            entries.append(row)
        start_time[0] = time.time()
        update_timer()

    def solve():
        for y in range(len(entries)):
            for x in range(len(entries)):
                entries[y][x].delete(0, tk.END)
                entries[y][x].insert(0, str(solution[y][x]))

    def check():
        for y in range(len(entries)):
            for x in range(len(entries)):
                val = entries[y][x].get()
                if not val.isdigit() or int(val) != solution[y][x]:
                    messagebox.showwarning("KenKen", "Incorrect! Try again.")
                    return
        messagebox.showinfo("KenKen", "Correct! You solved the puzzle!")

    control_frame = tk.Frame(root)
    control_frame.pack(pady=10)

    tk.Label(control_frame, text="Size:").pack(side=tk.LEFT)
    tk.OptionMenu(control_frame, size_var, *[i for i in range(3, 10)]).pack(side=tk.LEFT)
    tk.Button(control_frame, text="Generate", command=generate).pack(side=tk.LEFT, padx=5)
    tk.Button(control_frame, text="Solve", command=solve).pack(side=tk.LEFT, padx=5)
    tk.Button(control_frame, text="Check", command=check).pack(side=tk.LEFT, padx=5)

    root.mainloop()

solution = []
start_time = [None]
create_kenken_ui()
