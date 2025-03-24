import os
import json
from datetime import datetime, timedelta

class Server:
    """Class representing a server (computer) in the system"""
    
    def __init__(self, id="", name="", status="available", customer_name="", 
                 customer_phone="", start_time="", usage_time=0, price_per_hour=10000):
        """Initialize a Server object"""
        self.id = id
        self.name = name
        self.status = status
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.start_time = start_time
        self.usage_time = usage_time
        self.price_per_hour = price_per_hour
    
    @classmethod
    def from_dict(cls, data):
        """Create Server object from dictionary"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            status=data.get('status', 'available'),
            customer_name=data.get('customer_name', ''),
            customer_phone=data.get('customer_phone', ''),
            start_time=data.get('start_time', ''),
            usage_time=data.get('usage_time', 0),
            price_per_hour=data.get('price_per_hour', 10000)
        )
    
    def to_dict(self):
        """Convert Server object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'start_time': self.start_time,
            'usage_time': self.usage_time,
            'price_per_hour': self.price_per_hour
        }
    
    def is_available(self):
        """Check if the server is ready for use"""
        return self.status == 'available'
    
    def assign_customer(self, customer_name, customer_phone, usage_time):
        """Assign client to server"""
        if not self.is_available():
            raise ValueError(f"Server {self.id} has been used")
        
        self.status = 'occupied'
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.usage_time = usage_time
        
        # Take current time as start time
        current_time = datetime.now()
        self.start_time = current_time.strftime('%H:%M')
        
        return True
    
    def free_server(self):
        """Free up server after use"""
        self.status = 'available'
        self.customer_name = ''
        self.customer_phone = ''
        self.start_time = ''
        self.usage_time = 0
    
    def calculate_price(self):
        """Calculate price based on time of use"""
        return self.usage_time * self.price_per_hour
    
    def get_end_time(self):
        """Calculate end time based on start time and usage time"""
        if not self.start_time:
            return ""
        
        # Convert start time from string to datetime object
        start_hour, start_minute = map(int, self.start_time.split(':'))
        start_datetime = datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        
        # Calculate end time
        end_datetime = start_datetime + timedelta(hours=self.usage_time)
        
        return end_datetime.strftime('%H:%M')
    
    def __str__(self):
        """Convert Server object to string for display"""
        status_str = "Sẵn sàng" if self.is_available() else "In use"
        return f"Server {self.id} ({self.name}): {status_str}"

class ServerManager:
    """Class to manage servers in the system"""
    
    def __init__(self, file_path='servers.json'):
        """Object initialization ServerManager"""
        self.file_path = file_path
        self.servers = []
        self.load_servers()
    
    def load_servers(self):
        """Read server data from file JSON"""
        try:
            if not os.path.exists(self.file_path):
                print(f"File {self.file_path} does not exist!")
                return
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                server_data = json.load(f)
            
            self.servers = [Server.from_dict(data) for data in server_data]
            print(f"Read {len(self.servers)} servers from file {self.file_path}")
        except Exception as e:
            print(f"Error reading server file: {e}")
    
    def save_servers(self):
        """Save server data to JSON file"""
        try:
            server_data = [server.to_dict() for server in self.servers]
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(server_data, f, ensure_ascii=False, indent=4)
            
            print(f"Saved {len(self.servers)} servers to file {self.file_path}")
        except Exception as e:
            print(f"Error saving server file: {e}")
    
    def get_server_by_id(self, server_id):
        """Get Server object by ID"""
        for server in self.servers:
            if server.id == server_id:
                return server
        return None
    
    def get_available_servers(self):
        """Get a list of available servers"""
        return [server for server in self.servers if server.is_available()]
    
    def get_occupied_servers(self):
        """Get a list of servers currently in use"""
        return [server for server in self.servers if not server.is_available()]
    
    def assign_customer_to_server(self, server_id, customer_name, customer_phone, usage_time):
        """Assign clients to server by ID"""
        server = self.get_server_by_id(server_id)
        if not server:
            raise ValueError(f"Server with ID {server_id} not found")
        
        result = server.assign_customer(customer_name, customer_phone, usage_time)
        if result:
            self.save_servers()
        return result
    
    def free_server_by_id(self, server_id):
        """Release server by ID"""
        server = self.get_server_by_id(server_id)
        if not server:
            raise ValueError(f"Server with ID {server_id} not found ")
        
        server.free_server()
        self.save_servers()
        return True
    
    def get_all_servers(self):
        """Get list of all servers"""
        return self.servers 