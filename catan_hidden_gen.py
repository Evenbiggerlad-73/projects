import tkinter as tk
from tkinter import messagebox, ttk
import math
import random

# --- Constants & Configuration ---
HEX_RADIUS = 40
COLORS = {
    "Sea": "#1E90FF",
    "Forest": "#228B22",
    "Hills": "#B22222",
    "Pasture": "#7CFC00",
    "Fields": "#DAA520",
    "Mountains": "#808080",
    "Gold": "#FFD700",
    "Desert": "#F4A460",
    "Fog": "#A9A9A9",
    "Unknown": "#FFFFFF",
    "Border": "#000000"
}

RESOURCE_TYPES = ["Sea", "Forest", "Hills", "Pasture", "Fields", "Mountains", "Gold", "Desert"]

RESOURCE_ICONS = {
    "Forest": "🌲",
    "Hills": "⛰️",
    "Pasture": "🐑",
    "Fields": "🌾",
    "Mountains": "🏔️",
    "Gold": "💰",
    "Desert": "🏜️",
    "Sea": "🌊",
    "Fog": "☁️",
    "Unknown": "❓"
}

# --- Hex Math ---
class Hex:
    def __init__(self, q, r):
        self.q = q
        self.r = r

    def __eq__(self, other):
        return self.q == other.q and self.r == other.r

    def __hash__(self):
        return hash((self.q, self.r))

    def get_neighbors(self):
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [Hex(self.q + dq, self.r + dr) for dq, dr in directions]

def hex_to_pixel(q, r, radius):
    x = radius * math.sqrt(3) * (q + r/2)
    y = radius * 3/2 * r
    return x, y

def pixel_to_hex(x, y, radius):
    q = (math.sqrt(3)/3 * x - 1/3 * y) / radius
    r = (2/3 * y) / radius
    return hex_round(q, r)

def hex_round(q, r):
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s)
    if dq > dr and dq > ds:
        rq = -rr - rs
    elif dr > ds:
        rr = -rq - rs
    return rq, rr

# --- Data Models ---
class IslandGroup:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.tile_pool = []  # List of strings
        self.number_pool = [] # List of ints
        
    def add_tile(self, resource, count=1):
        for _ in range(count):
            self.tile_pool.append(resource)
            
    def remove_tile(self, resource):
        if resource in self.tile_pool:
            self.tile_pool.remove(resource)

    def add_number(self, number, count=1):
        for _ in range(count):
            self.number_pool.append(number)
            
    def remove_number(self, number):
        if number in self.number_pool:
            self.number_pool.remove(number)

class TileData:
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.island_id = 0 # 0 means unassigned
        self.resource = None
        self.number = None
        self.revealed = False

