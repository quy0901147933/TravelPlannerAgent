# Travel Planner Agent

Dự án học cách xây dựng AI Agent thông qua ứng dụng lập kế hoạch du lịch: nhận yêu cầu của du khách, nghiên cứu thông tin và đề xuất lịch trình phù hợp với ngân sách.

Đặc tả và tiêu chí nghiệm thu Chặng 1 (Task 01–04): [SPEC.md](SPEC.md).

## Trạng thái hiện tại

**Đã hoàn thành Task 01–08 (Chặng 1–2): đầu vào, gọi LLM thật, lịch trình có cấu trúc và xử lý lỗi có kiểm thử. Chưa có agent hoặc web chạy được.**

- Task 01: chốt phạm vi MVP và các trường đầu vào.
- Task 02: môi trường Ubuntu WSL 2, Python 3.10.12, Git và `.venv` đã hoạt động.
- Task 03: `TravelPreferences` dùng Pydantic để chuẩn hóa, kiểm tra dữ liệu và tính ngày về.
- Task 04: 20 phương thức kiểm thử bằng `unittest` đã đạt trong WSL ngày 06/11/2026.
- Task 05: đã dùng SDK `groq` với model `openai/gpt-oss-20b`; người học xác nhận nhận phản hồi từ API thật. Key đọc từ biến môi trường `GROQ_API_KEY`.
- Chọn Groq Free + GPT-OSS thay cho Gemini; không tự kích hoạt trả phí.
- Task 06: có Activity, TripDay, Itinerary và property tổng chi phí hoạt động.
- Task 07: sinh lịch trình từ dữ liệu giả lập qua Groq, kiểm tra schema và đối chiếu dữ liệu mẫu; người học xác nhận tổng 45 EUR.
- Task 08: xử lý lỗi qua cli(), kiểm thử offline bằng mock.
- Tổng 64 test offline: 46 test model và 18 test tạo lịch trình/CLI.
- Chưa tích hợp Tavily, tool calling, vòng lặp agent hoặc UI.

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

| Trường | Kiểu Python | Quy tắc hiện tại |
| --- | --- | --- |
| `origin_city` | `str` | Bỏ khoảng trắng hai đầu; không rỗng; khác điểm đến khi so sánh không phân biệt chữ hoa–thường |
| `destination_city` | `str` | Paris, Lyon hoặc Strasbourg; khác điểm xuất phát |
| `departure_day` | `date` | Từ hôm nay trở đi; nhận đối tượng `date` hoặc chuỗi ISO `YYYY-MM-DD` hợp lệ |
| `duration_days` | `int` | Từ 2 đến 7 |
| `num_adults` | `int` | Ít nhất 1 |
| `total_budget_eur` | `int` | Lớn hơn 0; nhận số EUR nguyên cho cả nhóm |
| `additional_preferences` | `str \| None` | Tùy chọn; bỏ khoảng trắng hai đầu; rỗng thành `None`; tối đa 1.000 ký tự sau chuẩn hóa |

Ngày về đọc qua property `trip.return_date`, được tính bằng `departure_day + timedelta(days=duration_days - 1)`, không yêu cầu nhập riêng. `return_date` hiện là Python property, không tự xuất hiện trong `model_dump()`.

Tên ngày khởi hành trong code và test hiện tại là `departure_day` (thiết kế ban đầu gọi là `departure_date`). Dùng `departure_day` khi tạo đối tượng.

### Giới hạn hiện tại

- Chưa xác minh `origin_city` là thành phố có thật hoặc thuộc châu Âu; đây vẫn là phạm vi sản phẩm, chưa là ràng buộc được model thực thi.
- `destination_city` phải đúng cách viết Paris, Lyon hoặc Strasbourg sau khi bỏ khoảng trắng; chưa tự chuẩn hóa `paris` thành `Paris`.
- Ngày hôm nay dựa trên `date.today()` và múi giờ hệ điều hành WSL.
- Chưa bật strict mode: Pydantic có thể chuyển đổi một số kiểu đầu vào. Bộ test hiện tại chưa cam kết từ chối mọi trường hợp ép kiểu.


Ngân sách gồm đi/về, lưu trú, ăn uống, đi lại nội thành, vé tham quan và khoản dự phòng 10% nằm trong tổng ngân sách. Dữ liệu đầu vào hợp lệ chưa đồng nghĩa ngân sách đủ thực hiện chuyến đi.

