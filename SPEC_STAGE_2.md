# SPEC — Travel Planner Agent

Ngày tổng hợp: **13/11/2026**. Mục đích: tra cứu thiết kế, môi trường và hành vi đã triển khai của hai chặng đầu.

## 1. Phạm vi và bằng chứng

Phân biệt **Task 01–02** (thiết kế đầu vào và chuẩn bị dự án) với **Chặng 1–2** (Task 01–08). Tài liệu ghi đầy đủ Task 01–02 và thông số đã có của Task 03–08 để khớp repository hiện tại.

Nguồn đối chiếu: [rule.md](rule.md), [README.md](README.md), mã nguồn, dữ liệu mẫu, kiểm thử và lịch sử Git trong repository WSL. Mốc mã nguồn được đọc: `b53320f`.

| Mốc | Kết quả |
| --- | --- |
| Task 01 | Chốt yêu cầu, kiểu dữ liệu và quy tắc đầu vào |
| Task 02 | WSL, môi trường Python, VS Code, Git và script kiểm tra |
| Task 03–04 | Model đầu vào Pydantic và kiểm thử |
| Task 05–08 | Groq, model lịch trình, sinh từ dữ liệu mẫu và xử lý lỗi |

Chưa có tool tìm kiếm, vòng lặp agent, Supervisor, Budget Optimizer hoàn chỉnh hoặc web. Không coi lịch trình mẫu là kết quả nghiên cứu du lịch thực tế.

## 2. Task 01 — Đặc tả yêu cầu du lịch

### 2.1. Quy ước sản phẩm

- Một thành phố đích mỗi chuyến: Paris, Lyon hoặc Strasbourg.
- Xuất phát từ một thành phố trong châu Âu, khác điểm đến.
- Chuyến đi dài 2–7 ngày lịch, gồm ngày đi và ngày về.
- Đếm người lớn; không có thông số trẻ em hoặc phân bổ phòng ở đầu vào hiện tại.
- Ngân sách nhận số EUR nguyên, tính cho cả nhóm và toàn chuyến đi.
- Dự kiến gồm đi/về, lưu trú, ăn uống, đi lại nội thành, vé tham quan và dự phòng 10% nằm trong tổng ngân sách. Chưa triển khai tính đủ các khoản này.
- Đích MVP: ba phương án Tiết kiệm, Cân bằng, Trải nghiệm. Nếu không đủ dữ liệu hoặc phương án khả thi, báo giới hạn thay vì tạo thêm dữ kiện.
- Chưa hỗ trợ đặt vé, đặt phòng, thanh toán, tài khoản hoặc hành trình nhiều thành phố.

### 2.2. Hợp đồng đầu vào hiện tại

Model: `TravelPreferences` trong [src/travel_planner/models.py](src/travel_planner/models.py).

| Trường | Kiểu Python | Bắt buộc | Chuẩn hóa và ràng buộc |
| --- | --- | --- | --- |
| `origin_city` | `str` | Có | Bỏ khoảng trắng hai đầu; ít nhất một ký tự; khác điểm đến khi so sánh bằng `casefold()` |
| `destination_city` | `Literal["Paris", "Strasbourg", "Lyon"]` | Có | Bỏ khoảng trắng hai đầu; phải đúng một trong ba tên |
| `departure_day` | `date` | Có | Không trước `date.today()`; nhận được chuỗi ISO hợp lệ `YYYY-MM-DD` |
| `duration_days` | `int` | Có | `2 <= value <= 7` |
| `num_adults` | `int` | Có | `value > 0`; chưa có giá trị mặc định trong model |
| `total_budget_eur` | `int` | Có | `value > 0`; chưa kiểm tra ngân sách có đủ thực hiện chuyến đi |
| `additional_preferences` | `str \| None` | Không | Mặc định `None`; bỏ khoảng trắng hai đầu; rỗng thành `None`; tối đa 1.000 ký tự sau chuẩn hóa |

**Tên trường đang dùng là `departure_day`.** Thiết kế ban đầu gọi `departure_date`; code không khai báo alias cho tên cũ. Khi tạo model, dùng tên hiện tại.

Ngày về là property, không nhập riêng:

```python
return_date = departure_day + timedelta(days=duration_days - 1)
```

`trip.return_date` không tự xuất hiện trong `model_dump()` hoặc JSON của model. Ví dụ đi ngày 18/12 trong bốn ngày thì ngày về là 21/12.

### 2.3. Ví dụ và lỗi dự kiến

