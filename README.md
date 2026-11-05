# Travel Planner Agent

Dự án học cách xây dựng AI Agent thông qua ứng dụng lập kế hoạch du lịch: nhận yêu cầu của du khách, nghiên cứu thông tin và đề xuất lịch trình phù hợp với ngân sách.

## Trạng thái hiện tại

**Dự án đang ở giai đoạn thiết lập, chưa có ứng dụng hoặc agent chạy được.**

- Đã chốt phạm vi MVP và hoàn thành bài thiết kế đầu vào (Task 01).
- Đang chuẩn bị môi trường phát triển (Task 02).
- Đã xác nhận qua terminal: Ubuntu 22.04 chạy WSL 2, Python 3.10.12 và Git 2.34.1.
- Chưa xác nhận hoàn tất môi trường ảo và kết nối VS Code với thư mục dự án trong WSL.
- Chưa tích hợp Gemini/Tavily, chưa có dependency ứng dụng hoặc bộ kiểm thử.

## Phạm vi MVP

- Điểm đến: Paris, Lyon hoặc Strasbourg; một thành phố mỗi chuyến.
- Điểm xuất phát: một thành phố trong châu Âu, khác điểm đến.
- Thời lượng: 2–7 ngày lịch, gồm ngày đi và ngày về.
- Người tham gia: người lớn; ngân sách EUR cho cả nhóm.
- Gợi ý địa điểm, khách sạn, ăn uống và phương tiện với giá ước tính có nguồn.
- Tạo ba phương án: **Tiết kiệm**, **Cân bằng**, **Trải nghiệm**.

Mỗi phương án dự kiến có lịch từng ngày, thời gian di chuyển ước tính, bảng chi phí và nguồn tham khảo. Nếu dữ liệu hoặc ngân sách không đủ, ứng dụng sẽ báo giới hạn và chỉ hiển thị các phương án khả thi.

MVP chưa bao gồm đặt vé, đặt phòng, thanh toán, tài khoản người dùng hoặc hành trình nhiều thành phố. Việc tối ưu ban đầu tập trung vào ngân sách, thời gian và nhóm địa điểm gần nhau; chưa bảo đảm nghiệm tối ưu toán học hay giá và tình trạng chỗ theo thời gian thực.

## Dữ liệu đầu vào

| Trường | Kiểu Python dự kiến | Quy tắc |
| --- | --- | --- |
| `origin_city` | `str` | Không rỗng; thành phố trong châu Âu |
| `destination_city` | `str` | Paris, Lyon hoặc Strasbourg; khác điểm xuất phát |
| `departure_date` | `date` | Không nằm trong quá khứ |
| `duration_days` | `int` | Từ 2 đến 7 |
| `num_adults` | `int` | Ít nhất 1 |
| `total_budget_eur` | `int` | Lớn hơn 0; nhận số EUR nguyên cho cả nhóm |
| `additional_preferences` | `str \| None` | Tùy chọn; tối đa 1.000 ký tự |

Ngày về được tính bằng ngày khởi hành cộng `duration_days - 1`, không yêu cầu nhập riêng.

Ngân sách gồm đi/về, lưu trú, ăn uống, đi lại nội thành, vé tham quan và khoản dự phòng 10% nằm trong tổng ngân sách. Dữ liệu đầu vào hợp lệ chưa đồng nghĩa ngân sách đủ thực hiện chuyến đi.

## Kiến trúc và công nghệ dự kiến

```text
Streamlit → Supervisor → Research Agent / Transport Agent
                      → Planner → Evaluator → Kết quả
```

- **Python + Pydantic:** logic và kiểm tra cấu trúc dữ liệu.
- **Gemini API:** LLM cho nghiên cứu và lập lịch trình.
- **Tavily:** tool tìm kiếm thông tin có nguồn.
- **Streamlit:** form nhập yêu cầu và so sánh lịch trình.
- **LangGraph:** bổ sung sau khi workflow Python hoạt động và được kiểm thử.

Supervisor ban đầu là code điều phối. Evaluator dùng Python để tính tiền, kiểm tra thời gian và phản hồi lỗi; Planner được sửa tối đa một lượt. Kết quả nghiên cứu được dùng chung cho ba phương án, với giới hạn sáu lượt tìm kiếm mỗi lần lập kế hoạch.

Ưu tiên free tier; khoảng 20 USD là ngân sách dự phòng toàn dự án. Quyền truy cập model, quota và giá dịch vụ phải được kiểm tra khi tích hợp; không tự chuyển sang trả phí.

## Môi trường phát triển

Sử dụng **Windows + Ubuntu trong WSL 2 + VS Code**. Python, Git và môi trường ảo của dự án chạy trong Ubuntu.

Thư mục làm việc dự kiến trong WSL: `/home/quy/projects/travel-planner`. Các lệnh dưới đây chạy trong terminal Ubuntu, tại thư mục gốc của bản dự án bạn đang sử dụng:

```bash
python3 -m venv .venv
source .venv/bin/activate
which python
python --version
python -m pip --version
```

Nếu `.venv` đã được tạo thành công, chỉ cần kích hoạt và kiểm tra, không cần tạo lại. Python được chọn phải nằm trong `.venv/bin/python` của dự án.

Hiện chưa có `requirements.txt`, entrypoint ứng dụng hoặc bộ kiểm thử, nên chưa có lệnh cài dependency, chạy web hay chạy test. Các hướng dẫn đó sẽ được bổ sung khi chức năng tương ứng được xây dựng.

## Tổ chức mã nguồn dự kiến

Các thư mục dưới đây sẽ được tạo dần theo task, chưa phải cấu trúc đã triển khai:

```text
travel-planner/
├── README.md
├── rule.md
├── .gitignore
├── .env.example
├── requirements.txt
├── src/travel_planner/
│   ├── __init__.py
│   ├── models.py
│   ├── workflow.py
│   ├── evaluator.py
│   ├── integrations/
│   ├── agents/
│   └── prompts/
├── ui/app.py
└── tests/fixtures/
```

`integrations/` chứa giao tiếp Gemini/Tavily; UI và logic nghiệp vụ không phụ thuộc trực tiếp vào SDK. `prompts/` lưu prompt, `tests/fixtures/` lưu dữ liệu kiểm thử cố định.

## Cách phát triển và kiểm chứng

1. Thiết kế đầu vào và chuẩn bị môi trường.
2. Gọi LLM, kiểm tra đầu ra có cấu trúc với dữ liệu mẫu.
3. Học tool calling và xây vòng lặp agent có giới hạn.
4. Tách Research, Transport và Supervisor.
5. Xây Planner, kiểm tra ngân sách và Evaluator.
6. Làm web Streamlit và kiểm tra toàn luồng.
7. Chuyển sang LangGraph và chạy kiểm thử hồi quy.

Làm từng task nhỏ: người học tự viết, AI hướng dẫn và review. Kiểm thử offline bằng mock trước, sau đó xác minh API thật và đối chiếu nguồn thủ công; báo riêng kết quả của hai hình thức kiểm tra.

Sau mỗi task đã kiểm tra, người học chủ động tạo commit. Đánh dấu phiên bản ổn định trước thay đổi lớn; ghi phiên bản Python và khóa phiên bản thư viện. Quản lý prompt và dữ liệu kiểm thử bằng Git. AI không tự commit nếu chưa được yêu cầu.

Quy ước phát triển sẽ được ghi trong [rule.md](rule.md). Không đưa `.venv/`, `.env`, API key, mật khẩu hoặc dữ liệu cá nhân không cần thiết vào Git hay log. Chỉ cấu hình API key khi đến task tích hợp; không dán bí mật vào chat.
