import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random

# --- Constants ---
GRID_SIZE = 20
DIRT_DENSITY = 0.2 # Reduced density to ensure completion in 200 steps
EMPTY = 0
DIRT = 1
AGENT_A_COLOR = 'red'
AGENT_B_COLOR = 'blue'
DIRT_COLOR = '#e6ccb3' # Light brown
CLEAN_COLOR = 'white'

class CleaningAgent:
    def __init__(self, agent_id, color, start_pos):
        self.agent_id = agent_id
        self.color = color
        self.pos = list(start_pos)  # [row, col]
        self.zone = None  # Will be defined during negotiation
        self.moves_made = 0
        self.cleaned_count = 0

    def negotiate_zone(self, total_cols, role):
        """
        Simple negotiation logic:
        Agents split the room vertically based on their ID to avoid overlap.
        """
        split_line = total_cols // 2
        
        if role == "LEFT":
            # Agent takes columns 0 to split_line-1
            self.zone = (0, split_line) 
            print(f"[Agent {self.agent_id}] Requesting LEFT Sector (Cols 0-{split_line}).")
        else:
            # Agent takes columns split_line to total_cols-1
            self.zone = (split_line, total_cols)
            print(f"[Agent {self.agent_id}] Requesting RIGHT Sector (Cols {split_line}-{total_cols}).")
            
        return True # Agreement reached

    def get_valid_moves(self):
        """Returns all valid adjacent coordinates within the negotiated zone."""
        r, c = self.pos
        candidates = [
            (r - 1, c), (r + 1, c), 
            (r, c - 1), (r, c + 1)
        ]
        valid = []
        min_col, max_col = self.zone
        
        for nr, nc in candidates:
            # Check Grid Boundaries
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                # Check Negotiated Zone Boundaries (Crucial for conflict avoidance)
                if min_col <= nc < max_col:
                    valid.append((nr, nc))
        return valid

    def find_nearest_dirt(self, grid):
        """Global Sensor: Finds nearest dirt in the assigned zone."""
        r, c = self.pos
        min_dist = float('inf')
        target = None
        min_col, max_col = self.zone

        # Scan only the assigned zone
        for row in range(GRID_SIZE):
            for col in range(min_col, max_col):
                if grid[row, col] == DIRT:
                    # Manhattan distance
                    dist = abs(row - r) + abs(col - c)
                    if dist < min_dist:
                        min_dist = dist
                        target = (row, col)
        return target

    def step(self, grid):
        """
        AI Logic: 
        1. Clean if on dirt.
        2. Look for adjacent dirt.
        3. If no adjacent dirt, look for NEAREST dirt in zone (Global sensing).
        """
        # 1. Clean current spot if dirty
        if grid[self.pos[0], self.pos[1]] == DIRT:
            grid[self.pos[0], self.pos[1]] = EMPTY
            self.cleaned_count += 1
            return # Spend turn cleaning

        valid_moves = self.get_valid_moves()
        if not valid_moves: 
            return # Stuck

        target_move = None
        
        # 2. Check immediate neighbors for dirt
        random.shuffle(valid_moves)
        for mr, mc in valid_moves:
            if grid[mr, mc] == DIRT:
                target_move = (mr, mc)
                break
        
        # 3. If no neighbor has dirt, find nearest dirt in entire zone and move towards it
        if not target_move:
            global_target = self.find_nearest_dirt(grid)
            if global_target:
                # Find move that minimizes distance to global target
                tr, tc = global_target
                best_dist = float('inf')
                for mr, mc in valid_moves:
                    dist = abs(mr - tr) + abs(mc - tc)
                    if dist < best_dist:
                        best_dist = dist
                        target_move = (mr, mc)
            else:
                # Zone is clean, random walk
                target_move = random.choice(valid_moves)

        # Execute move
        self.pos = list(target_move)
        self.moves_made += 1

# --- Simulation Setup ---

# Initialize Grid
grid = np.random.choice([EMPTY, DIRT], size=(GRID_SIZE, GRID_SIZE), p=[1-DIRT_DENSITY, DIRT_DENSITY])

# Initialize Agents
agent1 = CleaningAgent(1, AGENT_A_COLOR, [0, 0])
agent2 = CleaningAgent(2, AGENT_B_COLOR, [0, GRID_SIZE-1])

print("--- STARTING NEGOTIATION PHASE ---")
# Agents agree on zones to avoid collision/overlap
agent1.negotiate_zone(GRID_SIZE, "LEFT")
agent2.negotiate_zone(GRID_SIZE, "RIGHT")
print("--- NEGOTIATION COMPLETE: ZONES LOCKED ---")

# --- Visualization Setup ---

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_title("Multi-Agent Cleaning Simulation (Negotiated Zones)")

# Create a custom colormap for the grid (Clean vs Dirt)
cmap = plt.matplotlib.colors.ListedColormap([CLEAN_COLOR, DIRT_COLOR])

# Initial Plot
img = ax.imshow(grid, cmap=cmap, vmin=0, vmax=1)

# Agent Scatter Plots (Dots)
scat1 = ax.scatter(agent1.pos[1], agent1.pos[0], c=agent1.color, s=200, label='Agent A (Left Zone)', edgecolors='black')
scat2 = ax.scatter(agent2.pos[1], agent2.pos[0], c=agent2.color, s=200, label='Agent B (Right Zone)', edgecolors='black')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=2)

# Grid lines for visual clarity
ax.set_xticks(np.arange(-.5, GRID_SIZE, 1), minor=True)
ax.set_yticks(np.arange(-.5, GRID_SIZE, 1), minor=True)
ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
ax.tick_params(which='minor', size=0)
ax.set_xticks([]) # Hide major ticks
ax.set_yticks([])

# Draw the negotiated boundary line
ax.axvline(x=GRID_SIZE//2 - 0.5, color='black', linestyle='--', linewidth=2, label='Negotiated Boundary')

def update(frame):
    # 1. Update Agents Logic
    agent1.step(grid)
    agent2.step(grid)

    # 2. Update Visuals
    img.set_data(grid)
    
    # Update Agent positions
    scat1.set_offsets([agent1.pos[1], agent1.pos[0]])
    scat2.set_offsets([agent2.pos[1], agent2.pos[0]])

    # Check completion
    remaining_dirt = np.sum(grid)
    total_cells = GRID_SIZE * GRID_SIZE
    percent_clean = ((total_cells * DIRT_DENSITY - remaining_dirt) / (total_cells * DIRT_DENSITY)) * 100
    
    ax.set_title(f"Simulation Step: {frame} | Dirt Remaining: {remaining_dirt} | Cleaned: {int(percent_clean)}%")
    
    if remaining_dirt == 0:
        print(f"Cleaning Complete in {frame} steps!")
        ani.event_source.stop()

# Create Animation
# Reduced frames to 200 as requested
ani = FuncAnimation(fig, update, frames=200, interval=200, repeat=False)

plt.show()
