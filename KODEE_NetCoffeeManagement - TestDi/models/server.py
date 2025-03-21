import os
import json
from datetime import datetime, timedelta

class Server:
    """Lớp đại diện cho một server (máy tính) trong hệ thống"""
    
    def __init__(self, id="", name="", status="available", customer_name="", 
                 customer_phone="", start_time="", usage_time=0, price_per_hour=10000):
        """Khởi tạo một đối tượng Server"""
        self.id = id
        self.name = name
        self.status = status  # available hoặc occupied
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.start_time = start_time
        self.usage_time = usage_time  # Thời gian sử dụng (giờ)
        self.price_per_hour = price_per_hour  # Giá tiền mỗi giờ (VND)
    
    @classmethod
    def from_dict(cls, data):
        """Tạo đối tượng Server từ dictionary"""
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
        """Chuyển đổi đối tượng Server thành dictionary"""
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
        """Kiểm tra xem server có sẵn sàng để sử dụng không"""
        return self.status == 'available'
    
    def assign_customer(self, customer_name, customer_phone, usage_time):
        """Gán khách hàng cho server"""
        if not self.is_available():
            raise ValueError(f"Server {self.id} đã được sử dụng")
        
        self.status = 'occupied'
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.usage_time = usage_time
        
        # Lấy thời gian hiện tại làm thời gian bắt đầu
        current_time = datetime.now()
        self.start_time = current_time.strftime('%H:%M')
        
        return True
    
    def free_server(self):
        """Giải phóng server sau khi sử dụng"""
        self.status = 'available'
        self.customer_name = ''
        self.customer_phone = ''
        self.start_time = ''
        self.usage_time = 0
    
    def calculate_price(self):
        """Tính toán giá tiền dựa trên thời gian sử dụng"""
        return self.usage_time * self.price_per_hour
    
    def get_end_time(self):
        """Tính toán thời gian kết thúc dựa trên thời gian bắt đầu và thời gian sử dụng"""
        if not self.start_time:
            return ""
        
        # Chuyển đổi thời gian bắt đầu từ chuỗi sang đối tượng datetime
        start_hour, start_minute = map(int, self.start_time.split(':'))
        start_datetime = datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        
        # Tính thời gian kết thúc
        end_datetime = start_datetime + timedelta(hours=self.usage_time)
        
        return end_datetime.strftime('%H:%M')
    
    def __str__(self):
        """Chuyển đổi đối tượng Server thành chuỗi để hiển thị"""
        status_str = "Sẵn sàng" if self.is_available() else "Đang sử dụng"
        return f"Server {self.id} ({self.name}): {status_str}"

class ServerManager:
    """Lớp quản lý các server trong hệ thống"""
    
    def __init__(self, file_path='servers.json'):
        """Khởi tạo đối tượng ServerManager"""
        self.file_path = file_path
        self.servers = []
        self.load_servers()
    
    def load_servers(self):
        """Đọc dữ liệu server từ file JSON"""
        try:
            if not os.path.exists(self.file_path):
                print(f"File {self.file_path} không tồn tại!")
                return
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                server_data = json.load(f)
            
            self.servers = [Server.from_dict(data) for data in server_data]
            print(f"Đã đọc {len(self.servers)} server từ file {self.file_path}")
        except Exception as e:
            print(f"Lỗi khi đọc file server: {e}")
    
    def save_servers(self):
        """Lưu dữ liệu server vào file JSON"""
        try:
            server_data = [server.to_dict() for server in self.servers]
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(server_data, f, ensure_ascii=False, indent=4)
            
            print(f"Đã lưu {len(self.servers)} server vào file {self.file_path}")
        except Exception as e:
            print(f"Lỗi khi lưu file server: {e}")
    
    def get_server_by_id(self, server_id):
        """Lấy đối tượng Server theo ID"""
        for server in self.servers:
            if server.id == server_id:
                return server
        return None
    
    def get_available_servers(self):
        """Lấy danh sách các server có sẵn"""
        return [server for server in self.servers if server.is_available()]
    
    def get_occupied_servers(self):
        """Lấy danh sách các server đang được sử dụng"""
        return [server for server in self.servers if not server.is_available()]
    
    def assign_customer_to_server(self, server_id, customer_name, customer_phone, usage_time):
        """Gán khách hàng cho server theo ID"""
        server = self.get_server_by_id(server_id)
        if not server:
            raise ValueError(f"Không tìm thấy server với ID {server_id}")
        
        result = server.assign_customer(customer_name, customer_phone, usage_time)
        if result:
            self.save_servers()
        return result
    
    def free_server_by_id(self, server_id):
        """Giải phóng server theo ID"""
        server = self.get_server_by_id(server_id)
        if not server:
            raise ValueError(f"Không tìm thấy server với ID {server_id}")
        
        server.free_server()
        self.save_servers()
        return True
    
    def get_all_servers(self):
        """Lấy danh sách tất cả các server"""
        return self.servers 