Ví dụ học tập ban đầu (ngày đi chỉ hợp lệ nếu chưa qua tại lúc chạy):

```json
{
  "origin_city": "Bourges",
  "destination_city": "Strasbourg",
  "departure_day": "2026-12-18",
  "duration_days": 4,
  "num_adults": 4,
  "total_budget_eur": 800,
  "additional_preferences": "I want to visit places with a Christmas atmosphere."
}
```

Giữ các trường khác hợp lệ, thay riêng từng trường để kiểm tra:

| Thay đổi | Lý do bị từ chối |
| --- | --- |
| `duration_days = 8` | Ngoài khoảng 2–7 |
| `num_adults = 0` | Phải có ít nhất một người lớn |
| `total_budget_eur = 0` | Ngân sách phải dương |
| `origin_city = "   "` | Sau chuẩn hóa là chuỗi rỗng |
| `destination_city = "Berlin"` | Ngoài danh sách hỗ trợ |
| Ngày đi trước hôm nay | Ngày đã qua |
| Điểm xuất phát và điểm đến cùng tên | Trùng thành phố, kể cả khác hoa/thường |

Khi có nhiều vi phạm trong cùng một yêu cầu, không cam kết chỉ trả một lỗi. Bộ test dùng ngày tương đối để tránh ví dụ hết hạn.

### 2.4. Giới hạn của validation

- Chưa xác minh thành phố xuất phát có thật hoặc thuộc châu Âu.
- Chưa tự sửa `paris` thành `Paris`.
- Ngày hôm nay phụ thuộc múi giờ hệ điều hành WSL; chưa có timezone ứng dụng riêng.
- Chưa bật strict mode: một số giá trị có thể được Pydantic chuyển kiểu. Không cam kết từ chối mọi đầu vào sai kiểu hoặc mọi trường dư.
- Đúng schema không đồng nghĩa chuyến đi khả thi hoặc giá đúng thực tế.

## 3. Task 02 — Môi trường và quản lý mã nguồn

### 3.1. Thông số

| Thành phần | Giá trị |
| --- | --- |
| Máy làm việc | Windows với VS Code |
| Linux | `Ubuntu-22.04` trên WSL 2, theo kết quả terminal người học cung cấp |
| Tài khoản Linux | `quy` |
| Repository chính | `/home/quy/projects/travel-planner` |
| Bản Windows ban đầu | `D:\Project Agent Travel Planner`; không phải repository chính |
| Môi trường chuẩn | `/home/quy/projects/travel-planner/.venv` |
| Python trong `.venv` | `3.10.12`, kiểm tra lại ngày 13/11/2026 |
| pip trong `.venv` | `22.0.2`, kiểm tra lại ngày 13/11/2026 |
| Git trong WSL | `2.34.1`, kiểm tra lại ngày 13/11/2026 |
| Nhánh | `main` |
| Remote `origin` | `https://github.com/quy0901147933/TravelPlannerAgent.git` |
| Commit thiết lập ban đầu | `58ea9a8` — `chore: complete initial project setup` |

VS Code dùng extension WSL và Python của Microsoft trong Remote Extension Host. Interpreter của workspace là `.venv/bin/python`, không phải Python global `/usr/bin/python3`.

### 3.2. Mở lại dự án

Trong terminal Windows:

```powershell
wsl -d Ubuntu-22.04
```

Trong Ubuntu:

```bash
cd /home/quy/projects/travel-planner
code .
```

Trong terminal WSL của VS Code:

```bash
source .venv/bin/activate
which python
python --version
python -m pip --version
```

Đường dẫn Python mong đợi: `/home/quy/projects/travel-planner/.venv/bin/python`. Chọn cùng interpreter qua `Python: Select Interpreter` nếu VS Code chưa nhận ra.

### 3.3. Tái tạo môi trường khi cần

Không cần tạo lại môi trường đang hoạt động. Trên Ubuntu 22.04 với Python 3.10, nếu thiếu `ensurepip`, cài `python3.10-venv`:

```bash
sudo apt update
sudo apt install python3.10-venv
```

Tại gốc repository, khi cần tạo môi trường mới:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

`requirements.txt` hiện đã có từ các task sau; chưa có ở thời điểm thiết lập ban đầu. File khóa phiên bản dependency ứng dụng, không khóa hệ điều hành hoặc bản Python.

