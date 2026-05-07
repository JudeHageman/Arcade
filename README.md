# Resonance
This is an arcade where players can login, play different games, chat through a unique chat per game, and compete on leaderboards. Are arcade is unique in that all players belong to one of three teams. In supported games, the player's avatar matches the color of their team and they earn team score through some mechanic in the game. Teams can then compete on who has the most cumulative team score across the games in the leaderboards.

## How to setup
Clone the repository:
```
git clone https://github.com/JudeHageman/Arcade.git
```

WebSockets may have to be installed, in which case run:
```
pip install websockets
```

Launch the Python client: 
```
python3 .\py_client\client.py
```

Open another terminal and launch the Python server:
```
python3 .\py_client\client.py
```

Open an additional terminal and launch a C++ game server:
```
cd ./cpp_server/ && ./server_text --port 8080
```