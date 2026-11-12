# SPEC — Chặng 1: đầu vào và nền tảng Python

Ngày đối chiếu code và kiểm thử: **13/11/2026**. Phạm vi: **Task 01–04**, trọng tâm `TravelPreferences` (Task 03) và kiểm thử đầu vào (Task 04).

Đây là đặc tả hành vi đã triển khai, kèm giới hạn chưa triển khai; không phải cam kết toàn bộ MVP đã hoạt động. Code hiện có thêm Chặng 2 (Task 05–08), nhưng các model lịch trình, Groq và CLI của Chặng 2 không thuộc tiêu chí nghiệm thu tài liệu này.

## 1. Bảng đặc tả tổng quan

| Thành phần | Đặc tả Chặng 1 | Bằng chứng / giới hạn |
| --- | --- | --- |
| **Goal — mục tiêu cấp cao** | Biến yêu cầu chuyến đi thành dữ liệu có cấu trúc, chuẩn hóa và kiểm tra được bằng Python trước khi chuyển cho LLM hoặc agent. Người học hiểu đầu vào, validation và kiểm thử tự động. | Task 01 xác định yêu cầu; Task 02 chuẩn bị môi trường; Task 03 xây model; Task 04 kiểm chứng hành vi. |
| **Inputs — định dạng đầu vào** | Dictionary Python truyền bằng `TravelPreferences(**data)`; sáu trường bắt buộc và một trường tùy chọn. Ngày nhận `date` hoặc chuỗi ISO hợp lệ `YYYY-MM-DD`. | Bảng trường chi tiết ở mục 3. Tên thực tế là `departure_day`, không phải `departure_date`. |
| **Outputs — định dạng đầu ra** | Thành công: đối tượng `TravelPreferences` đã chuẩn hóa, có `return_date` được tính khi truy cập. Thất bại: `pydantic.ValidationError` có vị trí và loại lỗi. | Không trả lịch trình, giá vé, phòng hay ba phương án du lịch trong Chặng 1. |
| **Edge cases — trường hợp biên** | Ngày hôm nay/quá khứ, 1–2–7–8 ngày, số người và ngân sách bằng 0/âm/tối thiểu 1, chuỗi rỗng/khoảng trắng, sở thích 1.000/1.001 ký tự, cùng thành phố khác hoa–thường, ngày về qua tháng/năm. | 20 phương thức kiểm thử của `TestTravelPreferences`; một phương thức có thể chứa nhiều `subTest`. |
| **Performance constraints — ràng buộc hiệu năng** | Validation và tính ngày về chạy cục bộ; không cần key, mạng, LLM hoặc dịch vụ ngoài. Không retry, tìm kiếm hay vòng lặp agent trong Chặng 1. Sở thích sau chuẩn hóa tối đa 1.000 ký tự. | Chưa đặt hoặc đo SLA latency, throughput, RAM hay tải đồng thời; không coi thời gian chạy test là benchmark. Chưa có giới hạn độ dài tên thành phố, số người hoặc ngân sách tối đa. |
| **Acceptance criteria — tiêu chí nghiệm thu** | Toàn bộ AC01–AC20 ở mục 6 phải đạt bằng test offline. Môi trường và lệnh chạy được ghi để có thể kiểm tra lại. | Ngày 13/11/2026: 20/20 test đầu vào đạt; 46 test model và 18 test CLI/tạo lịch trình cũng đạt, nhưng 44 test còn lại thuộc Chặng 2. |

## 2. Kết quả từng task

