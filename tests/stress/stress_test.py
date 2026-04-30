import asyncio
import websockets
import json
import time
import random

# Configuration
SERVER_URI = "ws://127.0.0.1:8000"
NUM_BOTS = 10  # Adjust this to scale the stress
REQUESTS_PER_BOT = 10
SEARCH_PREFIXES = ["a", "b", "josh", "player", "test"]

async def simulate_bot(bot_id):
    username = f"bot_{bot_id}"
    password = "password123"
    
    try:
        async with websockets.connect(SERVER_URI) as websocket:
            # 1. Stress the Login (Auth & HashTable)
            login_payload = {
                "action": "login",
                "username": username,
                "password": password
            }
            await websocket.send(json.dumps(login_payload))
            
            # Wait for response (Login or Team Selection)
            response = await websocket.recv()
            resp_data = json.loads(response)

            # If it's a new account, handle team selection
            if resp_data.get("type") == "select_team":
                await websocket.send(json.dumps({"action": "select_team", "team": "Bots"}))
                await websocket.recv()

            # 2. Stress the Player Search (PrefixTrie & ArrayList)
            for i in range(REQUESTS_PER_BOT):
                prefix = random.choice(SEARCH_PREFIXES)
                search_payload = {
                    "action": "query",
                    "query": "player_search",
                    "prefix": prefix
                }
                
                start_time = time.perf_counter()
                await websocket.send(json.dumps(search_payload))
                
                # Wait for results with timeout
                try:
                    result = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    end_time = time.perf_counter()
                    print(f"Bot {bot_id} search '{prefix}' got response in {end_time - start_time:.4f}s")
                except asyncio.TimeoutError:
                    print(f"Bot {bot_id} search '{prefix}' TIMED OUT after {time.perf_counter() - start_time:.4f}s")
                    break
                
                await asyncio.sleep(random.uniform(0.1, 0.5)) # Simulate thinking time

    except Exception as e:
        print(f"Bot {bot_id} encountered an error: {e}")

async def run_stress_test():
    print(f"Starting stress test with {NUM_BOTS} simultaneous bots...")
    start_total = time.perf_counter()
    
    # Create a list of bot tasks
    tasks = [simulate_bot(i) for i in range(NUM_BOTS)]
    
    # Run all bots concurrently
    await asyncio.gather(*tasks)
    
    end_total = time.perf_counter()
    print(f"--- Test Complete ---")
    print(f"Total Time: {end_total - start_total:.2f} seconds")
    print(f"Average throughput: { (NUM_BOTS * REQUESTS_PER_BOT) / (end_total - start_total):.2f} searches/sec")

if __name__ == "__main__":
    asyncio.run(run_stress_test())