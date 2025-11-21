import random
import time
import sys

# --- Configuration ---
NUM_ROUNDS = 5
AGENTS_CONFIG = [
    {"name": "Agent Red", "strategy": "Aggressive", "risk_factor": 0.9, "color": "\033[91m"},
    {"name": "Agent Green", "strategy": "Balanced", "risk_factor": 0.7, "color": "\033[92m"},
    {"name": "Agent Blue", "strategy": "Conservative", "risk_factor": 0.5, "color": "\033[94m"},
    {"name": "Agent Yellow", "strategy": "Random", "risk_factor": 0.0, "color": "\033[93m"},
]
RESET_COLOR = "\033[0m"

class Agent:
    def __init__(self, id, name, strategy, risk_factor, color):
        self.id = id
        self.name = name
        self.strategy = strategy
        self.risk_factor = risk_factor
        self.color = color
        self.balance = 0
        self.wins = 0

    def evaluate_and_bid(self, true_task_value):
        # 1. Estimate Value: Agents don't know the true value perfectly.
        # Error margin is between -10% and +10%
        estimation_error = random.uniform(0.9, 1.1)
        estimated_value = true_task_value * estimation_error

        # 2. Determine Profit Margin based on strategy
        if self.strategy == "Random":
            margin = random.uniform(0.1, 0.5)
        else:
            # Higher risk factor = smaller margin (bidding higher to win)
            # Lower risk factor = larger margin (bidding lower to stay safe)
            margin = 0.4 - (self.risk_factor * 0.3)

        # 3. Calculate Bid
        my_bid = int(estimated_value * (1 - margin))
        
        # Log the internal thought process (simulation)
        return max(1, my_bid), estimated_value

def run_auction():
    print(f"{'-'*60}")
    print(f"STARTING MULTI-AGENT AUCTION SYSTEM")
    print(f"{'-'*60}\n")
    
    agents = [Agent(i, c["name"], c["strategy"], c["risk_factor"], c["color"]) 
              for i, c in enumerate(AGENTS_CONFIG)]

    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"--- ROUND {round_num} ---")
        
        # 1. Generate Task
        true_value = random.randint(100, 500)
        print(f"New Task Available! True Value (Unknown to agents): ${true_value}")
        print("Agents are processing messages...\n")
        time.sleep(1)

        # 2. Collect Bids
        bids = []
        print(f"{'Agent':<15} | {'Strategy':<12} | {'Bid':<10} | {'Msg'}")
        print("-" * 60)

        for agent in agents:
            bid_amount, estimated = agent.evaluate_and_bid(true_value)
            bids.append((bid_amount, agent))
            
            # Print bid arrival
            print(f"{agent.color}{agent.name:<15}{RESET_COLOR} | {agent.strategy:<12} | ${bid_amount:<9} | (Est: ${int(estimated)})")
            time.sleep(0.5) # Simulate network delay

        # 3. Determine Winner (Highest Bid)
        bids.sort(key=lambda x: x[0], reverse=True)
        winning_bid, winner = bids[0]

        # 4. Execute Transaction
        print("-" * 60)
        
        # Winner pays the bid, receives the True Value
        profit = true_value - winning_bid
        winner.balance += profit
        winner.wins += 1

        # 5. Output Result
        print(f"\n🏆 WINNER: {winner.color}{winner.name}{RESET_COLOR}")
        print(f"   Bid Amount: ${winning_bid}")
        print(f"   True Value: ${true_value}")
        
        if profit >= 0:
            print(f"   Outcome:    \033[92m+${profit} Profit\033[0m")
        else:
            print(f"   Outcome:    \033[91m-${abs(profit)} LOSS (Overpaid!)\033[0m")
        
        print("\n" + "="*60 + "\n")
        time.sleep(2)

    # --- Final Stats ---
    print("FINAL STANDINGS")
    print(f"{'Agent':<15} | {'Wins':<5} | {'Total Balance'}")
    print("-" * 40)
    agents.sort(key=lambda x: x.balance, reverse=True)
    for agent in agents:
        print(f"{agent.color}{agent.name:<15}{RESET_COLOR} | {agent.wins:<5} | ${agent.balance}")

if __name__ == "__main__":
    run_auction()
