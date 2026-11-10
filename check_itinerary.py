from travel_planner.models import Itinerary

trip = Itinerary.model_validate({
    "title": "Khám phá Paris",
    "destination_city": "Paris",
    "days": [
        {
            "date": "2026-12-20",
            "activities": [
                {
                    "name": "Tham quan bảo tàng",
                    "location": "Paris",
                    "start_time": "09:00",
                    "duration_minutes": 120,
                    "estimated_cost_eur": 30,
                }
            ],
        },
        {
            "date": "2026-12-21",
            "activities": [
                {
                    "name": "Đi dạo",
                    "location": "Paris",
                    "start_time": "10:00",
                    "duration_minutes": 60,
                    "estimated_cost_eur": 0,
                }
            ],
        },
    ],
})

assert len(trip.days) == 2
assert trip.total_estimated_cost_eur == 30.0

print(trip.model_dump_json(indent=2))
print("Tổng chi phí:", trip.total_estimated_cost_eur)
print("Kiểm tra OK")