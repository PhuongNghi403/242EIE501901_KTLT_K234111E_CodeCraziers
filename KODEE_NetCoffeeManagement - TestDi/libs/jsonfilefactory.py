import os
import json
from datetime import datetime


class JsonFileFactory:
    def __init__(self, base_dir):
        """Khởi tạo với thư mục cơ sở để lưu các file JSON"""
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def create_file(self, file_name, data=None):
        """Tạo file JSON mới với dữ liệu ban đầu"""
        file_path = os.path.join(self.base_dir, file_name)

        # Nếu file đã tồn tại, không ghi đè
        if os.path.exists(file_path):
            return False

        # Tạo file mới
        with open(file_path, 'w', encoding='utf-8') as f:
            if data is None:
                data = []
            json.dump(data, f, ensure_ascii=False, indent=4)

        return True

    def read_file(self, file_name, default_data=None):
        """Đọc dữ liệu từ file JSON"""
        file_path = os.path.join(self.base_dir, file_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Nếu file không tồn tại hoặc không phải JSON hợp lệ, trả về dữ liệu mặc định
            return [] if default_data is None else default_data

    def write_file(self, file_name, data):
        """Ghi dữ liệu vào file JSON"""
        file_path = os.path.join(self.base_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return True

    def append_to_file(self, file_name, item):
        """Thêm một mục vào file JSON"""
        file_path = os.path.join(self.base_dir, file_name)

        # Đọc dữ liệu hiện có
        data = self.read_file(file_name, [])

        # Thêm mục mới
        data.append(item)

        # Ghi lại file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return True

    def update_in_file(self, file_name, item, id_field='id'):
        """Cập nhật một mục trong file JSON dựa trên trường ID"""
        file_path = os.path.join(self.base_dir, file_name)

        # Đọc dữ liệu hiện có
        data = self.read_file(file_name, [])

        # Tìm và cập nhật mục
        updated = False
        for i, existing_item in enumerate(data):
            if existing_item.get(id_field) == item.get(id_field):
                data[i] = item
                updated = True
                break

        # Nếu không tìm thấy, thêm mới
        if not updated:
            data.append(item)

        # Ghi lại file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return True

    def delete_from_file(self, file_name, item_id, id_field='id'):
        """Xóa một mục khỏi file JSON dựa trên ID"""
        file_path = os.path.join(self.base_dir, file_name)

        # Đọc dữ liệu hiện có
        data = self.read_file(file_name, [])

        # Lọc ra các mục không có ID trùng khớp
        data = [item for item in data if item.get(id_field) != item_id]

        # Ghi lại file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return True

    def backup_file(self, file_name):
        """Tạo bản sao lưu của file JSON"""
        file_path = os.path.join(self.base_dir, file_name)
        backup_file_name = f"{os.path.splitext(file_name)[0]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        backup_file_path = os.path.join(self.base_dir, "backups", backup_file_name)

        # Tạo thư mục backups nếu chưa tồn tại
        os.makedirs(os.path.join(self.base_dir, "backups"), exist_ok=True)

        # Đọc dữ liệu từ file gốc
        data = self.read_file(file_name, [])

        # Ghi vào file backup
        with open(backup_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return backup_file_path