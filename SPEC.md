# SPEC — Chặng 2: Gọi LLM và tạo kết quả có cấu trúc

Ngày đối chiếu code: 13/11/2026. Phạm vi: Task 05–08.
Tài liệu mô tả hành vi đã triển khai; các giới hạn được ghi riêng, không coi prompt là bằng chứng kiểm tra.

## 1. Tổng quan

| Thành phần | Đặc tả |
| --- | --- |
| Goal | Kết nối LLM an toàn, biến dữ liệu du lịch giả lập thành lịch trình có cấu trúc, xác thực bằng Python và xử lý các lỗi dự kiến có kiểm soát. |
| Inputs | Biến môi trường GROQ_API_KEY và file JSON UTF-8 tests/fixtures/paris_sample.json. |
| Outputs | Itinerary hợp lệ, JSON in ra stdout và tổng chi phí hoạt động in riêng; lỗi dự kiến ra stderr và mã thoát 1. |
| Edge cases | Thiếu key/file, JSON sai, thiếu trường, dữ liệu ngoài giới hạn, nội dung rỗng, sai dữ liệu nguồn, timeout/kết nối/HTTP. |
| Performance constraints | Một lời gọi sinh lịch trình mỗi lần chạy hợp lệ; timeout SDK 30 giây, max_retries=0, max_completion_tokens=2048. Chưa có SLA hoặc benchmark tải. |
| Acceptance criteria | Schema hợp lệ, đối chiếu đúng dữ liệu nguồn, xử lý lỗi đúng nhánh; 46 test model và 18 test main/CLI đạt. Lần gọi thật do người học xác nhận riêng. |

Luồng: JSON mẫu → prompt + JSON Schema → Groq → chuỗi JSON → Pydantic → đối chiếu Python → hiển thị.

## 2. Phạm vi từng task

| Task | Đã triển khai | Bằng chứng và giới hạn |
| --- | --- | --- |
| 05 | Groq SDK 1.7.0, openai/gpt-oss-20b, key từ môi trường; check_groq.py | Người học xác nhận API thật phản hồi; không bật trả phí. Đây là thay đổi đã thống nhất so với lựa chọn Gemini ban đầu. |
| 06 | Activity, TripDay, Itinerary, property tổng tiền; check_itinerary.py | 46 test model gồm 20 test TravelPreferences cũ và 26 test mới. |
| 07 | generate_itinerary.py đọc fixture, gửi prompt, schema strict=False, validate JSON và đối chiếu dữ liệu bằng Counter | Người học xác nhận kết quả thật 45 EUR và kiểm tra mẫu thành công; không phải đánh giá chất lượng du lịch. |
| 08 | main() và cli(), bắt lỗi dự kiến, stderr, exit 1; test offline bằng mock | 18 test bao gồm các subTest; không gọi API thật trong bộ test. |

## 3. Inputs

| Đầu vào | Định dạng | Quy tắc hiện tại |
| --- | --- | --- |
| GROQ_API_KEY | Biến môi trường, chuỗi không rỗng | Kiểm tra tồn tại trước khi tạo client; key đúng hay không do API xác thực. Không hardcode/commit key. |
| destination_city | Chuỗi JSON | Output chỉ Paris/Lyon/Strasbourg và phải trùng fixture. |
| dates | Danh sách chuỗi YYYY-MM-DD | Output phải có ngày trùng danh sách, giữ đúng thứ tự; số ngày output 2–7. |
| activities | Danh sách object | Mỗi object có name, location, duration_minutes, estimated_cost_eur; model chọn start_time. |
| Fixture | File cố định theo đường dẫn tương đối với script | Không có schema Pydantic riêng cho input fixture; thiếu khóa/sai cấu trúc tùy ý chưa được xử lý đầy đủ. |

Fixture hiện tại: Paris; 20–21/12/2030; ba hoạt động có chi phí 30, 0 và 15 EUR cho cả nhóm.
TravelPreferences thuộc chặng trước, chưa được nối trực tiếp vào script sinh lịch trình.

## 4. Outputs và schema