| Task | Mục tiêu | Sản phẩm đã có | Trạng thái |
| --- | --- | --- | --- |
| 01 — Thiết kế đầu vào | Xác định dữ liệu cần hỏi, quy tắc hợp lệ và phạm vi chuyến đi. | Bảy trường đầu vào, ngân sách EUR cho cả nhóm, thời lượng gồm ngày đi và ngày về; ngày về không nhập riêng. | Hoàn thành thiết kế; quy tắc xuất phát trong châu Âu chưa được xác minh bằng code. |
| 02 — Chuẩn bị dự án | Có môi trường Python và quản lý phiên bản để học và phát triển. | Dự án `/home/quy/projects/travel-planner`, Ubuntu WSL 2, `.venv`, Git, `.gitignore`, README, rule và dependency đã ghi trong `requirements.txt`. | Đã thiết lập; trạng thái push cần kiểm tra qua Git, không suy ra từ việc có commit cục bộ. |
| 03 — Xây TravelPreferences | Mô hình hóa, chuẩn hóa và từ chối dữ liệu vi phạm quy tắc. | `src/travel_planner/models.py`: fields, field validators, model validator và property `return_date`. | Hoàn thành trong giới hạn mục 8. |
| 04 — Kiểm thử đầu vào | Chứng minh dữ liệu đúng/sai và các giá trị biên được xử lý như mong muốn. | `tests/test_models.py`, class `TestTravelPreferences`: 20 test offline bằng `unittest`. | 20/20 đạt khi đối chiếu 13/11/2026. |

Phạm vi MVP làm bối cảnh: Paris/Lyon/Strasbourg, một điểm đến mỗi chuyến, 2–7 ngày, người lớn, ngân sách EUR cho cả nhóm gồm đi/về và chi phí trong chuyến. Ba phương án Tiết kiệm/Cân bằng/Trải nghiệm, giá có nguồn, không đặt vé/phòng/thanh toán là mục tiêu sản phẩm về sau, chưa phải đầu ra Chặng 1.

## 3. Inputs — hợp đồng dữ liệu

| Trường | Kiểu sau validation | Bắt buộc / mặc định | Quy tắc đã thực thi |
| --- | --- | --- | --- |
| `origin_city` | `str` | Bắt buộc | Bỏ khoảng trắng hai đầu bằng `strip()`; độ dài ít nhất 1; không trùng điểm đến khi so sánh bằng `casefold()`. Chưa xác minh thành phố có thật hoặc thuộc châu Âu. |
| `destination_city` | `Literal["Paris", "Strasbourg", "Lyon"]` | Bắt buộc | Bỏ khoảng trắng hai đầu, sau đó phải đúng một trong ba tên và đúng chữ hoa–thường. |
| `departure_day` | `datetime.date` | Bắt buộc | Pydantic kiểm tra/chuyển kiểu trước; validator từ chối ngày nhỏ hơn `date.today()`. Ngày hôm nay hợp lệ. |
| `duration_days` | `int` | Bắt buộc | Từ 2 đến 7, gồm cả hai biên. Đếm ngày đi là ngày đầu. |
| `num_adults` | `int` | Bắt buộc | Lớn hơn 0, tức ít nhất 1 người lớn. |
| `total_budget_eur` | `int` | Bắt buộc | Lớn hơn 0; EUR nguyên cho cả nhóm. 1 EUR hợp lệ về cấu trúc, chưa chứng minh đủ chi phí chuyến đi. |
| `additional_preferences` | `str` hoặc `None` | Tùy chọn, mặc định `None` | Bỏ khoảng trắng hai đầu; chuỗi rỗng sau chuẩn hóa trở thành `None`; chuỗi còn nội dung dài tối đa 1.000 ký tự sau chuẩn hóa. |

**Ví dụ đầu vào** (ngày tạo tương đối để không hết hạn):

```python
from datetime import date, timedelta
from travel_planner.models import TravelPreferences

data = {
    "origin_city": "  Bourges  ",
    "destination_city": "  Paris  ",
    "departure_day": (date.today() + timedelta(days=10)).isoformat(),
    "duration_days": 3,
    "num_adults": 2,
    "total_budget_eur": 300,
    "additional_preferences": "  Thích bảo tàng và đi bộ  ",
}
trip = TravelPreferences(**data)
```

Đầu vào là dictionary Python; ngày dạng chuỗi ISO ở ví dụ mô phỏng dữ liệu văn bản. Chặng 1 chưa cung cấp HTTP endpoint hoặc form UI. Không bật strict mode: không được suy diễn rằng mọi giá trị sai kiểu ban đầu đều bị từ chối; Pydantic có thể ép một số kiểu sang kiểu đầu ra.

