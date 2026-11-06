# Quy ước dự án Travel Planner Agent

## 1. Cách học và làm việc

- Làm từng task nhỏ theo kế hoạch.
- Người học tự viết; AI giải thích, gợi ý và review.
- Hoàn thành và kiểm tra task hiện tại trước khi chuyển tiếp.
- Giữ thay đổi đúng phạm vi; không thêm tính năng ngoài yêu cầu.

## 2. Git và rollback

- Kiểm tra thay đổi bằng git diff trước khi commit.
- Sau mỗi task đã kiểm tra, người học chủ động tạo commit.
- AI không tự commit nếu chưa được yêu cầu.
- Tạo tag cho phiên bản ổn định trước thay đổi lớn.
- Ưu tiên git revert cho commit đã chia sẻ.
- Không dùng reset --hard hoặc xóa thay đổi khi chưa kiểm tra.
- Rollback code không bảo đảm khôi phục hành vi model bên ngoài.

## 3. Môi trường và dependency

- Chạy Python, Git và môi trường ảo trong Ubuntu WSL.
- Ghi phiên bản Python và cách thiết lập trong README.md.
- Cài thư viện trong .venv, không cài vào Python hệ thống.
- Khóa phiên bản dependency trong requirements.txt.
- Khi nâng dependency, cập nhật file phiên bản và chạy lại kiểm thử.
- Chỉ thêm dependency khi có nhu cầu cụ thể.

## 4. Phân chia trách nhiệm

- models.py định nghĩa cấu trúc dữ liệu dùng chung.
- integrations/ chứa SDK, HTTP và xử lý lỗi nhà cung cấp.
- agents/ chứa logic agent.
- workflow.py điều phối các bước.
- evaluator.py kiểm tra ràng buộc bằng Python.
- UI gọi logic ứng dụng, không gọi trực tiếp SDK Gemini/Tavily.
- Không thêm LangGraph trước chặng chuyển đổi đã lên kế hoạch.

## 5. Prompt và kiểm thử

- Lưu prompt trong prompts/ và quản lý bằng Git.
- Giữ dữ liệu kiểm thử cố định trong tests/fixtures/.
- Dùng mock cho kiểm thử offline.
- Phân biệt kết quả kiểm thử offline và gọi API thật.
- Khi đổi prompt, model hoặc workflow, chạy lại bộ đánh giá.
- Không kiểm tra LLM bằng cách yêu cầu văn bản giống hệt;
  kiểm tra schema, ràng buộc và chất lượng cần đạt.

### Quy ước kiểm thử đầu vào

- Dùng `unittest`; đặt test trong `tests/test_models.py`.
- Chạy tại gốc dự án: `PYTHONPATH=src python -m unittest discover -s tests -v` với `.venv` đã kích hoạt.
- Dùng ngày tương đối cho test hôm nay/quá khứ/tương lai để tránh dữ liệu hết hạn.
- Với dữ liệu sai, dùng `assertRaises(ValidationError)` và kiểm tra vị trí lỗi (`loc`); kiểm tra loại lỗi khi cần phân biệt nguyên nhân.
- Đặt cả thao tác tạo model và assertion bên trong `subTest` để lỗi được gắn đúng trường hợp.
- Khi sửa validator, chạy lại bộ test và cập nhật phạm vi đã kiểm chứng trong README.
- Hiện thống nhất tên trường ngày khởi hành là `departure_day`; nếu đổi tên phải sửa đồng thời model, test và tài liệu.

## 6. Bảo mật

- Không commit .env, API key, token hoặc mật khẩu.
- .env.example chỉ chứa tên biến và giá trị mẫu không bí mật.
- Không ghi bí mật hoặc dữ liệu cá nhân không cần thiết vào log.
- Không tự kích hoạt dịch vụ trả phí.
