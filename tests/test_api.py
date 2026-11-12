import os
import urllib.request
import urllib.error

key = os.getenv("GROQ_API_KEY")
if not key:
    raise SystemExit("Chưa có GROQ_API_KEY trong terminal này.")

request = urllib.request.Request(
    "https://api.groq.com/openai/v1/models",
    headers={
    "Authorization": f"Bearer {key}",
    "User-Agent": "travel-planner-dev/0.1",
    "Accept": "application/json",
    },
)

try:
    with urllib.request.urlopen(request, timeout=15) as response:
        print(f"HTTP {response.status}: Groq đã chấp nhận API key.")
except urllib.error.HTTPError as error:
    print(error.read().decode("utf-8"))
    if error.code == 401:
        print("HTTP 401: Key không hợp lệ hoặc đã bị thu hồi.")
    else:
        print(f"HTTP {error.code}: Chưa xác minh thành công; cần kiểm tra thêm.")
except urllib.error.URLError:
    print("Không kết nối được Groq. Kiểm tra mạng rồi thử lại.")