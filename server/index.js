const express = require('express');
const sql = require('mssql'); // Thêm thư viện mssql

const app = express();
const port = 8080;

// Cấu hình kết nối SQL Server
const dbConfig = {
  user: 'sa',                  // Tên đăng nhập (ví dụ: sa)
  password: '123456', // Mật khẩu tài khoản của bạn
  server: 'ADMIN-PC',
  database: 'PolyMartDB',
  options: {
    encrypt: true,
    trustServerCertificate: true
  }
};

// Hàm kết nối và kiểm tra Database
async function connectDB() {
  try {
    await sql.connect(dbConfig);
    console.log('✅ Kết nối thành công tới SQL Server - PolyMartDB!');
  } catch (err) {
    console.error('❌ Lỗi kết nối SQL Server:', err);
  }
}

connectDB();

// Middleware để đọc JSON từ request (nếu cần dùng API POST/PUT sau này)
app.use(express.json());

// Define a route for GET requests to the root URL
app.get('/', (req, res) => {
  res.send('Hello World from Express & PolyMartDB!');
});

// Ví dụ: Lấy dữ liệu từ một bảng trong PolyMartDB
app.get('/customers/:id', async (req, res) => {
  try {
    const customerId = req.params.id; // Lấy chuỗi ID từ URL (VD: "U1")

    // Sử dụng Prepared Statement để tránh lỗi SQL Injection
    let result = await new sql.Request()
      .input('id', sql.VarChar, customerId)
      .query('SELECT * FROM Customers WHERE CustomerID = @id');

    if (result.recordset.length === 0) {
      return res.status(404).send(`Không tìm thấy khách hàng với mã: ${customerId}`);
    }

    res.json(result.recordset[0]);
  } catch (err) {
    res.status(500).send('Lỗi truy vấn: ' + err.message);
  }
});

// ==========================================
// CODE CHO TRANG 404 (Phải đặt ở cuối cùng)
// ==========================================
app.use((req, res, next) => {
  res.status(404).send(`
    <div style="text-align: center; margin-top: 50px; font-family: Arial;">
      <h1 style="font-size: 50px; color: #ff4d4d;">404</h1>
      <h2>Oops! Không tìm thấy trang bạn yêu cầu.</h2>
      <p>Đường dẫn <strong>${req.originalUrl}</strong> không tồn tại trên hệ thống.</p>
      <a href="/" style="color: #007bff; text-destination: none; font-weight: bold;">Quay về trang chủ</a>
    </div>
  `);
});

// Start the server
app.listen(port, () => {
  console.log(`🚀 Server đang chạy tại http://localhost:${port}`);
});