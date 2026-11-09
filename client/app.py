from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import uuid
from PIL import Image

app = Flask(__name__)

# Thư mục lưu ảnh bản resize cho client (ví dụ: static/images)
CLIENT_IMAGES_FOLDER = 'static/images'
os.makedirs(CLIENT_IMAGES_FOLDER, exist_ok=True)

# Cấu hình giới hạn
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# URL cơ bản của Node.js API
NODE_BASE_URL = 'http://10.82.53.14:8080'
TODO_API_URL = f"{NODE_BASE_URL}/todos"
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
    customer_id = request.form.get('id')
    name = request.form.get('name')
    age = request.form.get('age')
    
    file = request.files.get('image')
    
    if not file or file.filename == '':
        return "Vui lòng chọn hình ảnh!", 400
        
    # 1. Kiểm tra định dạng đuôi file (.jpg, .png)
    if not allowed_file(file.filename):
        return "Định dạng file không hỗ trợ! Chỉ chấp nhận JPG, PNG.", 400
        
    # 2. Kiểm tra dung lượng nhỏ hơn 5MB
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0) # Reset con trỏ file về đầu
    
    if file_length > MAX_FILE_SIZE:
        return "Dung lượng ảnh vượt quá giới hạn 5MB!", 400

    try:
        # Mở ảnh bằng Pillow để kiểm tra kích thước và xử lý
        img = Image.open(file)
        width, height = img.size
        
        # 3. Kiểm tra kích thước > 100px (Cả chiều rộng và chiều cao phải > 100px)
        if width <= 100 or height <= 100:
            return "Kích thước ảnh quá nhỏ! Yêu cầu lớn hơn 100px (cả rộng và cao).", 400
            
        # 4. Đặt tên file không trùng lặp (dùng UUID kết hợp đuôi gốc)
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext == 'jpeg':
            ext = 'jpg'
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Chuẩn bị ảnh (nếu là ảnh PNG có nền trong suốt, chuyển sang RGB nếu lưu JPG để tránh lỗi)
        if img.mode in ('RGBA', 'LA') and ext == 'jpg':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background

        # 5. Xử lý lưu bản resize width = 200px vào thư mục images của client
        aspect_ratio = height / width
        new_height = int(200 * aspect_ratio)
        img_resized = img.resize((200, new_height), Image.Resampling.LANCZOS)
        
        client_image_path = os.path.join(CLIENT_IMAGES_FOLDER, unique_filename)
        # Lưu với chất lượng 80%
        if ext == 'jpg':
            img_resized.save(client_image_path, 'JPEG', quality=80)
        else:
            img_resized.save(client_image_path, 'PNG', optimize=True)

        # 6. Đẩy dữ liệu và file hình ảnh đã xử lý sang Node.js API để lưu vào database polymartdb
        form_data = {
            'id': customer_id,
            'name': name,
            'age': age,
            'imgname':unique_filename
        }

        # Mở lại file đã resize để gửi đi qua request POST sang Node.js
        with open(client_image_path, 'rb') as img_to_send:
            files_payload = {
                'image': (unique_filename, img_to_send, f'image/{"jpeg" if ext == "jpg" else "png"}')
            }
            
            response = requests.post(CUSTOMER_API_URL, json=form_data)

        # Kiểm tra phản hồi từ Node.js server
        if response.status_code == 200 or response.status_code == 201:
            return f"Thêm khách hàng thành công! Đã lưu ảnh: {unique_filename} và đẩy dữ liệu lên Node.js."
        else:
            return f"Xử lý ở Flask thành công nhưng Node.js báo lỗi: {response.text}", response.status_code

    except Exception as e:
        return f"Đã xảy ra lỗi khi xử lý ảnh hoặc gửi dữ liệu: {str(e)}", 500


if __name__ == '__main__':
    # Chạy Flask ở cổng 5000
    app.run(port=5000, debug=True)