## Kiến trúc và công nghệ dự kiến

```text
Streamlit → Supervisor → Research Agent / Transport Agent
                      → Planner → Evaluator → Kết quả
```

- **Python + Pydantic:** logic và kiểm tra cấu trúc dữ liệu.
- **Groq + GPT-OSS:** LLM hiện tại; Task 05 dùng `openai/gpt-oss-20b` qua SDK `groq`.
- **Tavily:** tool tìm kiếm thông tin có nguồn.
- **Streamlit:** form nhập yêu cầu và so sánh lịch trình.
- **LangGraph:** bổ sung sau khi workflow Python hoạt động và được kiểm thử.

Supervisor ban đầu là code điều phối. Evaluator dùng Python để tính tiền, kiểm tra thời gian và phản hồi lỗi; Planner được sửa tối đa một lượt. Kết quả nghiên cứu được dùng chung cho ba phương án, với giới hạn sáu lượt tìm kiếm mỗi lần lập kế hoạch.

Ưu tiên free tier; khoảng 20 USD là ngân sách dự phòng toàn dự án. Quyền truy cập model, quota và giá dịch vụ phải được kiểm tra khi tích hợp; không tự chuyển sang trả phí.

## Môi trường phát triển

Sử dụng **Windows + Ubuntu trong WSL 2 + VS Code**. Python, Git và môi trường ảo của dự án chạy trong Ubuntu.

Thư mục dự án chính trong WSL: `/home/quy/projects/travel-planner`. Các lệnh dưới đây chạy trong terminal Ubuntu, tại thư mục gốc của bản dự án bạn đang sử dụng:

```bash
python3 -m venv .venv
source .venv/bin/activate
which python
python --version
python -m pip --version
```

Nếu `.venv` đã được tạo thành công, chỉ cần kích hoạt và kiểm tra, không cần tạo lại. Python được chọn phải nằm trong `.venv/bin/python` của dự án.

Cài dependency đã khóa phiên bản trong môi trường ảo:

```bash
cd /home/quy/projects/travel-planner
source .venv/bin/activate
python -m pip install -r requirements.txt
```

`requirements.txt` được đối chiếu với .venv khi chốt Task 08, gồm Pydantic 2.14.3, Groq SDK 1.7.0 và các dependency liên quan. `unittest` có sẵn trong Python. Chưa có entrypoint agent hoặc web.

## Kiểm tra kết nối Groq — Task 05

Chạy trong terminal Ubuntu WSL, tại thư mục gốc dự án:

```bash
cd /home/quy/projects/travel-planner
source .venv/bin/activate
read -rsp "Nhập Groq API key: " GROQ_API_KEY
echo
export GROQ_API_KEY
python check_groq.py
```

Key được nhập ẩn, chỉ tồn tại trong terminal hiện tại và được SDK đọc từ biến môi trường. Đóng terminal thì cần nhập lại. Không ghi key vào code, Git, log hoặc chat. Chưa dùng file `.env`; Python không tự nạp file này.

`check_groq.py` gửi một yêu cầu sinh văn bản thật đến `openai/gpt-oss-20b`, với timeout 20 giây và không tự retry. Người học đã xác nhận chạy thành công; script này chỉ kiểm tra kết nối; structured output được thử riêng trong generate_itinerary.py. Chưa xác minh tool calling hoặc chất lượng lịch trình thực tế.

`tests/test_api.py` là script kiểm tra API thủ công, có gọi mạng; không tính là một trong 20 test offline. Chạy riêng khi cần:

```bash
python tests/test_api.py
```

## Chạy kiểm thử model

Chạy từ thư mục gốc dự án trong Ubuntu WSL:

```bash
cd /home/quy/projects/travel-planner
source .venv/bin/activate
PYTHONPATH=src:. python -m unittest discover -s tests -p test_models.py -v
```

`PYTHONPATH=src` giúp Python tìm package `travel_planner` trong thư mục `src`. Mỗi lần chạy test là một phiên Python mới, không cần `importlib.reload()`.

Kết quả xác minh ngày 06/11/2026: **20 test, OK**. Đây là kiểm thử offline của model; không gọi Groq, Tavily hoặc dịch vụ bên ngoài. Sau Task 05, ảnh terminal người học cung cấp tiếp tục xác nhận 20 test OK và `git diff --check` không báo lỗi.