| Model/trường | Kiểu | Ràng buộc đã thực thi |
| --- | --- | --- |
| Activity.name | str | Ít nhất 1 ký tự |
| Activity.location | str | Ít nhất 1 ký tự |
| Activity.start_time | datetime.time | Pydantic nhận giờ hợp lệ, ví dụ 09:00 |
| Activity.duration_minutes | int | > 0 |
| Activity.estimated_cost_eur | float | >= 0, hữu hạn; không NaN hoặc vô cực |
| TripDay.date | datetime.date | Ngày hợp lệ |
| TripDay.activities | list[Activity] | Ít nhất 1 hoạt động |
| Itinerary.title | str | Ít nhất 1 ký tự |
| Itinerary.destination_city | Literal | Paris, Lyon hoặc Strasbourg |
| Itinerary.days | list[TripDay] | 2–7 ngày |
| total_estimated_cost_eur | property float | Tổng chi phí mọi hoạt động, tính lại khi đọc; không là trường JSON mặc định |

model_json_schema() tạo mô tả cấu trúc; model_validate_json() đọc và xác thực phản hồi; model_dump_json(indent=2) xuất dữ liệu.
stdout chứa cả thông báo thành công, JSON và tổng tiền, không phải một tài liệu JSON thuần.
Tổng tiền chưa gồm đầy đủ khách sạn, vận chuyển hoặc dự phòng. Dùng float, chưa có quy tắc làm tròn tiền riêng.

## 5. Đối chiếu dữ liệu và edge cases

| Trường hợp | Hành vi |
| --- | --- |
| Thiếu/rỗng GROQ_API_KEY | ValueError trước khi tạo client; cli báo lỗi, exit 1 |
| Thiếu file | FileNotFoundError được cli bắt |
| JSON fixture sai cú pháp | JSONDecodeError được cli bắt |
| Nội dung API None hoặc chuỗi rỗng | ValueError; không chấp nhận là lịch trình |
| JSON đầu ra sai hoặc thiếu trường | Pydantic ValidationError; cli báo lỗi schema, exit 1 |
| Chi phí 0 | Hợp lệ, hỗ trợ hoạt động miễn phí |
| Chi phí âm/NaN/vô cực | Bị từ chối |
| Thời lượng 0/âm; danh sách hoạt động rỗng | Bị từ chối |
| 1 hoặc 8 ngày | Bị từ chối; 2 và 7 là biên hợp lệ |
| Điểm đến hoặc ngày khác fixture | ValueError |
| Hoạt động thiếu/thêm/lặp/thay đổi | Counter đối chiếu tuple tên, địa điểm, thời lượng, chi phí; sai thì ValueError |
| Timeout/mất kết nối | Bắt APITimeoutError/APIConnectionError; không tự retry |
| HTTP 401/403/429 | Thông báo riêng cho xác thực, từ chối và quota |
| HTTP khác, gồm 500 | Thông báo mã HTTP; không in nguyên body lỗi từ Groq |
| Luồng thành công | Không SystemExit lỗi; cli trả None, tiến trình kết thúc bình thường |

Counter không ràng buộc thứ tự hoạt động hoặc hoạt động thuộc ngày cụ thể.
Chuỗi chỉ chứa khoảng trắng chưa bị từ chối bởi min_length=1. Model chưa strict về ép kiểu và chưa cấm trường extra.
Ngày liên tiếp, hoạt động chồng giờ, giờ mở cửa, di chuyển và tính khả thi chỉ được đề cập trong prompt hoặc chưa triển khai; chưa có kiểm tra Python bảo đảm.

## 6. Performance constraints và bảo mật

| Ràng buộc | Cấu hình / mức bảo đảm |
| --- | --- |
| Lời gọi | Một create() trong luồng hợp lệ; không vòng lặp sửa lịch trình |
| Timeout | 30 giây ở SDK sinh lịch trình; không cam kết tổng tiến trình kết thúc chính xác trong 30 giây |
| Retry | max_retries=0 |
| Token | max_completion_tokens=2048; không phải số từ; đầu ra bị cắt có thể thất bại validation |
| Kết nối thử | check_groq.py timeout 20 giây, không tự retry |
| Môi trường | Python trong Ubuntu WSL, dependency khóa ở requirements.txt; không cài thêm ngoài nhu cầu |
| Key | Nhập ẩn vào biến môi trường; không đọc .env tự động; test dùng key giả |
| Kiểm thử | Mock Groq và file; không tiêu quota API |
| Chưa đo | Thời gian sinh trung bình, chất lượng tiếng Việt, tải đồng thời, tỷ lệ API thành công và chi phí production |

