# 🤖 Phil AI CLI (Client Edition)

> **Trợ lý Lập trình AI Cá nhân - Mạnh mẽ, Bảo mật và Tự chủ.**

`phil-cli` là giao diện dòng lệnh (Command Line Interface) giúp bạn kết nối và làm việc với hệ thống siêu máy tính **Phil AI Agent**.

Khác với các công cụ AI khác, `phil-cli` chạy cực nhẹ trên máy tính cá nhân của bạn, mọi tác vụ nặng (suy luận, training, chạy code) đều được xử lý trên Server mạnh mẽ (GPU A100).

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Size](https://img.shields.io/badge/Size-%3C50MB-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20MacOS%20%7C%20Linux-lightgrey)

---

## ✨ Tính Năng Nổi Bật

* **💬 Chat Thông Minh:** Hỏi đáp về code, kiến trúc hệ thống, và debug lỗi.
* **🛠️ Project Assistant:** Kéo thả (hoặc trỏ đường dẫn) cả một thư mục dự án, Phil sẽ đọc, hiểu và sửa lỗi trực tiếp trên nhiều file.
* **🚀 Siêu Nhẹ:** Không cần GPU, không cần Docker. Cài đặt trong 30 giây.
* **🔒 Bảo Mật:** Code của bạn được xử lý trong môi trường Sandbox cô lập (Isolated) trên Server.

---

## 📥 Hướng Dẫn Cài Đặt

### Yêu cầu
* Máy tính đã cài **Python 3.8** trở lên.
* Kết nối Internet.

### Cách 1: Cài đặt từ file (Khuyên dùng nội bộ)
Nếu bạn nhận được file `.whl` từ quản trị viên:

```bash
pip install phil_cli-1.0.0-py3-none-any.whl
```

### Cách 2: Cài đặt từ Source (Dành cho Dev)

```bash
pip install phil_cli-1.0.0-py3-none-any.whl
```
### 🔑 Đăng Nhập & Cấu Hình
Trước khi sử dụng, bạn cần kết nối với Phil Server bằng API Key.
1. **Lấy API Key:** Liên hệ quản trị viên hoặc truy cập Dashboard để lấy Key (Ví dụ: pk_...).
2. **Chạy lệnh đăng nhập:**

```bash
# Đăng nhập với Server mặc định
phil login pk_YOUR_API_KEY

# HOẶC: Đăng nhập với Server riêng (nếu bạn tự host)
phil login pk_YOUR_API_KEY --server "[https://api.your-domain.com](https://api.your-domain.com)"
```
Sau khi đăng nhập thành công, thông tin sẽ được lưu tại `~/.phil_config.json`.

---

### 📖 Hướng Dẫn Sử Dụng

1. **Chat với Phil (Chế độ Cơ bản)**
Bắt đầu cuộc hội thoại nhanh để hỏi đáp, viết snippet code ngắn.

```bash
pip chat
```
* **Gõ** `exit` hoặc `quit` để thoát.
* Phil hỗ trợ hiển thị Markdown, Code Highlighting đẹp mắt ngay trên Terminal.

2. Sửa lỗi Dự án (Chế độ Project) 🔥
Đây là tính năng mạnh nhất. Bạn có thể yêu cầu Phil sửa lỗi cho **toàn bộ thư mục code.**

**Cú pháp:**
```bash
phil fix [Đường_dẫn_thư_mục] "[Yêu_cầu_của_bạn]"
```
**Ví dụ thực tế:**
Bạn đang đứng tại thư mục dự án và muốn Phil sửa lỗi kết nối Database:
```bash
phil fix . "File main.py đang bị lỗi kết nối MongoDB, hãy sửa và thêm try-catch"
```
**Quy trình xử lý:**
1. CLI sẽ tự động nén thư mục hiện tại (.) thành file zip.
2. Gửi lên Server Phil AI.
3. Server giải nén -> Đọc code -> Sửa code -> Đóng gói lại.
4. CLI sẽ trả về đường dẫn tải xuống (Download Link) của dự án đã sửa.

---

### ❓ Câu Hỏi Thường Gặp (FAQ)
**Q: Tôi có cần GPU để chạy cái này không?**
A: **Không.** Máy tính văn phòng bình thường chạy tốt. GPU nằm ở trên Server.

**Q: Lỗi "Connection Refused"?**
A: Kiểm tra lại kết nối Internet hoặc URL Server trong lệnh phil login. Có thể Server đang bảo trì.

**Q: Lỗi "401 Unauthorized"?**
A: API Key của bạn bị sai, hết hạn hoặc chưa thanh toán gói cước. Vui lòng liên hệ Admin.

---

### 👨‍💻 Dành Cho Developer (Build Package)
Nếu bạn muốn đóng gói lại source code thành file cài đặt .whl để gửi cho người khác:
```bash
# 1. Cài đặt công cụ build
pip install build

# 2. Build gói
cd phil-client-package
python -m build

# 3. Kết quả
# File cài đặt sẽ nằm trong thư mục dist/
```

---

Powered by Phil AI Agent.