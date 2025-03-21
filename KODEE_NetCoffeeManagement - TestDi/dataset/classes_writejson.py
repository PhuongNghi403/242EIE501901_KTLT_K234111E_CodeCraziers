import os
import json
import random
from datetime import datetime, timedelta


def generate_employees():
    """Tạo dữ liệu mẫu cho nhân viên"""
    employees = []

    # Tạo 5 nhân viên
    for i in range(1, 6):
        phone = '0' + ''.join(str(random.randint(0, 9)) for _ in range(9))

        employee = {
            'id': f'EM{i:02d}',
            'name': f'Employee {i}',
            'password': '123',
            'phone': phone,
            'address': f'Employee Address {i}',
            'position': 'Employee'
        }
        employees.append(employee)

    # Lưu vào file JSON
    with open(os.path.join('employees.json'), 'w', encoding='utf-8') as f:
        json.dump(employees, f, ensure_ascii=False, indent=4)

    print(f"Created {len(employees)} employees.")
    return employees


def generate_managers():
    """Tạo dữ liệu mẫu cho quản lý"""
    managers = []

    # Tạo 3 quản lý
    for i in range(1, 4):
        phone = '0' + ''.join(str(random.randint(0, 9)) for _ in range(9))
        manager = {
            'id': f'MN{i:02d}',
            'name': f'Manager {i}',
            'password': '456',
            'phone': phone,
            'address': f'Manager Address {i}',
            'position': 'Manager'
        }
        managers.append(manager)

    # Lưu vào file JSON
    with open(os.path.join('managers.json'), 'w', encoding='utf-8') as f:
        json.dump(managers, f, ensure_ascii=False, indent=4)

    print(f"Created {len(managers)} managers.")
    return managers


def generate_menu_items():
    """Tạo dữ liệu mẫu cho menu"""
    menu_items = []

    # Tạo danh sách food
    food_data = [
        ("Mì xào bò", 40000, "Food"),
        ("Mì xào trứng", 30000, "Food"),
        ("Mì xào bò trứng", 45000, "Food"),
        ("Nui xào trứng", 30000, "Food"),
        ("Nui xào bò", 40000, "Food"),
        ("Nui xào bò trứng", 45000, "Food"),
        ("Cơm chiên trứng", 30000, "Food"),
        ("Cơm chiên bò xào", 40000, "Food")
    ]

    # Tạo danh sách menu_items từ dữ liệu trên
    for i, (name, price, category) in enumerate(food_data, start=1):
        menu_item = {
            'id': f'FD{i:03d}',
            'name': name,
            'price': price,  # Giá gốc (không còn random)
            'category': 'Food',
            'order_count': 0
        }
        menu_items.append(menu_item)

    # Tạo danh sách drink
    drink_data = [
        ("Nước suối", 10000, "Drink"),
        ("Sting", 15000, "Drink"),
        ("Pepsi", 15000, "Drink"),
        ("Olong Tea Plus", 30000, "Drink"),
        ("Trà tắc", 15000, "Drink"),
        ("Trà sữa", 25000, "Drink"),
        ("Matcha Latte", 30000, "Drink"),
    ]

    for i, (name, price, category) in enumerate(drink_data, start=1):
        menu_item = {
            'id': f'DR{i:03d}',
            'name': name,
            'price': price,
            'category': 'Drink',
            'order_count': 0
        }
        menu_items.append(menu_item)

    # Tạo danh sách snack
    snack_data = [
        ("Snack (random)", 10000, "Snack"),
        ("Nui sấy", 8000, "Snack"),
        ("Khô gà", 12000, "Snack"),
        ("Khô bò", 17000, "Snack"),
        ("Đậu phộng gói", 10000, "Snack"),
    ]

    for i, (name, price, category) in enumerate(snack_data, start=1):
        menu_item = {
            'id': f'SN{i:03d}',
            'name': name,
            'price': price,
            'category': 'Snack',
            'order_count': 0
        }
        menu_items.append(menu_item)

    # Lưu vào file JSON
    with open(os.path.join('menu_items.json'), 'w', encoding='utf-8') as f:
        json.dump(menu_items, f, ensure_ascii=False, indent=4)

    print(f"Created {len(menu_items)} menu items.")
    return menu_items


def generate_shifts(employees):
    """Tạo dữ liệu mẫu cho ca làm"""
    shifts = []

    # Tạo ca làm cho 7 ngày gần đây
    today = datetime.now()
    shift_names = ['Morning', 'Afternoon', 'Evening']

    for i in range(7):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')

        for j, shift_name in enumerate(shift_names):
            # Chọn ngẫu nhiên một nhân viên
            employee = random.choice(employees)

            shift = {
                'id': f'S{i * 3 + j + 1:03d}',
                'name': shift_name,
                'employee_id': employee['id'],
                'date': date_str
            }
            shifts.append(shift)

    # Lưu vào file JSON
    with open(os.path.join('shifts.json'), 'w', encoding='utf-8') as f:
        json.dump(shifts, f, ensure_ascii=False, indent=4)

    print(f"Created {len(shifts)} shifts.")
    return shifts