Bộ kiểm thử bao phủ:

- Dữ liệu hợp lệ, ngày đi hôm nay và cả ba điểm đến.
- Thời lượng 2–7 ngày; từ chối 1 và 8 ngày.
- Số người, ngân sách phải dương; chấp nhận giá trị tối thiểu 1.
- Ngày quá khứ; chuyển chuỗi ISO hợp lệ sang `date`; từ chối ngày sai, rỗng và `None`.
- Thành phố trùng nhau, kể cả khác chữ hoa–thường hoặc có khoảng trắng.
- Điểm xuất phát rỗng và điểm đến ngoài phạm vi.
- Bỏ khoảng trắng; sở thích rỗng thành `None`; giới hạn 1.000/1.001 ký tự.
- Ngày về cho thời lượng hợp lệ và chuyến đi qua cuối tháng/cuối năm.

### Cấu trúc đã có

```text
travel-planner/
├── README.md
├── rule.md
├── .gitignore
├── check_setup.py
├── check_groq.py
├── check_itinerary.py
├── generate_itinerary.py
├── requirements.txt
├── src/travel_planner/
│   ├── __init__.py
│   └── models.py
└── tests/
    ├── fixtures/paris_sample.json
    ├── test_models.py
    ├── test_generate_itinerary.py
    └── test_api.py
```


## Cấu trúc dự kiến cho các chặng tiếp theo

Sơ đồ dưới đây bao gồm cả các thành phần chưa triển khai; sẽ tạo dần theo task:

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

`integrations/` chứa giao tiếp Groq/Tavily; UI và logic nghiệp vụ không phụ thuộc trực tiếp vào SDK. `prompts/` lưu prompt, `tests/fixtures/` lưu dữ liệu kiểm thử cố định.

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

## Task 06–08: lịch trình có cấu trúc và xử lý lỗi

- Task 06: `Activity`, `TripDay`, `Itinerary` và property tổng chi phí hoạt động; 46 test model offline đạt.
- Task 07: người học đã xác nhận Groq sinh lịch trình mẫu đúng schema và dữ liệu nguồn, tổng 45 EUR. Dữ liệu giả lập không phải nghiên cứu du lịch thực tế.
- Task 08: `main()` kiểm tra đầu ra; `cli()` bắt lỗi thiếu key, file/JSON mẫu, timeout, kết nối, HTTP, JSON/schema đầu ra và dữ liệu khác mẫu; lỗi được in vào stderr và thoát mã 1. SDK không tự retry.
- Xác minh ngày 11/11/2026: 18 test tạo lịch trình/CLI offline đạt bằng mock, tách biệt với API thật. Test bao phủ mã thoát, thông báo, HTTP 401/403/429/500, dữ liệu thiếu/lặp/thay đổi và luồng thành công.
- Chưa kiểm tra chồng giờ hoặc tính khả thi du lịch thực tế; schema hiện tại chưa thực thi các quy tắc này.

Chạy hai bộ test offline, tránh script gọi mạng thủ công `tests/test_api.py`:

```bash
PYTHONPATH=src:. python -m unittest discover -s tests -p test_models.py -v
PYTHONPATH=src:. python -m unittest discover -s tests -p test_generate_itinerary.py -v
```

## Chạy lịch trình mẫu

Kiểm tra model bằng dữ liệu cố định, không gọi mạng:

```bash
PYTHONPATH=src python check_itinerary.py
```

Sinh lịch trình qua API thật (cần GROQ_API_KEY trong terminal hiện tại):

```bash
PYTHONPATH=src python generate_itinerary.py
```

Dữ liệu nằm ở tests/fixtures/paris_sample.json. Script dùng JSON Schema ở chế độ strict=False, sau đó Pydantic kiểm tra JSON/schema và Python đối chiếu điểm đến, ngày, số lần xuất hiện cùng tên/địa điểm/thời lượng/chi phí hoạt động. Tổng chi phí chỉ gồm hoạt động; chưa bao gồm đầy đủ lưu trú, vận chuyển hoặc dự phòng.

Không chạy discovery toàn bộ tests/ khi chỉ muốn kiểm thử offline: tests/test_api.py là script gọi mạng thủ công.
