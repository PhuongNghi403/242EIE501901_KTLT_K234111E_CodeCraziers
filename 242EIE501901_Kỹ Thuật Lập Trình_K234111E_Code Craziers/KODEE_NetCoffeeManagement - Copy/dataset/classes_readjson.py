import os
import json

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
