from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# URL cơ bản của Node.js API
NODE_BASE_URL = 'http://10.82.53.14:8080'
CUSTOMER_API_URL = f"{NODE_BASE_URL}/customers/add"


# --- PHẦN 1: QUẢN LÝ CÔNG VIỆC (TODOS) ---

@app.route('/')
def index():
    try:
        # Controller gọi sang Node.js API để lấy dữ liệu công việc
        response = requests.get(TODO_API_URL)
        todos = response.json()
    except Exception as e:
        todos = []
        print(f"Không thể kết nối đến Node.js API (todos): {e}")
        
    # Trả về View (template) kèm theo dữ liệu
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    if title:
        # Controller gửi dữ liệu mới sang Node.js API lưu trữ
        requests.post(TODO_API_URL, json={'title': title})
        
    return redirect(url_for('index'))


# --- PHẦN 2: QUẢN LÝ KHÁCH HÀNG (CUSTOMERS) ---

@app.route('/customers')
def list_customers():
    try:
        # Controller gọi sang Node.js API lấy danh sách khách hàng
        response = requests.get(CUSTOMER_API_URL)
        customers = response.json()
    except Exception as e:
        customers = []
        print(f"Không thể kết nối đến Node.js API (customers): {e}")
        
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['POST'])
def add_customer():
    idcustomer = request.form.get('id')
    name = request.form.get('name')
    age = request.form.get('age')
    
    if name:
        payload = {
            'id': idcustomer,  # Node.js API sẽ tự sinh ID
            'name': name,
            'age': age
        }
        requests.post(CUSTOMER_API_URL, json=payload)
        
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Chạy Flask ở cổng 5000
    app.run(port=5000, debug=True)