## 7. Acceptance criteria

| ID | Tiêu chí nghiệm thu | Kiểm chứng |
| --- | --- | --- |
| AC01 | Gọi model thật thành công với key ngoài code | Người học đã xác nhận check_groq.py |
| AC02 | Định nghĩa đủ ba model lồng nhau và ràng buộc bảng schema | 46 test model đạt, gồm test hồi quy đầu vào |
| AC03 | Tính tổng nhiều ngày/hoạt động, gồm hoạt động miễn phí | Test tổng tiền, thay đổi chi phí và zero float |
| AC04 | Trả JSON theo schema và validate thành Itinerary | Test JSON round-trip, schema sai; lần gọi thật do người học xác nhận |
| AC05 | Giữ đúng điểm đến/ngày và mỗi hoạt động đúng số lần | Test sai dữ liệu, thiếu/lặp/thêm/sửa |
| AC06 | Fixture mẫu hiện tại tạo tổng 45 EUR | Test offline luồng thành công và xác nhận lần gọi thật |
| AC07 | Lỗi dự kiến được báo có kiểm soát, exit 1 | Test CLI ValueError, ValidationError, file/JSON, timeout, kết nối, HTTP |
| AC08 | Luồng thành công không thoát lỗi | test_cli_success |
| AC09 | Không tự retry, không vòng lặp vô hạn | Kiểm tra cấu hình client và create gọi một lần |
| AC10 | Không in traceback tự động hoặc body HTTP nhạy cảm ở nhánh đã bắt | Test stdout/stderr và chuỗi bí mật giả trong HTTP error |
| AC11 | Tái chạy offline không cần key thật | 18 test bằng mock, 46 test model |
| AC12 | Tài liệu và dependency phản ánh môi trường | README.md, requirements.txt, pip check |

AC10 không phải bảo đảm che mọi bí mật tùy ý trong mọi exception; ValueError hiện in nội dung thông báo của ứng dụng.
Không chạy API thật lần nữa chỉ để viết SPEC; bằng chứng online là kết quả người học đã cung cấp trong phiên.

## 8. File và cách kiểm chứng

| File | Vai trò |
| --- | --- |
| src/travel_planner/models.py | Schema dùng chung và property |
| tests/fixtures/paris_sample.json | Dữ liệu giả lập cố định |
| generate_itinerary.py | Prompt hiện nằm trực tiếp trong main; gọi model, validation, CLI |
| tests/test_generate_itinerary.py | 18 test main/CLI offline |
| tests/test_models.py | 46 test model |
| check_groq.py / check_itinerary.py | Kiểm tra kết nối thật / model mẫu |
| tests/test_api.py | Script thủ công gọi API danh sách model; không phải test offline |
| README.md / requirements.txt | Hướng dẫn và phiên bản dependency |

Chạy tại /home/quy/projects/travel-planner:

```bash
source .venv/bin/activate
PYTHONPATH=src:. python -m unittest discover -s tests -p test_models.py -v
PYTHONPATH=src:. python -m unittest discover -s tests -p test_generate_itinerary.py -v
python -m pip check
git diff --check
```

Không discovery toàn bộ tests khi muốn offline vì tests/test_api.py gọi mạng ngay khi import.
Chạy thật sau khi cấu hình key: PYTHONPATH=src python generate_itinerary.py.

## 9. Ngoài phạm vi Chặng 2

Chưa có nghiên cứu Tavily, nguồn giá thực, tool calling, vòng lặp agent, Supervisor, Evaluator đầy đủ, ba phương án tối ưu, Streamlit, đặt dịch vụ hoặc triển khai production.
Prompt chưa tách ra prompts/ theo cấu trúc dài hạn của rule.md. Bộ xử lý lỗi chưa cam kết bắt lỗi lập trình hoặc fixture có cấu trúc tùy ý.