Không copy `.venv` giữa Windows và Linux; tái tạo trên hệ điều hành sẽ chạy dự án. Repository có thêm `.venv-1` tại lúc kiểm tra; tài liệu này chỉ dùng `.venv`, không xác nhận hoặc thay đổi môi trường còn lại.

### 3.4. Script kiểm tra môi trường

[check_setup.py](check_setup.py) in thông báo và `sys.executable`:

```bash
python check_setup.py
```

Kết quả đã kiểm tra lại:

```text
Travel Planner: environment is ready
Python: /home/quy/projects/travel-planner/.venv/bin/python
```

Đây là smoke check interpreter, không phải kiểm thử chức năng agent. Lưu file bằng Ctrl+S trước khi chạy; dấu chấm cạnh tab VS Code báo thay đổi chưa lưu, còn `U` là trạng thái Git chưa theo dõi.

### 3.5. Git, bảo mật và rollback

`.gitignore` hiện có:

```gitignore
.venv/
.env
.env.*
!.env.example

__pycache__/
*.py[cod]
.pytest_cache/
```

Quy tắc hiện tại không ghi riêng `.venv-1/`. Nếu dùng thêm môi trường khác, cần kiểm tra và bổ sung quy tắc trước khi stage; không mặc định mọi môi trường ảo đều được bỏ qua.

- `README.md`: cách thiết lập, sử dụng và trạng thái dự án.
- `rule.md`: quy ước phát triển, bảo mật, kiểm thử và commit.
- Kiểm tra `git status`, `git diff` và diff đã stage trước commit; chọn đúng file, giữ nguyên thay đổi không liên quan.
- Không commit API key, `.env`, mật khẩu hoặc môi trường ảo. Gitignore không tự loại file đã từng được theo dõi.
- Sau task đã kiểm tra, tạo commit; trước thay đổi lớn, đánh dấu mốc ổn định bằng tag.
- Ưu tiên `git revert` cho commit đã chia sẻ; không force-push hoặc dùng reset phá hủy dữ liệu để rollback thông thường.
- Rollback code không khôi phục model/dữ liệu dịch vụ bên ngoài. Không khẳng định LLM sẽ trả kết quả giống hệt.

Lỗi từng gặp: gõ `Ubuntu-22.4` thay vì `Ubuntu-22.04`; thiếu gói venv; chọn Python global; chưa lưu file; Git thiếu tên/email; commit khi chưa `git add`. Các bước setup hiện tại đã vượt qua lỗi interpreter; lịch sử Git xác nhận commit ban đầu thực sự tồn tại.

## 4. Chặng 2 (Task 05–08) — Đặc tả chi tiết

Ngày đối chiếu code: 13/11/2026. Phạm vi: Task 05–08.
Tài liệu mô tả hành vi đã triển khai; các giới hạn được ghi riêng, không coi prompt là bằng chứng kiểm tra.

### 1. Tổng quan

| Thành phần | Đặc tả |
| --- | --- |
| Goal | Kết nối LLM an toàn, biến dữ liệu du lịch giả lập thành lịch trình có cấu trúc, xác thực bằng Python và xử lý các lỗi dự kiến có kiểm soát. |
| Inputs | Biến môi trường GROQ_API_KEY và file JSON UTF-8 tests/fixtures/paris_sample.json. |
| Outputs | Itinerary hợp lệ, JSON in ra stdout và tổng chi phí hoạt động in riêng; lỗi dự kiến ra stderr và mã thoát 1. |
| Edge cases | Thiếu key/file, JSON sai, thiếu trường, dữ liệu ngoài giới hạn, nội dung rỗng, sai dữ liệu nguồn, timeout/kết nối/HTTP. |
| Performance constraints | Một lời gọi sinh lịch trình mỗi lần chạy hợp lệ; timeout SDK 30 giây, max_retries=0, max_completion_tokens=2048. Chưa có SLA hoặc benchmark tải. |
| Acceptance criteria | Schema hợp lệ, đối chiếu đúng dữ liệu nguồn, xử lý lỗi đúng nhánh; 46 test model và 18 test main/CLI đạt. Lần gọi thật do người học xác nhận riêng. |

Luồng: JSON mẫu → prompt + JSON Schema → Groq → chuỗi JSON → Pydantic → đối chiếu Python → hiển thị.

### 2. Phạm vi từng task

