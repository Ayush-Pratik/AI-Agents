import pygame
import random
import math

# --- Configuration ---
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
FPS = 60 
ANIMATION_SPEED = 2

# Colors
COLORS = [
    (255, 80, 80),   # Red
    (80, 255, 80),   # Green
    (80, 80, 255),   # Blue
    (255, 255, 80)   # Yellow
]

# --- Classes ---

class Task:
    def __init__(self):
        self.x = random.randint(200, WIDTH - 200)
        self.y = random.randint(200, HEIGHT - 200)
        self.true_value = random.randint(50, 150) 
        self.work_needed = 100
        self.radius = 15
        self.color = (200, 200, 200)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255,255,255), (self.x, self.y), self.radius, 2)

class Agent:
    def __init__(self, id, start_x, start_y, color):
        self.id = id
        self.x = start_x
        self.y = start_y
        self.start_pos = (start_x, start_y)
        self.color = color
        self.radius = 20
        
        self.balance = 0
        
        # Personality Traits
        self.valuation_skill = random.uniform(0.85, 1.15) 
        self.greed = random.uniform(0.1, 0.3) 
        
        # New Trait: Aggressiveness (Probability to enter an auction)
        # 0.3 means they only bid 30% of the time, 0.9 means 90%
        self.aggressiveness = random.uniform(0.3, 0.8)

        self.state = "IDLE" 
        self.current_bid = 0
        self.work_progress = 0
        self.last_action_text = "Ready"

    def calculate_bid(self, task_value):
        estimated_value = task_value * self.valuation_skill
        max_bid = estimated_value * (1 - self.greed)
        self.current_bid = int(max(1, max_bid))
        return self.current_bid

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > ANIMATION_SPEED:
            self.x += (dx / dist) * ANIMATION_SPEED
            self.y += (dy / dist) * ANIMATION_SPEED
            return False
        else:
            self.x = target_x
            self.y = target_y
            return True

    def update(self, task):
        if self.state == "MOVING_TO_TASK":
            self.last_action_text = "Winning! Moving..."
            if self.move_towards(task.x, task.y):
                self.state = "WORKING"
        
        elif self.state == "WORKING":
            self.work_progress += 1
            self.last_action_text = f"Working {self.work_progress}%"
            if self.work_progress >= task.work_needed:
                profit = task.true_value - self.current_bid
                self.balance += profit
                self.state = "RETURNING"
                self.work_progress = 0
                return True 

        elif self.state == "RETURNING":
            self.last_action_text = "Task Done. Returning."
            if self.move_towards(self.start_pos[0], self.start_pos[1]):
                self.state = "IDLE"
                self.last_action_text = "Idle"
        
        return False

    def draw(self, screen, font):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        text = font.render(f"A{self.id}", True, (0,0,0))
        screen.blit(text, (self.x - 5, self.y - 8))
        status = font.render(self.last_action_text, True, TEXT_COLOR)
        screen.blit(status, (self.x - 20, self.y - 40))

        if self.state == "WORKING":
            pygame.draw.rect(screen, (255, 255, 255), (self.x - 15, self.y + 25, 30, 5))
            pygame.draw.rect(screen, (0, 255, 0), (self.x - 15, self.y + 25, 30 * (self.work_progress/100), 5))

# --- Main System ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Multi-Agent Auction (Reduced Bids)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    header_font = pygame.font.SysFont("Arial", 24, bold=True)

    agents = [
        Agent(1, 50, 50, COLORS[0]),
        Agent(2, WIDTH-50, 50, COLORS[1]),
        Agent(3, 50, HEIGHT-50, COLORS[2]),
        Agent(4, WIDTH-50, HEIGHT-50, COLORS[3])
    ]

    current_task = None
    task_delay_timer = 0
    auction_log = "System: Waiting for task..."

    running = True
    while running:
        screen.fill(BG_COLOR)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if current_task is None:
            task_delay_timer += 1
            if task_delay_timer > 60:
                current_task = Task()
                auction_log = f"NEW TASK! Value: ${current_task.true_value}"
                
                # --- AUCTION LOGIC ---
                bids = []
                bid_participants = 0
                
                for agent in agents:
                    if agent.state == "IDLE":
                        # DECISION: Should I bid? (Simulate interest/availability)
                        # Agent only bids if random chance is lower than their aggressiveness trait
                        if random.random() < agent.aggressiveness:
                            bid = agent.calculate_bid(current_task.true_value)
                            bids.append((bid, agent))
                            bid_participants += 1
                        else:
                            # Optional: Visual feedback that they passed
                            agent.last_action_text = "Passed (No Bid)"
                
                if bids:
                    bids.sort(key=lambda x: x[0], reverse=True)
                    winning_bid, winner = bids[0]
                    auction_log = f"WINNER: A{winner.id} (${winning_bid}) | Total Bids: {bid_participants}"
                    winner.state = "MOVING_TO_TASK"
                else:
                    auction_log = "No bids placed. Task skipped."
                    current_task = None 
                    task_delay_timer = 0

        task_completed = False
        for agent in agents:
            if current_task and agent.state != "IDLE" and agent.state != "RETURNING":
                if agent.update(current_task):
                    task_completed = True
            else:
                agent.update(None)

        if task_completed:
            current_task = None
            task_delay_timer = 0

        # Drawing
        if current_task:
            current_task.draw(screen)
            for agent in agents:
                if agent.state == "MOVING_TO_TASK" or agent.state == "WORKING":
                    pygame.draw.line(screen, agent.color, (agent.x, agent.y), (current_task.x, current_task.y), 2)

        for agent in agents:
            agent.draw(screen, font)

        # UI
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, 250, HEIGHT))
        pygame.draw.line(screen, (255, 255, 255), (250, 0), (250, HEIGHT), 2)
        title = header_font.render("Agent Stats", True, (255, 215, 0))
        screen.blit(title, (20, 20))

        y_offset = 60
        for agent in agents:
            name_text = font.render(f"Agent {agent.id} Bal: ${agent.balance}", True, agent.color)
            screen.blit(name_text, (20, y_offset))
            aggro_text = font.render(f"Bid Rate: {int(agent.aggressiveness*100)}%", True, (150, 150, 150))
            screen.blit(aggro_text, (20, y_offset + 20))
            
            if agent.state == "IDLE":
                state_text = agent.last_action_text
            elif agent.state == "MOVING_TO_TASK":
                state_text = f"Won bid: ${agent.current_bid}"
            else:
                state_text = agent.state
            
            sub_text = font.render(state_text, True, (200, 200, 200))
            screen.blit(sub_text, (20, y_offset + 40))
            y_offset += 85

        log_title = header_font.render("Auction Feed", True, (255, 215, 0))
        screen.blit(log_title, (20, HEIGHT - 100))
        log_msg = font.render(auction_log, True, (255, 255, 255))
        screen.blit(log_msg, (20, HEIGHT - 70))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