# --- Main Application ---
class CatanGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Catan Seafarers Hidden Island Generator")
        
        # Offset for dragging/panning grid - MUST be before setup_ui
        self.offset_x = 400
        self.offset_y = 300

        self.mode = "EDITOR" # EDITOR or PLAY
        self.selected_island_id = 1
        self.islands = {i: IslandGroup(i, f"Island {i}") for i in range(1, 4)}
        
        self.tiles = {} # (q, r) -> TileData
        
        self.setup_ui()

    def setup_ui(self):
        # Main Layout: Left = Canvas, Right = Controls
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#87CEEB")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel) # Windows
        self.canvas.bind("<Button-4>", self.on_mousewheel) # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel) # Linux scroll down
        
        self.sidebar = tk.Frame(self.main_frame, width=300, padx=10, pady=10)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mode Toggle
        mode_frame = tk.Frame(self.sidebar)
        mode_frame.pack(fill=tk.X)
        self.mode_btn = tk.Button(mode_frame, text="Switch to PLAY Mode", command=self.toggle_mode, bg="orange", width=20)
        self.mode_btn.pack(side=tk.LEFT, pady=5)
        
        # Manual Override Toggle
        self.manual_var = tk.BooleanVar(value=False)
        self.manual_cb = tk.Checkbutton(self.sidebar, text="Manual Placement", variable=self.manual_var)
        self.manual_cb.pack(pady=2)

        # Island Management
        manage_frame = tk.LabelFrame(self.sidebar, text="Manage Island Groups")
        manage_frame.pack(fill=tk.X, pady=5)
        
        btn_grid = tk.Frame(manage_frame)
        btn_grid.pack(pady=2)
        tk.Button(btn_grid, text="-", width=3, command=self.remove_island_group).pack(side=tk.LEFT, padx=5)
        self.island_count_lbl = tk.Label(btn_grid, text="3 Islands")
        self.island_count_lbl.pack(side=tk.LEFT, padx=5)
        tk.Button(btn_grid, text="+", width=3, command=self.add_island_group).pack(side=tk.LEFT, padx=5)

        # Island Selection
        tk.Label(self.sidebar, text="Active Island Group:").pack(anchor=tk.W)
        self.island_selector_frame = tk.Frame(self.sidebar)
        self.island_selector_frame.pack(fill=tk.X)
        self.island_var = tk.IntVar(value=1)
        self.update_island_selectors()

        # Randomize Pool Buttons
        rand_frame = tk.Frame(self.sidebar)
        rand_frame.pack(fill=tk.X, pady=2)
        tk.Button(rand_frame, text="Small", command=lambda: self.randomize_pool("small"), width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(rand_frame, text="Med", command=lambda: self.randomize_pool("med"), width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(rand_frame, text="Large", command=lambda: self.randomize_pool("large"), width=6).pack(side=tk.LEFT, padx=2)

        # Custom Random Count
        custom_frame = tk.Frame(self.sidebar)
        custom_frame.pack(fill=tk.X, pady=2)
        tk.Label(custom_frame, text="Custom:").pack(side=tk.LEFT)
        self.custom_rand_var = tk.StringVar(value="5")
        tk.Entry(custom_frame, textvariable=self.custom_rand_var, width=5).pack(side=tk.LEFT, padx=5)
        tk.Button(custom_frame, text="Go", command=lambda: self.randomize_pool("custom"), width=4).pack(side=tk.LEFT)
            
        # Pool Configuration
        tk.Label(self.sidebar, text="--- Island Config ---", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        
        self.scroll_canvas = tk.Canvas(self.sidebar, borderwidth=0, highlightthickness=0, width=280)
        self.scroll_frame = tk.Frame(self.scroll_canvas)
        self.vsb = tk.Scrollbar(self.sidebar, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scroll_canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))

        # Resource Counters
        tk.Label(self.scroll_frame, text="Resources:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=2)
        self.res_vars = {} # resource -> StringVar
        for res in RESOURCE_TYPES:
            frame = tk.Frame(self.scroll_frame)
            frame.pack(fill=tk.X)
            
            lbl = tk.Label(frame, text=res, width=10, anchor=tk.W)
            lbl.pack(side=tk.LEFT)
            
            btn_minus = tk.Button(frame, text="-", width=2, command=lambda r=res: self.adj_res(r, -1))
            btn_minus.pack(side=tk.LEFT)
            
            v = tk.StringVar(value="0")
            self.res_vars[res] = v
            tk.Label(frame, textvariable=v, width=3).pack(side=tk.LEFT)
            
            btn_plus = tk.Button(frame, text="+", width=2, command=lambda r=res: self.adj_res(r, 1))
            btn_plus.pack(side=tk.LEFT)

        # Number Counters
        tk.Label(self.scroll_frame, text="Numbers:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10, 2))
        self.num_vars = {} # num -> StringVar
        possible_nums = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]
        
        # Grid for numbers to save space
        num_grid = tk.Frame(self.scroll_frame)
        num_grid.pack(fill=tk.X)
        for i, num in enumerate(possible_nums):
            row = i // 2
            col = (i % 2) * 4
            
            tk.Label(num_grid, text=str(num), width=3).grid(row=row, column=col)
            tk.Button(num_grid, text="-", width=1, command=lambda n=num: self.adj_num(n, -1)).grid(row=row, column=col+1)
            
            v = tk.StringVar(value="0")
            self.num_vars[num] = v
            tk.Label(num_grid, textvariable=v, width=2).grid(row=row, column=col+2)
            
            tk.Button(num_grid, text="+", width=1, command=lambda n=num: self.adj_num(n, 1)).grid(row=row, column=col+3)

        self.stats_lbl = tk.Label(self.sidebar, text="Total: 0 Tiles, 0 Numbers", fg="blue")
        self.stats_lbl.pack(pady=5)

        tk.Label(self.sidebar, text="Instructions:\n1. EDITOR: Click/Drag to place hexes.\n2. Set pools using +/- buttons.\n3. Click 'PLAY' to shuffle.\n4. Click Fog to reveal.", justify=tk.LEFT).pack(pady=10)

        # Initialize pools for island 1
        self.change_active_island()

    def update_island_selectors(self):
        for widget in self.island_selector_frame.winfo_children():
            widget.destroy()
        
        # Create a grid or wrap for radio buttons if there are many
        for i in sorted(self.islands.keys()):
            rb = tk.Radiobutton(self.island_selector_frame, text=f"I{i}", variable=self.island_var, value=i, 
                           command=self.change_active_island, indicatoron=0, width=4)
            rb.pack(side=tk.LEFT, padx=2)
        
        self.island_count_lbl.config(text=f"{len(self.islands)} Islands")

    def add_island_group(self):
        new_id = max(self.islands.keys()) + 1 if self.islands else 1
        if new_id > 12: return # Limit to 12 islands for UI sanity
        self.islands[new_id] = IslandGroup(new_id, f"Island {new_id}")
        self.update_island_selectors()

    def randomize_pool(self, size):
        island = self.islands[self.selected_island_id]
        island.tile_pool = []
        island.number_pool = []
        
        # Calculate base hex count for this island
        hex_count = sum(1 for t in self.tiles.values() if t.island_id == self.selected_island_id)
        if hex_count == 0:
            messagebox.showwarning("Warning", f"Place some hexes for Island {self.selected_island_id} first!")
            return

        if size == "small":
            counts = hex_count
        elif size == "med":
            counts = hex_count + 4
        elif size == "large":
            counts = hex_count * 2
        elif size == "custom":
            try:
                counts = int(self.custom_rand_var.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid custom count")
                return
        
        # Land distribution
        land_types = [t for t in RESOURCE_TYPES if t not in ["Sea", "Desert"]]
        for _ in range(counts - 1):
            island.add_tile(random.choice(land_types))
        
        # Add Desert or another land
        if random.random() > 0.3:
            island.add_tile("Desert")
        else:
            island.add_tile(random.choice(land_types))
        
        # Numbers distribution (standard Catan-ish frequencies)
        standard_nums = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        
        # We need as many numbers as there are land tiles (Desert and Sea don't get numbers)
        # To be safe, we'll just fill the number pool to match the tile pool size (minus estimated deserts)
        num_required = counts
        for i in range(num_required):
            island.add_number(standard_nums[i % len(standard_nums)])
            
        self.update_ui_counts()

    def remove_island_group(self):
        if len(self.islands) <= 1: return
        max_id = max(self.islands.keys())
        
        # Reassign tiles from this island to unassigned (0)
        for tile in self.tiles.values():
            if tile.island_id == max_id:
                tile.island_id = 0 
        
        # Clean up tiles that are now unassigned (remove them)
        self.tiles = {k: v for k, v in self.tiles.items() if v.island_id != 0}
        
        del self.islands[max_id]
        if self.selected_island_id == max_id:
            self.island_var.set(1)
            self.change_active_island()
        self.update_island_selectors()
        self.refresh_canvas()

    def toggle_mode(self):
        if self.mode == "EDITOR":
            if self.finalize_map():
                self.mode = "PLAY"
                self.mode_btn.config(text="Switch to EDITOR Mode", bg="lightgreen")
                self.refresh_canvas()
        else:
            self.mode = "EDITOR"
            self.mode_btn.config(text="Switch to PLAY Mode", bg="orange")
            # Reset reveal status
            for tile in self.tiles.values():
                tile.revealed = False
            self.refresh_canvas()

    def adj_res(self, res, delta):
        island = self.islands[self.selected_island_id]
        if delta > 0:
            island.add_tile(res)
        else:
            island.remove_tile(res)
        self.update_ui_counts()

    def adj_num(self, num, delta):
        island = self.islands[self.selected_island_id]
        if delta > 0:
            island.add_number(num)
        else:
            island.remove_number(num)
        self.update_ui_counts()

    def update_ui_counts(self):
        island = self.islands[self.selected_island_id]
        for res in RESOURCE_TYPES:
            self.res_vars[res].set(str(island.tile_pool.count(res)))
        for num in self.num_vars:
            self.num_vars[num].set(str(island.number_pool.count(num)))
        
        hex_count = sum(1 for t in self.tiles.values() if t.island_id == self.selected_island_id)
        # Max land tiles possible from current pool
        max_land_in_pool = len([r for r in island.tile_pool if r not in ["Sea", "Desert"]])
        # We need at least as many numbers as there are land tiles in the pool that COULD be picked, 
        # OR just as many as the hex_count (if all picked were land). 
        # Safest bet for the user is having enough numbers for the hex_count.
        self.stats_lbl.config(text=f"Placed: {hex_count} hexes\nPool: {len(island.tile_pool)} Tiles, {len(island.number_pool)} Numbers\nMax Land Possible: {min(hex_count, max_land_in_pool)}")

    def change_active_island(self):
        self.selected_island_id = self.island_var.get()
        self.update_ui_counts()
        self.refresh_canvas()

    def update_island_config(self):
        pass # No longer needed with instant updates

    def on_canvas_click(self, event):
        q, r = pixel_to_hex(event.x - self.offset_x, event.y - self.offset_y, HEX_RADIUS)
        coord = (q, r)
        
        if self.mode == "EDITOR":
            if coord in self.tiles and self.tiles[coord].island_id == self.selected_island_id:
                # Remove if same island
                del self.tiles[coord]
            else:
                # Add or change island
                new_tile = TileData(q, r)
                new_tile.island_id = self.selected_island_id
                self.tiles[coord] = new_tile
            self.update_ui_counts()
            self.refresh_canvas()
        
        elif self.mode == "PLAY":
            if coord in self.tiles:
                self.tiles[coord].revealed = True
                self.refresh_canvas()

    def on_canvas_drag(self, event):
        if self.mode == "EDITOR":
            q, r = pixel_to_hex(event.x - self.offset_x, event.y - self.offset_y, HEX_RADIUS)
            coord = (q, r)
            if coord not in self.tiles or self.tiles[coord].island_id != self.selected_island_id:
                new_tile = TileData(q, r)
                new_tile.island_id = self.selected_island_id
                self.tiles[coord] = new_tile
                self.update_ui_counts()
                self.refresh_canvas()

    def on_mousewheel(self, event):
        # Pan the view
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0): # Up
            self.offset_y += 20
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0): # Down
            self.offset_y -= 20
        self.refresh_canvas()

    def finalize_map(self):
        # Group tiles by island
        island_tiles = {}
        for tile in self.tiles.values():
            if tile.island_id not in island_tiles:
                island_tiles[tile.island_id] = []
            island_tiles[tile.island_id].append(tile)
        
        # Validate and Shuffe each island
        for island_id, tiles in island_tiles.items():
            island = self.islands.get(island_id)
            if not island: continue
            
            if len(island.tile_pool) < len(tiles):
                messagebox.showerror("Error", f"Island {island_id} has {len(tiles)} hexes on board, but only {len(island.tile_pool)} tiles in pool!")
                return False
            
            # Shuffle and sample resources
            res_sample = random.sample(island.tile_pool, len(tiles))
            for i, tile in enumerate(tiles):
                tile.resource = res_sample[i]
                tile.number = None # Reset
            
            # Identify tiles needing numbers
            num_required_tiles = [t for t in tiles if t.resource not in ["Sea", "Desert"]]
            if len(island.number_pool) < len(num_required_tiles):
                 messagebox.showerror("Error", f"Island {island_id} sampled {len(num_required_tiles)} land hexes, but only {len(island.number_pool)} numbers in pool!")
                 return False
            
            # Sample numbers from the pool
            num_sample = random.sample(island.number_pool, len(num_required_tiles))

            if self.manual_var.get():
                # Order numbers by frequency (best first) for manual placement
                # Frequencies: 6,8 > 5,9 > 4,10 > 3,11 > 2,12
                def score(n):
                    return {6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}.get(n, 0)
                
                num_sample.sort(key=score, reverse=True)
                for i, tile in enumerate(num_required_tiles):
                    tile.number = num_sample[i]
            else:
                # Smart Number Placement (Adjacency & Gold Rule)
                if not self.place_numbers(num_required_tiles, num_sample):
                    messagebox.showwarning("Warning", f"Could not satisfy 6/8 rules for Island {island_id} perfectly. Placing randomly.")
                    # Fallback to random
                    random.shuffle(num_sample)
                    for i, tile in enumerate(num_required_tiles):
                        tile.number = num_sample[i]
                    
        return True

    def place_numbers(self, tiles, number_pool):
        # red = 6 or 8
        reds = [n for n in number_pool if n in [6, 8]]
        others = [n for n in number_pool if n not in [6, 8]]
        
        for attempt in range(200):
            # Reset
            for t in tiles: t.number = None
            random.shuffle(tiles)
            
            success = True
            # Place Reds first
            current_reds = list(reds)
            random.shuffle(current_reds)
            
            for val in current_reds:
                # Find a valid tile for this red
                found_spot = False
                # Try tiles that aren't gold and don't have red neighbors
                eligible_tiles = [t for t in tiles if t.number is None and t.resource != "Gold"]
                random.shuffle(eligible_tiles)
                
                for t in eligible_tiles:
                    # Check neighbors
                    neighbor_is_red = False
                    for dq, dr in [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]:
                        neighbor_coord = (t.q + dq, t.r + dr)
                        if neighbor_coord in self.tiles:
                            if self.tiles[neighbor_coord].number in [6, 8]:
                                neighbor_is_red = True
                                break
                    
                    if not neighbor_is_red:
                        t.number = val
                        found_spot = True
                        break
                
                if not found_spot:
                    success = False
                    break
            
            if success:
                # Place others
                random.shuffle(others)
                idx = 0
                for t in tiles:
                    if t.number is None:
                        t.number = others[idx]
                        idx += 1
                return True
        return False

    def refresh_canvas(self):
        self.canvas.delete("all")
        self.draw_grid_base()
        
        for coord, tile in self.tiles.items():
            x, y = hex_to_pixel(tile.q, tile.r, HEX_RADIUS)
            cx, cy = x + self.offset_x, y + self.offset_y
            
            # Determine color and labels
            if self.mode == "EDITOR":
                color = COLORS.get("Unknown")
                text = f"I{tile.island_id}"
                num_text = ""
                # Draw small indicator of what island it belongs to
                self.draw_hexagon(cx, cy, color, text, num_text, tile.island_id)
            else: # PLAY mode
                if tile.revealed:
                    color = COLORS.get(tile.resource, COLORS["Unknown"])
                    text = tile.resource
                    num_text = str(tile.number) if tile.number else ""
                    self.draw_hexagon(cx, cy, color, text, num_text)
                else:
                    color = COLORS["Fog"]
                    text = "?"
                    num_text = ""
                    self.draw_hexagon(cx, cy, color, text, num_text)

    def draw_hexagon(self, x, y, color, label="", sub_label="", island_id=None, is_background=False):
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30 # Pointy top
            angle_rad = math.pi / 180 * angle_deg
            points.extend([x + HEX_RADIUS * math.cos(angle_rad),
                           y + HEX_RADIUS * math.sin(angle_rad)])
        
        if is_background:
            self.canvas.create_polygon(points, fill="#EBF5FB", outline="#AED6F1", width=1)
            return

        outline = "black"
        width = 1
        if island_id:
            # Highlight border based on island ID
            border_colors = {
                1: "#FF0000", 2: "#0000FF", 3: "#008000", 
                4: "#E67E22", 5: "#8E44AD", 6: "#1ABC9C",
                7: "#2C3E50", 8: "#D35400", 9: "#7F8C8D",
                10: "#C0392B", 11: "#27AE60", 12: "#2980B9"
            }
            outline = border_colors.get(island_id, "black")
            width = 3
            
        self.canvas.create_polygon(points, fill=color, outline=outline, width=width)
        
        if label == "?":
            # Fog representation
            self.canvas.create_text(x, y, text=RESOURCE_ICONS["Fog"], font=("Arial", 24))
        elif label:
            icon = RESOURCE_ICONS.get(label)
            if icon:
                # Draw Icon
                icon_y = y - 10 if sub_label else y
                self.canvas.create_text(x, icon_y, text=icon, font=("Arial", 22))
                
                # In Editor mode or for Sea/Desert, the resource name might be useful if no icon or alongside it
                if self.mode == "EDITOR" or label in ["Sea", "Desert"]:
                    # Small text for resource name if it's Sea/Desert or we're in editor
                    text_y = y + 15 if label in ["Sea", "Desert"] else y + 5
                    # ... but in Editor we show island ID instead
                    if self.mode == "EDITOR":
                        self.canvas.create_text(x, y + 15, text=label, font=("Arial", 7), fill="black")
            else:
                # Fallback for island ID labels in Editor
                self.canvas.create_text(x, y, text=label, font=("Arial", 10, "bold"))

        if sub_label:
            # Catan-style number tokens
            r = 12
            self.canvas.create_oval(x-r, y+18-r, x+r, y+18+r, fill="white", outline="black")
            fill = "red" if sub_label in ["6", "8"] else "black"
            self.canvas.create_text(x, y+18, text=sub_label, font=("Arial", 9, "bold"), fill=fill)

    def draw_grid_base(self):
        # Draw a background grid of ocean tiles to show spacing
        # Covers a wide area (approx 25x20 hexes)
        for q in range(-15, 16):
            for r in range(-15, 16):
                if abs(q + r) > 20: continue
                
                # Skip if a real tile is already there
                if (q, r) in self.tiles:
                    continue
                
                x, y = hex_to_pixel(q, r, HEX_RADIUS)
                cx, cy = x + self.offset_x, y + self.offset_y
                
                # Only draw if roughly within canvas bounds to save performance
                if -HEX_RADIUS < cx < 1000 and -HEX_RADIUS < cy < 800:
                    self.draw_hexagon(cx, cy, "", is_background=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = CatanGenerator(root)
    root.geometry("1100x700")
    root.mainloop()