## 4. Outputs — kết quả và lỗi

| Tình huống | Định dạng / cách đọc | Ý nghĩa |
| --- | --- | --- |
| Hợp lệ | Đối tượng `TravelPreferences`; đọc `trip.origin_city`, `trip.departure_day`, v.v. | Bảy trường đã chuẩn hóa và kiểm tra. Với ví dụ trên, tên thành phố là `Bourges`/`Paris`, sở thích bỏ khoảng trắng và ngày có kiểu `date`. |
| Ngày về | `trip.return_date` có kiểu `date` | `departure_day + timedelta(days=duration_days - 1)`. Đi 3 ngày thì ngày về cách ngày đi 2 ngày. Không cần gọi `()` hoặc nhập ngày về. |
| Dictionary đầu ra | `trip.model_dump()` | Bảy trường của model; ngày vẫn là đối tượng Python `date`. Property `return_date` không tự được đưa vào dictionary. |
| JSON đầu ra nếu cần | `trip.model_dump_json()` | Pydantic có thể serialize các trường sang chuỗi JSON; ngày thành chuỗi. Đây không phải API riêng của ứng dụng và chưa có test serialize riêng cho TravelPreferences trong 20 test Chặng 1. |
| Không hợp lệ | `ValidationError`; đọc `.errors()` | Danh sách thông tin lỗi. Kiểm thử tập trung vào `loc` và một số `type`, không cố định toàn bộ thông báo tiếng Anh của thư viện. |

| Ví dụ lỗi | `loc` mong đợi | Loại lỗi / giải thích |
| --- | --- | --- |
| 9 ngày | `("duration_days",)` | Vi phạm giới hạn lớn nhất 7. |
| Ngày đã qua, kể cả chuỗi ISO | `("departure_day",)` | `type="value_error"` khi validator chủ động `raise ValueError(...)`. |
| Chuỗi không phải ngày, ngày không tồn tại hoặc `None` | `("departure_day",)` | Pydantic phải trả ValidationError về ngày; không để TypeError do so sánh chuỗi/None với date thoát ra. |
| Điểm đến Berlin | `("destination_city",)` | Không thuộc Literal ba điểm đến. |
| Xuất phát PARIS, đến Paris | `()` | Lỗi toàn model do quan hệ giữa hai trường, không gán cho riêng một trường. |

Luồng ngày: đầu vào → Pydantic chuyển thành `date` → field validator kiểm tra không trong quá khứ → model validator kiểm tra hai thành phố. Model validator `mode="after"` chỉ chạy khi các trường đã hợp lệ.

## 5. Edge cases — bảng trường hợp biên

| Nhóm | Đầu vào / trường hợp | Kết quả mong đợi | Đã kiểm thử |
| --- | --- | --- | --- |
| Thời lượng | 1 và 8 | Từ chối tại duration_days | Có |
| Thời lượng | Mọi giá trị nguyên 2–7 | Chấp nhận; ngày về đúng | Có |
| Số người | 0, -1 / 1 | Từ chối / chấp nhận | Có |
| Ngân sách | 0, -100 / 1 | Từ chối / chấp nhận | Có |
| Ngày | Hôm nay | Chấp nhận | Có |
| Ngày | Ngày quá khứ dạng date và ISO | Từ chối tại departure_day | Có |
| Ngày | ISO hợp lệ trong tương lai | Chuyển sang date và chấp nhận | Có |
| Ngày | `not-a-date`, `2030-02-30`, chuỗi rỗng, None | ValidationError tại departure_day | Có |
| Điểm xuất phát | Chuỗi rỗng hoặc chỉ dấu cách | Từ chối sau strip | Có |
| Điểm đến | Paris, Lyon, Strasbourg | Chấp nhận | Có |
| Điểm đến | Berlin, Moscow, London, chuỗi rỗng, dấu cách | Từ chối | Có |
| Trùng thành phố | Paris / PARIS / Paris có khoảng trắng so với Paris | Từ chối toàn model | Có |
| Chuẩn hóa thành phố | Bourges/Paris có khoảng trắng hai đầu | Giữ tên sau strip | Có |
| Sở thích | Bỏ trường / None / rỗng / dấu cách / tab, xuống dòng | None | Có |
| Sở thích | Văn bản có khoảng trắng hai đầu | Bỏ khoảng trắng, giữ nội dung | Có |
| Sở thích | 1.000 / 1.001 chữ a | Chấp nhận / từ chối | Có |
| Ngày về | 31/01, chuyến 3 ngày | 02/02 cùng năm | Có, năm tương lai |
| Ngày về | 31/12, chuyến 3 ngày | 02/01 năm sau | Có, năm tương lai |

