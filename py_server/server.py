# used for async process management and the WebSocket server
import asyncio

# used to connect to the Python server
import websockets

# used for the TCP socket check to see if C++ server is up
import socket

async def handle_client(client):
    """Handle client connections"""
    print(f"Client connected: {client.remote_address}")

    # try/except to handle client disconnections
    try:
        # listen for messages from the client
        async for msg in client:
            print(f"Received: {msg}")
            
            if msg == "check_cpp":
                # C++ server doesn't use WebSocket, so use a regular TCP socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', 8080))
                sock.close()
                
                print(f"C++ connection result: {result}")
                if result == 0:
                    print("C++ server is responding")
                    await client.send("ready")
                else:
                    print("C++ server not responding")
                    await client.send("not_ready")
            else:
                # echo any messages
                await client.send(f"Echo: {msg}")
                
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {client.remote_address}")

async def run_server():
    """Start the Python server"""
    server = await websockets.serve(handle_client, "127.0.0.1", 8000)
    print("Python server running on ws://127.0.0.1:8000")
    print("Press Ctrl+C to stop.")
    
    # keep the server running indefinitely (until KeyboardInterrupt in main)
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nServer stopped.")
