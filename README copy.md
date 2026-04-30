# Resonance

Resonance is an arcade platform where players log in, join a faction, launch games, and earn scores that feed into leaderboards and player profiles. The system is split into a Python WebSocket server, a Python desktop client, a C++ real-time game server, and several pygame-based games.

## What It Does

The project provides:

- account creation and login
- faction/team selection and team-colored gameplay
- live game status checks
- in-game and client-side chat
- game launch and session reporting
- profile, leaderboard, match history, player search, and game catalog tabs

## Main Flow

1. Server startup and state loading: the Python server starts, loads persisted data from the NDJSON files, and builds its in-memory data structures for accounts, chats, games, and connected clients.
2. Login and account creation: the client opens a WebSocket connection to the server, sends login requests, and new accounts are routed through faction selection before they can enter the main UI.
3. Live status and chat updates: the server checks each configured game server on a short interval, broadcasts connected-game status to authenticated clients, and keeps recent Python-side chat messages available in memory for the client UI.
4. Game launch and session reporting: the client launches a game as a subprocess, the game connects to the C++ multiplayer server, the client reads stdout lines that begin with `[USER]`, forwards those payloads back to the Python server, and the server appends score/session/chat data to the NDJSON files while refreshing memory-backed views.
5. Tab requests and data queries: the client requests data for the profile, leaderboard, match history, player search, and games catalog tabs, and the server refreshes the relevant modules before returning the response.
6. Game exit and UI restore: when a launched game closes, the client restores the launch button and clears the running-game state so the player can launch another game.

## How It Works

### Python Server

The server in [py_server/server.py](py_server/server.py) is the main coordination layer. It:

- accepts WebSocket connections from the desktop client
- authenticates users and creates new accounts
- keeps track of connected clients
- checks whether game servers are still reachable
- broadcasts global status updates every 2 seconds
- stores chat messages and game sessions in NDJSON-backed files
- refreshes the in-memory data layer before serving tab requests

### Python Client

The client in [py_client/client.py](py_client/client.py) is the user-facing desktop app. It:

- shows the login screen and main game/navigation screens
- keeps a persistent WebSocket connection open to the Python server
- launches games as separate processes
- reads game stdout and forwards user messages back to the server
- switches between profile, leaderboard, search, match history, and catalog tabs

### C++ Game Server

The C++ server in [cpp_server/src/server.cpp](cpp_server/src/server.cpp) handles real-time multiplayer game state. It uses pluggable serializers so player data can be encoded as text, JSON, or binary depending on the build configuration.

### Data Files

The runtime data is stored in [data/](data/):

- [accounts.ndjson](data/accounts.ndjson) for user accounts
- [chats.ndjson](data/chats.ndjson) for persisted chat messages
- [sessions.ndjson](data/sessions.ndjson) for completed game sessions
- [games.ndjson](data/games.ndjson) for the game catalog and metadata

### Custom Data Structures

The backend relies on custom implementations in [data_structures/](data_structures/) for fast lookup and ordered data handling. These include a hash table, linked list, dynamic array, prefix trie, BST, circular buffer, and priority queue.

## Game Structure

The playable games under [games/](games/) share a similar structure:

- [main.py](games/game_2/game/main.py) and [main.py](games/game_3/game/main.py) boot the game, set up the UI, and launch the level
- [settings.py](games/game_2/game/settings.py) and [settings.py](games/immortal_tree/game/settings.py) define resolution, tile size, server connection settings, and game-specific UI values
- modules such as `character.py`, `enemy.py`, `level.py`, `inventory.py`, and `network_client.py` control movement, enemies, gameplay, and network communication

## Tests

The [tests/](tests/) folder contains integration tests for login and leaderboard behavior, plus unit tests for the custom data structures and stress tests for server load.
