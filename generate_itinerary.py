import sys
import os
import json
from pathlib import Path 
from groq import(
    Groq,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)

from pydantic import ValidationError
from travel_planner.models import Itinerary

def main():
    if not os.getenv("GROQ_API_KEY"):
       raise ValueError("Pas encore configurer GROQ_API_KEY")
    
    root = Path(__file__).resolve().parent

    sample = json.loads(
        (root / "tests/fixtures/paris_sample.json").read_text(encoding="utf-8")
    )

    client = Groq(timeout=30.0, max_retries=0)
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
        {
            "role": "system",
            "content": (
                "Bạn tạo lịch trình từ dữ liệu giả lập. "
                "Chỉ dùng các ngày và hoạt động được cung cấp. "
                "Dùng mỗi hoạt động đúng một lần, giữ nguyên tên, địa điểm, "
                "thời lượng và chi phí. Mỗi ngày có ít nhất một hoạt động. "
                "Tự chọn giờ bắt đầu hợp lý, không chồng giờ. "
                "Chỉ trả về JSON theo schema được yêu cầu."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(sample, ensure_ascii=False),
        },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "itinerary",
                "strict": False,
                "schema": Itinerary.model_json_schema(),
            },
        },
        max_completion_tokens=2048,
    )
    content = response.choices[0].message.content

    if not content:
       raise ValueError("Model ne retourne pas contenu")
    trip = Itinerary.model_validate_json(content)

    from collections import Counter

    if trip.destination_city != sample["destination_city"]:
       raise ValueError("Destination d'arrive n'est pas vrai selon sample")
    if [day.date.isoformat() for day in trip.days] != sample["dates"]:
       raise ValueError("Date n'est pas vrai selon sample")

    expected = Counter(
    (
        activity["name"],
        activity["location"],
        activity["duration_minutes"],
        activity["estimated_cost_eur"],
    )
    for activity in sample["activities"]
    )

    actual = Counter(
    (
        activity.name,
        activity.location,
        activity.duration_minutes,
        activity.estimated_cost_eur,
    )
    for day in trip.days
    for activity in day.activities
    )

    if actual != expected:
        raise ValueError("Activity in the data sample isn't available , check again !")

    print("Task 07: Success check sample data")

    print(trip.model_dump_json(indent=2))
    print("Total cost: ", trip.total_estimated_cost_eur)


def cli():
    try:
      main()
    except FileNotFoundError:
      print("Error: Don't find data sample", file=sys.stderr)
      sys.exit(1)
    except APITimeoutError:
      print("Error: Groq reponse time out", file=sys.stderr)
      sys.exit(1)
    except APIConnectionError:
      print("Error: Can not connect API", file=sys.stderr)
      sys.exit(1)
    except json.JSONDecodeError:
      print("Error: Data sample is incorrect JSON", file=sys.stderr)
      sys.exit(1)
    except APIStatusError as error:
      if error.status_code == 401:
         message = "API key is invalide and is recalled"
      elif error.status_code == 403:
         message = "The request is rejected authentication"
      elif error.status_code == 429:
         message = "The API call limit has been reached."
      else:
         message = f"Groq return HTTP {error.status_code}."   

      print(f"Error: {message}", file=sys.stderr)
      sys.exit(1)

    except ValidationError:
      print(
        "Lỗi: Đầu ra model không phải JSON hợp lệ "
        "hoặc không đúng schema Itinerary.",
        file=sys.stderr,
      )
      sys.exit(1)
    except ValueError as error:
      print(f"Error: {error}", file=sys.stderr)
      sys.exit(1)


if __name__ == '__main__':
    cli()