| Task | Đã triển khai | Bằng chứng và giới hạn |
| --- | --- | --- |
| 05 | Groq SDK 1.7.0, openai/gpt-oss-20b, key từ môi trường; check_groq.py | Người học xác nhận API thật phản hồi; không bật trả phí. Đây là thay đổi đã thống nhất so với lựa chọn Gemini ban đầu. |
| 06 | Activity, TripDay, Itinerary, property tổng tiền; check_itinerary.py | 46 test model gồm 20 test TravelPreferences cũ và 26 test mới. |
| 07 | generate_itinerary.py đọc fixture, gửi prompt, schema strict=False, validate JSON và đối chiếu dữ liệu bằng Counter | Người học xác nhận kết quả thật 45 EUR và kiểm tra mẫu thành công; không phải đánh giá chất lượng du lịch. |
| 08 | main() và cli(), bắt lỗi dự kiến, stderr, exit 1; test offline bằng mock | 18 test bao gồm các subTest; không gọi API thật trong bộ test. |

### 3. Inputs

| Đầu vào | Định dạng | Quy tắc hiện tại |
| --- | --- | --- |
| GROQ_API_KEY | Biến môi trường, chuỗi không rỗng | Kiểm tra tồn tại trước khi tạo client; key đúng hay không do API xác thực. Không hardcode/commit key. |
| destination_city | Chuỗi JSON | Output chỉ Paris/Lyon/Strasbourg và phải trùng fixture. |
| dates | Danh sách chuỗi YYYY-MM-DD | Output phải có ngày trùng danh sách, giữ đúng thứ tự; số ngày output 2–7. |
| activities | Danh sách object | Mỗi object có name, location, duration_minutes, estimated_cost_eur; model chọn start_time. |
| Fixture | File cố định theo đường dẫn tương đối với script | Không có schema Pydantic riêng cho input fixture; thiếu khóa/sai cấu trúc tùy ý chưa được xử lý đầy đủ. |

Fixture hiện tại: Paris; 20–21/12/2030; ba hoạt động có chi phí 30, 0 và 15 EUR cho cả nhóm.
TravelPreferences thuộc chặng trước, chưa được nối trực tiếp vào script sinh lịch trình.

### 4. Outputs và schema

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

### 5. Đối chiếu dữ liệu và edge cases

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

### 6. Performance constraints và bảo mật

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

### 7. Acceptance criteria

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

### 8. File và cách kiểm chứng

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

### 9. Ngoài phạm vi Chặng 2

Chưa có nghiên cứu Tavily, nguồn giá thực, tool calling, vòng lặp agent, Supervisor, Evaluator đầy đủ, ba phương án tối ưu, Streamlit, đặt dịch vụ hoặc triển khai production.
Prompt chưa tách ra prompts/ theo cấu trúc dài hạn của rule.md. Bộ xử lý lỗi chưa cam kết bắt lỗi lập trình hoặc fixture có cấu trúc tùy ý.

## 5. Kiểm chứng và cách chạy lại

Xác minh trực tiếp ngày **13/11/2026** trong WSL, dùng `.venv`:

| Kiểm tra | Kết quả |
| --- | --- |
| `check_setup.py` | Chạy được; đúng interpreter của dự án |
| `tests/test_models.py` | 46 test, OK; gồm 20 phương thức test TravelPreferences |
| `tests/test_generate_itinerary.py` | 18 test, OK; mock API |
| Tổng offline | 64 test đạt; không phải 64 lời gọi API |
| `python -m pip check` | Không phát hiện dependency xung đột |
| `git diff --check` trước viết SPEC | Không báo lỗi |

Chạy lại từ gốc repository:

```bash
source .venv/bin/activate
python check_setup.py
PYTHONPATH=src:. python -m unittest discover -s tests -p test_models.py -v
PYTHONPATH=src:. python -m unittest discover -s tests -p test_generate_itinerary.py -v
python -m pip check
```

Không chạy discovery toàn bộ `tests/` khi chỉ muốn offline: `tests/test_api.py` là script gọi API thủ công, không thuộc bộ test offline. File này đã được phiên khác đưa vào commit `66f4e4d`; công việc hiện tại không sửa nội dung file.

Các dependency chính được khóa hiện tại: Pydantic `2.14.3`, Groq SDK `1.7.0`, HTTPX `0.28.1`; toàn bộ phiên bản trực tiếp/gián tiếp xem [requirements.txt](requirements.txt). Không nâng phiên bản trong công việc viết SPEC.

SPEC này là bản ghi trạng thái, không tự tạo thêm tính năng. Khi thay tên trường, model, prompt, dependency hoặc quy tắc kiểm tra, cập nhật code, test, README và phần SPEC liên quan cùng nhau.
