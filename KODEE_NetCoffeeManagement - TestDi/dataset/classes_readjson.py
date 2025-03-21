import os
import json
from datetime import datetime, timedelta
from random import random


def load_employees():
    """Đọc dữ liệu nhân viên từ file employees.json"""
    file_path = 'employees.json'
    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại!")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        employees = json.load(f)
    return employees

def load_managers():
    """Đọc dữ liệu quản lý từ file managers.json"""
    file_path = 'managers.json'
    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại!")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        managers = json.load(f)
    return managers

def load_menu_items():
    """Đọc dữ liệu menu từ file menu_items.json"""
    file_path = 'menu_items.json'
    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại!")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        menu_items = json.load(f)
    return menu_items

def load_shifts():
    """Đọc dữ liệu ca làm từ file shifts.json"""
    file_path = 'shifts.json'
    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại!")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        shifts = json.load(f)
    return shifts

def load_invoices():
    """Đọc dữ liệu hoá đơn từ file invoices.json"""
    file_path = 'invoices.json'
    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại!")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        invoices = json.load(f)
    return invoices

def load_servers():
    """Đọc dữ liệu server (máy) từ file servers.json"""
    file_path = 'servers.json'
    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại!")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        servers = json.load(f)
    return servers
def update_invoice_data(employees, menu_items, servers, invoices):
    """Cập nhật dữ liệu hóa đơn với thông tin server và món ăn."""
    updated_invoices = []
    today = datetime.now()

    for invoice in invoices:
        # Cập nhật đơn hàng (order) với thông tin server
        order = invoice.get('order', {})

        # Chọn ngẫu nhiên 1 server từ danh sách servers
        selected_server = random.choice(servers)
        server_item = {
            'item_id': selected_server['id'],  # SE01, SE02, ...
            'name': f'Server {selected_server["id"][-2:]}',  # "Server 01", "Server 02", ...
            'price': selected_server['price_per_hour'] * order['usage_time'],  # Tính tiền server theo số giờ sử dụng
            'quantity': 1  # Mỗi hóa đơn chỉ có 1 máy
        }
        # Giữ server và món ăn trong order['items']
        order['items'] = [server_item]  # Khởi tạo với server

        # Thêm món ăn vào đơn hàng
        num_items = random.randint(3, 4)  # 3-4 món ăn
        for _ in range(num_items):
            menu_item = random.choice(menu_items)
            quantity = random.randint(1, 2)  # Số lượng mỗi món ăn 1-2
            item = {
                'item_id': menu_item['id'],
                'name': menu_item['name'],
                'price': menu_item['price'],
                'quantity': quantity
            }
            order['items'].append(item)  # Thêm món ăn vào list

        # Tính tổng tiền
        food_total = sum(item['price'] * item['quantity'] for item in order['items'])
        total = food_total + server_item['price']  # Tổng tiền bao gồm cả server và món ăn

        # Cập nhật giờ ra (time_out) = time_in + usage_time (giờ)
        time_in_str = invoice['time_in']
        time_in = datetime.strptime(f"{invoice['date']} {time_in_str}", "%Y-%m-%d %H:%M")
        time_out = time_in + timedelta(hours=order['usage_time'])
        time_out_str = time_out.strftime('%H:%M')

        # Cập nhật thông tin hóa đơn
        updated_invoice = {
            'id': invoice['id'],
            'employee_id': invoice['employee_id'],
            'employee_name': invoice['employee_name'],
            'date': invoice['date'],
            'time_in': time_in_str,
            'time_out': time_out_str,
            'total': total,
            'order': order
        }
        updated_invoices.append(updated_invoice)

    # Lưu lại file invoices mới
    with open('invoices.json', 'w', encoding='utf-8') as f:
        json.dump(updated_invoices, f, ensure_ascii=False, indent=4)

    print(f"Updated {len(updated_invoices)} invoices.")
    return updated_invoices

def main():
    """Hàm chính để đọc dữ liệu từ các file JSON và in ra màn hình"""
    print("Reading sample data from JSON files...")

    employees = load_employees()
    managers = load_managers()
    menu_items = load_menu_items()
    shifts = load_shifts()
    invoices = load_invoices()
    servers = load_servers()

    print(f"\nEmployees ({len(employees)}):")
    print(employees)

    print(f"\nManagers ({len(managers)}):")
    print(managers)

    print(f"\nMenu Items ({len(menu_items)}):")
    print(menu_items)

    print(f"\nShifts ({len(shifts)}):")
    print(shifts)

    print(f"\nInvoices ({len(invoices)}):")
    # Nếu muốn in toàn bộ invoices có thể rất dài, tuỳ bạn xử lý
    # Ở đây in 5 cái đầu làm ví dụ
    for inv in invoices[:5]:
        print(inv)

    print(f"\nServers ({len(servers)}):")
    print(servers)

    print("\nFinished reading JSON data.")

if __name__ == "__main__":
    main()
