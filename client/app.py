from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

# URL của Node.js API
NODE_API_URL = 'http://10.82.53.14:8080/'

@app.route('/')
def index():
    try:
        # Controller gọi sang Node.js API để lấy dữ liệu
        response = requests.get(NODE_API_URL)
        todos = response.json()
    except Exception as e:
        todos = []
        print(f"Không thể kết nối đến Node.js API: {e}")
        
    # Trả về View (template) kèm theo dữ liệu
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    if title:
        # Controller gửi dữ liệu mới sang Node.js API lưu trữ
        requests.post(NODE_API_URL, json={'title': title})
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Chạy Flask ở cổng 5000
    app.run(port=5000, debug=True)