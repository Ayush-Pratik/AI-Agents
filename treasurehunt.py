import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import matplotlib.patches as patches

# --- Configuration ---
MAZE_SIZE = 15
ANIMATION_INTERVAL = 400  # Milliseconds (Slower speed)
MAX_STEPS = 300

# Colors (Hex codes)
COLOR_WALL = '#2C3E50'        # Dark Slate Blue
COLOR_PATH = '#ECF0F1'        # Clouds White
COLOR_AGENT_1 = '#E74C3C'     # Alizarin Red
COLOR_AGENT_2 = '#3498DB'     # Peter River Blue
COLOR_TRAIL_1 = '#F1948A'     # Light Red
COLOR_TRAIL_2 = '#85C1E9'     # Light Blue
COLOR_TREASURE = '#F1C40F'    # Sunflower Yellow
COLOR_OVERLAP = '#9B59B6'     # Purple (where trails meet)

# Map Constants
EMPTY = 0
WALL = 1
TREASURE = 9

# 1. Setup the Maze (15x15)
# 1 = Wall, 0 = Path, 9 = Treasure
grid_layout = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 9, 0, 0, 0, 0, 1, 0, 1], # Treasure at (7, 7)
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]
maze = np.array(grid_layout)

# Start Positions
START_1 = (1, 1)    # Top Left
START_2 = (13, 13)  # Bottom Right

# --- Agent Logic ---
class SearchAgent:
    def __init__(self, name, start_pos, color):
        self.name = name
        self.color = color
        self.pos = start_pos
        self.queue = deque([start_pos])
        self.visited = {start_pos}
        self.finished = False
        self.found_treasure = False

    def move(self, maze_grid, partner_visited):
        if not self.queue or self.finished:
            self.finished = True
            return

        current = self.queue.popleft()
        self.pos = current
        r, c = current

        if maze_grid[r, c] == TREASURE:
            self.found_treasure = True
            self.finished = True
            return

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        np.random.shuffle(directions)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < MAZE_SIZE and 0 <= nc < MAZE_SIZE:
                if maze_grid[nr, nc] != WALL:
                    if (nr, nc) not in self.visited and (nr, nc) not in partner_visited:
                        self.visited.add((nr, nc))
                        self.queue.append((nr, nc))

# --- Simulation Execution ---
agent1 = SearchAgent("Agent Red", START_1, COLOR_AGENT_1)
agent2 = SearchAgent("Agent Blue", START_2, COLOR_AGENT_2)

history = []

for _ in range(MAX_STEPS):
    state = {
        'p1': agent1.pos,
        'p2': agent2.pos,
        'v1': agent1.visited.copy(),
        'v2': agent2.visited.copy(),
        'status': "Searching..."
    }
    
    agent1.move(maze, agent2.visited)
    agent2.move(maze, agent1.visited)

    if agent1.found_treasure:
        # Create the "Victory" frame logic
        state['p1'] = agent1.pos # Ensure final pos is recorded
        state['status'] = "RED FOUND THE TREASURE!"
        # Append multiple times to pause animation on victory
        for _ in range(20): 
            history.append(state)
        break
    if agent2.found_treasure:
        state['p2'] = agent2.pos
        state['status'] = "BLUE FOUND THE TREASURE!"
        for _ in range(20):
            history.append(state)
        break
    
    history.append(state)

# --- Visualization Setup ---
fig, ax = plt.subplots(figsize=(8, 8))
fig.patch.set_facecolor('#FDFEFE')

def setup_plot():
    ax.clear()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Collaborative Multi-Agent Search", fontsize=14, fontweight='bold')
    
    grid_img = np.zeros((MAZE_SIZE, MAZE_SIZE, 3))
    for r in range(MAZE_SIZE):
        for c in range(MAZE_SIZE):
            if maze[r, c] == WALL:
                grid_img[r, c] = [int(x*255) for x in plt.matplotlib.colors.to_rgb(COLOR_WALL)]
            elif maze[r, c] == TREASURE:
                grid_img[r, c] = [int(x*255) for x in plt.matplotlib.colors.to_rgb(COLOR_TREASURE)]
            else:
                grid_img[r, c] = [int(x*255) for x in plt.matplotlib.colors.to_rgb(COLOR_PATH)]
    
    ax.imshow(grid_img.astype('uint8'))
    return ax

ax = setup_plot()
visited_layer = ax.imshow(np.zeros((MAZE_SIZE, MAZE_SIZE, 4)), zorder=1)

# Agents
dot1, = ax.plot([], [], 'o', color=COLOR_AGENT_1, markersize=15, markeredgecolor='white', label='Agent 1')
dot2, = ax.plot([], [], 'o', color=COLOR_AGENT_2, markersize=15, markeredgecolor='white', label='Agent 2')

# Winner Marker (Hidden initially)
winner_star, = ax.plot([], [], '*', color='gold', markersize=30, markeredgecolor='black', zorder=10, visible=False)

status_text = ax.text(0.5, -0.05, "", transform=ax.transAxes, ha="center", fontsize=12, fontweight='bold')

legend_elements = [
    patches.Patch(facecolor=COLOR_AGENT_1, label='Agent Red'),
    patches.Patch(facecolor=COLOR_AGENT_2, label='Agent Blue'),
    patches.Patch(facecolor=COLOR_TREASURE, label='Treasure'),
]
ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1.1))

def animate(frame_idx):
    data = history[frame_idx]
    
    # Update positions
    dot1.set_data([data['p1'][1]], [data['p1'][0]])
    dot2.set_data([data['p2'][1]], [data['p2'][0]])
    
    # Reset visual styles for normal search
    dot1.set_marker('o')
    dot2.set_marker('o')
    dot1.set_markersize(15)
    dot2.set_markersize(15)
    winner_star.set_visible(False)

    # VICTORY VISUALS
    if "RED FOUND" in data['status']:
        dot1.set_visible(False) # Hide dot, show star
        winner_star.set_data([data['p1'][1]], [data['p1'][0]])
        winner_star.set_color(COLOR_AGENT_1)
        winner_star.set_visible(True)
    elif "BLUE FOUND" in data['status']:
        dot2.set_visible(False)
        winner_star.set_data([data['p2'][1]], [data['p2'][0]])
        winner_star.set_color(COLOR_AGENT_2)
        winner_star.set_visible(True)
    else:
        dot1.set_visible(True)
        dot2.set_visible(True)

    # Update Trails
    overlay = np.zeros((MAZE_SIZE, MAZE_SIZE, 4))
    all_visited_1 = data['v1']
    all_visited_2 = data['v2']
    
    for r in range(MAZE_SIZE):
        for c in range(MAZE_SIZE):
            if maze[r, c] == WALL or maze[r, c] == TREASURE:
                continue
            is_v1 = (r, c) in all_visited_1
            is_v2 = (r, c) in all_visited_2
            
            if is_v1 and is_v2:
                overlay[r, c] = list(plt.matplotlib.colors.to_rgb(COLOR_OVERLAP)) + [0.5]
            elif is_v1:
                overlay[r, c] = list(plt.matplotlib.colors.to_rgb(COLOR_TRAIL_1)) + [0.6]
            elif is_v2:
                overlay[r, c] = list(plt.matplotlib.colors.to_rgb(COLOR_TRAIL_2)) + [0.6]
                
    visited_layer.set_data(overlay)
    status_text.set_text(data['status'])
    
    return dot1, dot2, visited_layer, status_text, winner_star

ani = FuncAnimation(fig, animate, frames=len(history), interval=ANIMATION_INTERVAL, blit=True, repeat=False)

plt.tight_layout()
plt.show()