## 6. Acceptance criteria — tiêu chí nghiệm thu và test tương ứng

Mỗi hàng dưới đây tương ứng một phương thức thuộc `TestTravelPreferences` trong `tests/test_models.py`. Trạng thái khi đối chiếu: **tất cả đạt**.

| ID | Tiêu chí nghiệm thu | Test bằng chứng |
| --- | --- | --- |
| AC01 | Tạo được chuyến hợp lệ, giữ đúng dữ liệu, sở thích mặc định None, ngày về đúng. | `test_valid_input` |
| AC02 | Từ chối 1 và 8 ngày; lỗi chỉ tại duration_days. | `test_rejection_invalid_duration` |
| AC03 | Chấp nhận từng số ngày 2–7, tính đúng ngày về từng lượt subTest. | `test_accept_valid_duration` |
| AC04 | Từ chối 0 và -1 người; lỗi chỉ tại num_adults. | `test_reject_invalid_num_adults` |
| AC05 | Từ chối ngân sách 0 và -100; lỗi chỉ tại total_budget_eur. | `test_reject_invalid_budget` |
| AC06 | Từ chối ngày quá khứ dạng date. | `test_reject_past_departure` |
| AC07 | Từ chối cùng thành phố, không phân biệt hoa–thường và khoảng trắng hai đầu; lỗi toàn model. | `test_reject_same_cities` |
| AC08 | Từ chối điểm xuất phát rỗng hoặc chỉ dấu cách. | `test_empty_origin_city` |
| AC09 | Từ chối điểm đến ngoài phạm vi và điểm đến rỗng. | `test_reject_invalid_destination` |
| AC10 | Sở thích rỗng, dấu cách, tab/xuống dòng hoặc None thành None. | `test_normalize_empty_additional_preferences` |
| AC11 | Sở thích 1.000 ký tự được giữ, 1.001 ký tự bị từ chối đúng trường. | `test_preferences_limit_length` |
| AC12 | Ngày đi hôm nay hợp lệ và ngày về đúng. | `test_accept_departure_today` |
| AC13 | Cả Paris, Lyon và Strasbourg đều được chấp nhận. | `test_accept_supported_destinations` |
| AC14 | Bỏ khoảng trắng hai đầu tên xuất phát và điểm đến. | `test_strip_city_names` |
| AC15 | Bỏ khoảng trắng hai đầu sở thích và giữ nội dung. | `test_strip_preferences` |
| AC16 | Chấp nhận 1 người và tổng ngân sách 1 EUR. | `test_accept_minimum_adults_and_budget` |
| AC17 | Ngày về đúng khi đi qua cuối tháng và cuối năm. | `test_return_date_across_boundaries` |
| AC18 | Chuyển ngày tương lai dạng ISO sang date, giữ đúng ngày và ngày về. | `test_accept_departure_iso_string` |
| AC19 | Ngày sai/rỗng/None tạo ValidationError đúng trường. | `test_reject_invalid_departure_values` |
| AC20 | Chuỗi ISO ngày quá khứ tạo lỗi tại departure_day với type value_error. | `test_reject_past_departure_iso_string` |

## 7. Cách xác minh và ràng buộc hiệu năng

Chạy trong Ubuntu WSL tại dự án chính, không cần API key:

```bash
cd /home/quy/projects/travel-planner
source .venv/bin/activate
PYTHONPATH=src:.:tests python -m unittest test_models.TestTravelPreferences -v
```

