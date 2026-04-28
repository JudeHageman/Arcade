import socket
import threading
import json
import struct
from queue import Queue

class NetworkClient:
    def __init__(self, player_name, server_host='localhost', server_port=8080, serializer='text'):
        self.player_name = player_name
        self.server_host = server_host
        self.server_port = server_port
        self.serializer = serializer.lower()  # 'text', 'json', or 'binary'
        
        if self.serializer not in ['text', 'json', 'binary']:
            raise ValueError(f"Invalid serializer: {serializer}. Must be 'text', 'json', or 'binary'")
        
        self.sock = None
        self.connected = False
        self.my_player_id = None
        
        self.update_queue = Queue()
        self.receiver_thread = None
        self.running = False
        
        print(f"Network client using {self.serializer.upper()} serialization")
        
    def connect(self):
        """Connect to game server"""
        try:
            print(f"Connecting to {self.server_host}:{self.server_port}...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_host, self.server_port))
            self.connected = True
            self.running = True
            
            self.receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receiver_thread.start()
            
            print(f"Connected to server using {self.serializer.upper()} serialization!")
            return True
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.connected = False
            return False
    
    def _receive_loop(self):
        """Background thread to receive messages from server"""
        buffer = ""
        
        while self.running and self.connected:
            try:
                data = self.sock.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    print("Server disconnected")
                    self.connected = False
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self._process_message(line)
                    
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                    self.connected = False
                break
    
    def _process_message(self, msg):
        """Process a message from server"""
        # First check message type (before any separator)
        if msg.startswith("CONNECTED|"):
            parts = msg.split('|')
            self.my_player_id = int(parts[1])
            print(f"Assigned player ID: {self.my_player_id}")
            
        elif msg.startswith("STATE||"):
            # Game state update
            # Format: STATE||<serialized_player1>||<serialized_player2>||...
            # Players are separated by || (double pipe) to avoid conflicts with serialization formats
            parts = msg.split('||')
            print(f"[DEBUG] Received STATE message with {len(parts)-1} player entries")
            players = {}
            
            for i in range(1, len(parts)):
                if parts[i]:
                    print(f"[DEBUG] Parsing player {i}: '{parts[i][:50]}...'")  # First 50 chars
                    player_data = self._deserialize_player(parts[i])
                    if player_data:
                        print(f"[DEBUG] Parsed player: ID={player_data['id']}, Name={player_data['name']}")
                        players[player_data['id']] = player_data
                    else:
                        print(f"[DEBUG] Failed to parse player data")
            
            print(f"[DEBUG] Total players parsed: {len(players)}")
            self.update_queue.put(players)
    
    def _deserialize_player(self, data):
        """Deserialize player data based on format"""
        try:
            if self.serializer == 'text':
                return self._deserialize_text(data)
            elif self.serializer == 'json':
                return self._deserialize_json(data)
            elif self.serializer == 'binary':
                return self._deserialize_binary(data)
        except Exception as e:
            print(f"[ERROR] Deserialization error ({self.serializer} format): {e}")
            print(f"[ERROR] Data received: '{data[:100]}...'")
            print(f"[ERROR] This usually means server and client are using different serializers!")
            print(f"[ERROR] Server might be using a different format than '{self.serializer}'")
            return None
    
    def _deserialize_text(self, data):
        """Deserialize TEXT format: "id|name|x|y|socket|character_type|status|is_attacking|individual_score|team_score|team|tree_health" """
        parts = data.split('|')
        if len(parts) >= 5:
            try:
                result = {
                    'id': int(parts[0]),
                    'name': parts[1],
                    'x': float(parts[2]),
                    'y': float(parts[3])
                }
                # Add character_type and status if present
                if len(parts) >= 7:
                    result['character_type'] = parts[5]
                    result['status'] = parts[6]
                else:
                    result['character_type'] = ''
                    result['status'] = 'down'
                # Add is_attacking if present
                if len(parts) >= 8:
                    result['is_attacking'] = parts[7].lower() == 'true'
                else:
                    result['is_attacking'] = False
                # Add scores if present
                if len(parts) >= 10:
                    result['individual_score'] = int(parts[8])
                    result['team_score'] = int(parts[9])
                else:
                    result['individual_score'] = 0
                    result['team_score'] = 0
                # Add team if present
                if len(parts) >= 11:
                    result['team'] = parts[10].strip()
                else:
                    result['team'] = 'blue'
                # Add tree_health if present
                if len(parts) >= 12:
                    result['tree_health'] = float(parts[11].strip())
                else:
                    result['tree_health'] = -1
                # Add tree_regen_count if present
                if len(parts) >= 13:
                    result['tree_regen_count'] = int(parts[12].strip())
                else:
                    result['tree_regen_count'] = 0
                return result
            except (ValueError, IndexError) as e:
                print(f"Error parsing text data '{data}': {e}")
                return None
        return None
    
    def _deserialize_json(self, data):
        """Deserialize JSON format: {"id":1,"name":"Alice",...}"""
        player = json.loads(data)
        return {
            'id': player['id'],
            'name': player['name'],
            'x': player['x'],
            'y': player['y'],
            'character_type': player.get('character_type', ''),
            'status': player.get('status', 'down'),
            'is_attacking': player.get('is_attacking', False),
            'individual_score': player.get('individual_score', 0),
            'team_score': player.get('team_score', 0),
            'team': player.get('team', 'blue'),
            'tree_health': player.get('tree_health', -1),
            'tree_regen_count': player.get('tree_regen_count', 0)
        }
    
    def _deserialize_binary(self, data):
        """Deserialize BINARY format: base64-encoded 88-byte struct"""
        import base64
        
        try:
            # Decode base64 to get raw bytes
            raw_bytes = base64.b64decode(data)
            
            # Struct format: int(4) + char[32] + float(4) + float(4) + int(4) + char[16] + char[8] + padding(16) = 88 bytes
            if len(raw_bytes) < 88:
                return None
            
            # Unpack: i = int, 32s = 32-byte string, f = float, f = float, i = int, 16s = 16-byte string, 8s = 8-byte string, 16x = 16 bytes padding
            unpacked = struct.unpack('i32sff i16s8s16x', raw_bytes[:88])
            
            player_id = unpacked[0]
            name = unpacked[1].decode('utf-8').rstrip('\x00')  # Remove null terminator
            x = unpacked[2]
            y = unpacked[3]
            character_type = unpacked[5].decode('utf-8').rstrip('\x00')  # Remove null terminator
            status = unpacked[6].decode('utf-8').rstrip('\x00')  # Remove null terminator
            
            return {
                'id': player_id,
                'name': name,
                'x': x,
                'y': y,
                'character_type': character_type,
                'status': status
            }
        except Exception as e:
            print(f"Binary deserialization error: {e}")
            return None
    
    def send_update(self, x, y, character_type="", status="down", is_attacking=False, individual_score=0, team_score=0, team='blue', tree_health=-1, tree_regen_count=0):
        """Send position, status, scores, team, tree health, and regen count to server"""
        if self.connected and self.my_player_id is not None:
            attacking_str = "true" if is_attacking else "false"
            msg = f"UPDATE|{self.my_player_id}|{x}|{y}|{self.player_name}|{character_type}|{status}|{attacking_str}|{individual_score}|{team_score}|{team}|{tree_health}|{tree_regen_count}\n"
            try:
                self.sock.send(msg.encode('utf-8'))
            except:
                self.connected = False
    
    def get_updates(self):
        """Get most recent update from queue"""
        updates = []
        while not self.update_queue.empty():
            updates.append(self.update_queue.get())
        
        if updates:
            return updates[-1]
        return None
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        self.connected = False
        if self.sock:
            self.sock.close()