def generate_servers():
    """Tạo dữ liệu mẫu cho server (máy tính)"""
    servers = []

    # Tạo 30 server từ SE01 -> SE30
    for i in range(1, 31):
        server = {
            'id': f'SE{i:02d}',
            'name': f'Server {i}',
            'status': 'available',  # available hoặc occupied
            'customer_name': '',
            'customer_phone': '',
            'start_time': '',
            'usage_time': 0,  # Thời gian sử dụng (giờ)
            'price_per_hour': 10000  # Giá tiền mỗi giờ (VND)
        }
        servers.append(server)

    # Cập nhật ngẫu nhiên một số server sang trạng thái đang sử dụng
    num_occupied = random.randint(5, 15)  # Số lượng server đang được sử dụng
    occupied_servers = random.sample(servers, num_occupied)

    for server in occupied_servers:
        server['status'] = 'occupied'
        server['customer_name'] = f'Customer {random.randint(1, 100)}'
        server['customer_phone'] = '0' + ''.join(str(random.randint(0, 9)) for _ in range(9))

        # Thời gian bắt đầu ngẫu nhiên trong ngày hôm nay
        hours = random.randint(8, 21)  # Từ 8h sáng đến 21h tối
        minutes = random.randint(0, 59)
        start_time = f"{hours:02d}:{minutes:02d}"
        server['start_time'] = start_time

        # Thời gian sử dụng từ 1-5 giờ
        server['usage_time'] = random.randint(1, 5)

    # Lưu vào file JSON
    with open(os.path.join('servers.json'), 'w', encoding='utf-8') as f:
        json.dump(servers, f, ensure_ascii=False, indent=4)

    print(f"Created {len(servers)} servers (with {num_occupied} occupied).")
    return servers


def generate_invoices(employees, menu_items, servers):
    """Tạo dữ liệu mẫu cho hóa đơn với thông tin server và món ăn."""
    invoices = []
    num_invoices = 50  # Tổng số hóa đơn
    today = datetime.now()

    for i in range(1, num_invoices + 1):
        # Chọn ngẫu nhiên 1 ngày trong 7 ngày gần đây
        invoice_date = today - timedelta(days=random.randint(0, 6))

        # Tạo giờ vào ngẫu nhiên
        time_in_hour = random.randint(0, 23)
        time_in_minute = random.randint(0, 59)
        time_in = invoice_date.replace(hour=time_in_hour, minute=time_in_minute, second=0, microsecond=0)

        # Chọn ngẫu nhiên một nhân viên
        employee = random.choice(employees)

        # Tạo số điện thoại (bắt đầu bằng '0' + 9 chữ số random)
        phone = '0' + ''.join(str(random.randint(0, 9)) for _ in range(9))

        # Tạo đơn hàng (order) với thông tin server
        usage_time = random.randint(1, 24)  # Số giờ sử dụng (giờ)
        # Điều chỉnh số giờ để tổng tiền dao động từ 10.000 VND đến 240.000 VND
        usage_price = usage_time * 10000  # Giá server theo số giờ

        order = {
            'customer_name': f'Customer {i}',
            'customer_phone': phone,
            'computer_id': f'M{random.randint(1, 16):02d}',
            'usage_time': usage_time,
            'usage_price': usage_price,
            'items': []
        }

        # Thêm thông tin server vào hóa đơn
        selected_server = random.choice(servers)
        server_item = {
            'item_id': selected_server['id'],  # SE01, SE02, ...
            'name': f'Server {selected_server["id"][-2:]}',  # "Server 01", "Server 02", ...
            'price': selected_server['price_per_hour'] * usage_time,  # Tính tiền server theo số giờ sử dụng
            'quantity': 1  # Mỗi hóa đơn chỉ có 1 máy
        }
        order['items'].append(server_item)

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
            order['items'].append(item)

        # Tính tổng tiền cho hóa đơn
        food_total = sum(item['price'] * item['quantity'] for item in order['items'])
        total = food_total + server_item['price']  # Tổng tiền bao gồm server và món ăn

        # Tính giờ ra (time_out) = time_in + usage_time (giờ)
        time_out = time_in + timedelta(hours=usage_time)

        # Chuyển đổi ngày và giờ sang chuỗi định dạng
        date_str = invoice_date.strftime('%Y-%m-%d')
        time_in_str = time_in.strftime('%H:%M')
        time_out_str = time_out.strftime('%H:%M')

        # Tạo hóa đơn
        invoice = {
            'id': f'IN{i:03d}',
            'employee_id': employee['id'],
            'employee_name': employee['name'],
            'date': date_str,
            'time_in': time_in_str,
            'time_out': time_out_str,
            'total': total,
            'order': order
        }

        invoices.append(invoice)

    # Lưu dữ liệu hóa đơn vào file JSON
    with open('invoices.json', 'w', encoding='utf-8') as f:
        json.dump(invoices, f, ensure_ascii=False, indent=4)

    print(f"Created {len(invoices)} invoices.")
    return invoices


def main():
    """Hàm chính để tạo dữ liệu mẫu"""
    print("Generating sample data...")

    try:
        # Tạo dữ liệu
        employees = generate_employees()
        managers = generate_managers()
        menu_items = generate_menu_items()
        shifts = generate_shifts(employees)
        servers = generate_servers()
        invoices = generate_invoices(employees, menu_items, servers)

        print("Successfully generated sample data.")
    except Exception as e:
        print(f"Error generating sample data: {e}")


if __name__ == "__main__":
    main()