Lệnh này chọn đúng **20 test Chặng 1**, kể cả khi file test_models.py có thêm test Chặng 2. Kết quả nghiệm thu mong đợi: `Ran 20 tests` và `OK`.

Kiểm tra hồi quy offline hiện có của cả dự án:

```bash
PYTHONPATH=src:. python -m unittest discover -s tests -p test_models.py -v
PYTHONPATH=src:. python -m unittest discover -s tests -p test_generate_itinerary.py -v
python -m pip check
```

Kết quả đối chiếu 13/11/2026: 46 test model + 18 test tạo lịch trình/CLI = **64 test offline đạt**. Không chạy discovery không lọc: `tests/test_api.py` là script mạng thủ công và chạy khi import; không thuộc test offline Chặng 1. Không gọi Groq/Tavily để nghiệm thu Chặng 1.

| Ràng buộc | Tình trạng |
| --- | --- |
| Không phụ thuộc dịch vụ ngoài khi kiểm tra đầu vào | Đã đáp ứng; 20 test chạy cục bộ không cần API key. |
| Không phát sinh chi phí LLM từ Chặng 1 | Không có lời gọi LLM trong model và test đầu vào. |
| Chặn sở thích sau chuẩn hóa vượt 1.000 ký tự | Đã có Field max_length và test hai biên; không phải giới hạn kích thước request thô trước xử lý. |
| Thời gian phản hồi, RAM, tải đồng thời | Chưa có mục tiêu định lượng hoặc benchmark; không công bố số hiệu năng từ thời gian unittest. |
| Khả năng tái chạy | Dependency ghi trong requirements.txt; test ngày dùng thời gian tương đối. Kết quả vẫn phụ thuộc ngày/múi giờ hệ điều hành. |

## 8. Giới hạn và phần chưa nghiệm thu

| Nội dung | Trạng thái / tác động |
| --- | --- |
| Xác minh điểm xuất phát trong châu Âu | Chưa có dữ liệu địa lý hoặc validator thực thi. Tên không rỗng không đồng nghĩa là thành phố hợp lệ. |
| Kiểm tra ngân sách đủ cho chuyến đi | Chưa làm ở Chặng 1. Chưa cộng vé, lưu trú, ăn uống, dự phòng 10% hoặc kiểm chứng giá. |
| Ba phương án, tìm kiếm nguồn, agent, web, đặt dịch vụ | Ngoài phạm vi nghiệm thu Chặng 1. |
| Tên departure_date trong thiết kế cũ | Code dùng departure_day. Không có alias; người dùng code phải dùng tên thực tế. |
| Kiểu dữ liệu nghiêm ngặt | Chưa bật strict mode; chưa có test phủ mọi trường hợp bool, số thực, chuỗi số hoặc ép kiểu. |
| Trường dư, thay đổi thuộc tính sau khi tạo | Chưa định nghĩa chính sách riêng hoặc có test nghiệm thu; không cam kết cấm sửa hay tự validation lại mỗi lần gán. |
| Ngày giới hạn datetime, múi giờ nghiệp vụ | Chưa xử lý date.max/overflow và chưa cố định timezone riêng cho ứng dụng. date.today() lấy ngày hệ điều hành. |
| Bao phủ còn thiếu | Chưa có test đầu vào thiếu từng trường bắt buộc, serialize riêng TravelPreferences, năm nhuận hoặc fuzz/property-based. 20 test đạt không có nghĩa bao phủ mọi dữ liệu có thể nhập. |
| Chặng 2 trong cùng repo | Activity/TripDay/Itinerary, Groq và CLI có đặc tả/kiểm thử riêng; không được tính là thành quả Task 03–04. |

## 9. Kết luận nghiệm thu Chặng 1

Task 03 tạo được lớp dữ liệu đầu vào có chuẩn hóa và ràng buộc rõ; Task 04 cung cấp 20 test hồi quy kiểm chứng các quy tắc và trường hợp biên đã liệt kê. Có thể dùng TravelPreferences làm đầu vào cho các chặng tiếp theo trong các giới hạn trên. SPEC ghi hành vi hiện có, không tự mở rộng kiến trúc hoặc bổ sung tính năng chưa được triển khai.
