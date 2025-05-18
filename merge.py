import tkinter as tk
from tkinter import messagebox
import random
import time

# Genetic Algorithm 
def evaluate_fitness(grid, N):
    penalty = 0
    
    for row in grid:
        counts = {}
        for val in row:
            counts[val] = counts.get(val, 0) + 1
        for count in counts.values():
            if count > 1:
                penalty += (count - 1)
    
    for col in range(N):
        counts = {}
        for row in range(N):
            val = grid[row][col]
            counts[val] = counts.get(val, 0) + 1
        for count in counts.values():
            if count > 1:
                penalty += (count - 1)
    return 1 / (1 + penalty)

def tournament_selection(pop, fitnesses, k=3):
    selected = []
    for _ in range(2):
        group = random.sample(list(zip(pop, fitnesses)), k)
        selected.append(max(group, key=lambda x: x[1])[0])
    return selected

def crossover(p1, p2, N):
    point = random.randint(1, N - 1)
    c1 = p1[:point] + p2[point:]
    c2 = p2[:point] + p1[point:]
    return c1, c2

def mutate(grid, N):
    row = random.randint(0, N - 1)
    col1, col2 = random.sample(range(N), 2)
    grid[row][col1], grid[row][col2] = grid[row][col2], grid[row][col1]

def generate_random_grid(N):
    return [random.sample(range(1, N + 1), N) for _ in range(N)]

def genetic_latin_square(N, pop_size=100, generations=1000):
    pop = [generate_random_grid(N) for _ in range(pop_size)]
    for _ in range(generations):
        fitnesses = [evaluate_fitness(ind, N) for ind in pop]
        max_fit = max(fitnesses)
        if max_fit == 1:
            return pop[fitnesses.index(max_fit)]
        new_pop = []
        while len(new_pop) < pop_size:
            p1, p2 = tournament_selection(pop, fitnesses)
            c1, c2 = crossover(p1, p2, N)
            mutate(c1, N)
            mutate(c2, N)
            new_pop += [c1, c2]
        pop = new_pop
    return pop[fitnesses.index(max_fit)]

# Backtracking
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

# KenKen Game Functions 
colors = [
    "#FFC0CB", "#87CEFA", "#90EE90", "#FFD700",
    "#DDA0DD", "#FFA07A", "#98FB98", "#AFEEEE",
    "#F08080", "#FF5733", "#DFFF00", "#40E0D0", "#CCCCFF"
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
        cells = [(x, y) for y in range(size) for x in range(size) if regions[y][x] == region_id]
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

# Main KenKen UI 
def create_kenken_ui():
    root = tk.Tk()
    root.title("KenKen Puzzle Generator")

    timer_label = tk.Label(root, text="Time: 0s", font=("Arial", 12))
    timer_label.pack()

    entries = []
    grid_frame = tk.Frame(root)
    grid_frame.pack()

    size_var = tk.IntVar(value=3)
    method_var = tk.StringVar(value="Backtracking")
    solution = []
    start_time = [None]

    def update_timer():
        if start_time[0]:
            elapsed = int(time.time() - start_time[0])
            timer_label.config(text=f"Time: {elapsed}s")
            root.after(1000, update_timer)

    def generate():
        size = size_var.get()
        solution.clear()

        if method_var.get() == "Backtracking":
            result = solve_latin_square(size)
        else:
            result = genetic_latin_square(size)

        if not result:
            messagebox.showerror("Error", "Couldn't generate a solution")
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

    def compare_methods():
        size = size_var.get()
        # Backtracking
        start_bt = time.time()
        sol_bt = solve_latin_square(size)
        time_bt = time.time() - start_bt
        fitness_bt = evaluate_fitness(sol_bt, size) if sol_bt else 0

        # Genetic
        start_gen = time.time()
        sol_gen = genetic_latin_square(size)
        time_gen = time.time() - start_gen
        fitness_gen = evaluate_fitness(sol_gen, size) if sol_gen else 0

        msg = (
            f"Comparison for size {size}:\n\n"
            f"Backtracking:\n- Time: {time_bt:.4f} seconds\n- Fitness: {fitness_bt:.4f}\n\n"
            f"Genetic Algorithm:\n- Time: {time_gen:.4f} seconds\n- Fitness: {fitness_gen:.4f}"
        )
        messagebox.showinfo("Method Comparison", msg)

    control_frame = tk.Frame(root)
    control_frame.pack(pady=10)

    tk.Label(control_frame, text="Size:").pack(side=tk.LEFT)
    tk.OptionMenu(control_frame, size_var, *[i for i in range(3, 10)]).pack(side=tk.LEFT, padx=5)

    tk.Label(control_frame, text="Method:").pack(side=tk.LEFT)
    tk.OptionMenu(control_frame, method_var, "Backtracking", "Genetic").pack(side=tk.LEFT, padx=5)

    tk.Button(control_frame, text="Generate", command=generate).pack(side=tk.LEFT, padx=5)
    tk.Button(control_frame, text="Solve", command=solve).pack(side=tk.LEFT, padx=5)
    tk.Button(control_frame, text="Check", command=check).pack(side=tk.LEFT, padx=5)
    tk.Button(control_frame, text="Compare Methods", command=compare_methods).pack(side=tk.LEFT, padx=5)

    root.mainloop()

create_kenken_ui()
