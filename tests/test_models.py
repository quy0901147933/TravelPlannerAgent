import unittest
from datetime import date , timedelta
from pydantic import ValidationError
from travel_planner.models import TravelPreferences

class TestTravelPreferences(unittest.TestCase):
    def test_valid_input(self):
        departure = date.today() + timedelta(days=10)
        data = {
            "duration_days" : 3,
            "origin_city" : "Bourges",
            "destination_city" : "Paris",
            "departure_day" : departure,
            "num_adults" : 2,
            "total_budget_eur" : 300,
        }
        trip = TravelPreferences(**data)
        self.assertEqual(trip.duration_days , 3)
        self.assertEqual(trip.origin_city , "Bourges")
        self.assertEqual(trip.destination_city , "Paris")
        self.assertEqual(trip.departure_day , departure)
        self.assertEqual(trip.num_adults , 2)
        self.assertEqual(trip.total_budget_eur , 300)
        self.assertIsNone(trip.additional_preferences)
        self.assertEqual(trip.return_date , departure + timedelta(days=2))
    def test_rejection_invalid_duration(self):
        departure = date.today() + timedelta(days=10)
        data = {
                "duration_days" : 3,
                "origin_city" : "Bourges",
                "destination_city" : "Paris",
                "departure_day" : departure,
                "num_adults" : 2,
                "total_budget_eur" : 300,
        }
        for invalid_days in (1 , 8):
            with self.subTest(duration_days = invalid_days):
                data["duration_days"] = invalid_days
                with self.assertRaises(ValidationError) as caught:
                    TravelPreferences(**data)
                self.assertEqual(
                    [error["loc"] for error in caught.exception.errors()],
                    [("duration_days",)]
                )
    def test_accept_valid_duration(self):
        departure = date.today() + timedelta(days=10)
        data = {
                "duration_days" : 3,
                "origin_city" : "Bourges",
                "destination_city" : "Paris",
                "departure_day" : departure,
                "num_adults" : 2,
                "total_budget_eur" : 300,
        }
        for valid_days in range(2,8):
            with self.subTest(duration_days = valid_days):
                data["duration_days"] = valid_days
                trip = TravelPreferences(**data)
                self.assertEqual(trip.duration_days , valid_days)
                self.assertEqual(trip.return_date , departure + timedelta(days=valid_days - 1))

    def test_reject_invalid_num_adults(self):
        departure = date.today() + timedelta(days=10)
        data = {
                "duration_days" : 3,
                "origin_city" : "Bourges",
                "destination_city" : "Paris",
                "departure_day" : departure,
                "num_adults" : 2,
                "total_budget_eur" : 300,
        }
        for invalid_num in (0 , -1):
            with self.subTest(num_adults = invalid_num):
                data["num_adults"] = invalid_num
                with self.assertRaises(ValidationError) as caught:
                    TravelPreferences(**data)
                self.assertEqual(
                    [error["loc"] for error in caught.exception.errors()],
                    [("num_adults",)],
                )
    def test_reject_invalid_budget(self):
        departure = date.today() + timedelta(days=10)
        data = {
                "duration_days" : 3,
                "origin_city" : "Bourges",
                "destination_city" : "Paris",
                "departure_day" : departure,
                "num_adults" : 2,
                "total_budget_eur" : 300,
        }

        for invalid_budget in (0 , -100):
            with self.subTest(total_budget_eur = invalid_budget):
                data["total_budget_eur"] = invalid_budget
                with self.assertRaises(ValidationError) as caught:
                    TravelPreferences(**data)
                self.assertEqual(
                    [error["loc"] for error in caught.exception.errors()],
                    [("total_budget_eur",)],
                )
    def test_reject_past_departure(self):
        departure = date.today() - timedelta(days=10)
        data = {
                "duration_days" : 3,
                "origin_city" : "Bourges",
                "destination_city" : "Paris",
                "departure_day" : departure,
                "num_adults" : 2,
                "total_budget_eur" : 300,
        }

        with self.assertRaises(ValidationError) as caught:
            TravelPreferences(**data)

        self.assertEqual(
            [error["loc"] for error in caught.exception.errors()],
            [("departure_day",)],
        )
    def test_reject_same_cities(self):
        departure = date.today() + timedelta(days=10)
        data = {
                "duration_days" : 3,
                "origin_city" : "Paris",
                "destination_city" : "Paris",
                "departure_day" : departure,
                "num_adults" : 2,
                "total_budget_eur" : 300,
        }
        for origin in ("Paris", "PARIS", "  Paris  "):
            with self.subTest(origin_city=origin):
                data["origin_city"] = origin
                with self.assertRaises(ValidationError) as caught:
                    TravelPreferences(**data)
                self.assertEqual(
                    [error["loc"] for error in caught.exception.errors()],
                    [()],
                )

    def test_empty_origin_city(self):
        departure = date.today() + timedelta(days=10)
        data = {
                "duration_days" : 3,
                "origin_city" : "Bourges",
                "destination_city" : "Paris",
                "departure_day" : departure,
                "num_adults" : 2,
                "total_budget_eur" : 300,
        }
        for invalid_value in ("", " "):
            with self.subTest(origin_city = invalid_value):
                data["origin_city"] = invalid_value

                with self.assertRaises(ValidationError) as caught:
                    TravelPreferences(**data)

                self.assertEqual(
                    [error["loc"] for error in caught.exception.errors()],
                    [("origin_city",)],
                )
    def test_reject_invalid_destination(self):
        departure = date.today() + timedelta(days=10)
        data = {
                "duration_days" : 3,
                "origin_city" : "Bourges",
                "destination_city" : "Paris",
                "departure_day" : departure,
                "num_adults" : 2,
                "total_budget_eur" : 300,
        }
        for invalid_value in ("Berlin" , "Moscow" , "London" , " " , ""):
            with self.subTest(destination_city = invalid_value):
                data["destination_city"] = invalid_value

                with self.assertRaises(ValidationError) as caught:
                    TravelPreferences(**data)

                self.assertEqual(
                    [error["loc"] for error in caught.exception.errors()],
                    [("destination_city",)],
                )
    def test_normalize_empty_additional_preferences(self):
        departure = date.today() + timedelta(days=10)
        data = {
                "duration_days" : 3,
                "origin_city" : "Bourges",
                "destination_city" : "Paris",
                "departure_day" : departure,
                "num_adults" : 2,
                "total_budget_eur" : 300,
        }
        for invalid_value in ("", "  ", "\t\n", None):
            with self.subTest(additional_preferences = invalid_value):
                data["additional_preferences"] = invalid_value
                trip = TravelPreferences(**data)
                self.assertIsNone(trip.additional_preferences)
    def test_preferences_limit_length(self):
        departure = date.today() + timedelta(days=10)
        data = {
                "duration_days" : 3,
                "origin_city" : "Bourges",
                "destination_city" : "Paris",
                "departure_day" : departure,
                "num_adults" : 2,
                "total_budget_eur" : 300,
        }
        with self.subTest(length=1000):
            data["additional_preferences"] = 'a' * 1000
            trip = TravelPreferences(**data)
            self.assertEqual(trip.additional_preferences , 'a' * 1000)

        with self.subTest(length=1001):
            data["additional_preferences"] = 'a' * 1001
            with self.assertRaises(ValidationError) as caught:
                TravelPreferences(**data)
            self.assertEqual(
                [error["loc"] for error in caught.exception.errors()],
                [("additional_preferences",)],
            )
    def test_accept_departure_today(self):
        today = date.today()

        data = {
            "origin_city": "Bourges",
            "destination_city": "Paris",
            "departure_day": today,
            "duration_days": 3,
            "num_adults": 2,
            "total_budget_eur": 300,
        }

        trip = TravelPreferences(**data)

        self.assertEqual(trip.departure_day, today)
        self.assertEqual(
            trip.return_date,
            today + timedelta(days=2),
        )
    def test_accept_supported_destinations(self):
        data = {
            "origin_city": "Bourges",
            "destination_city": "Paris",
            "departure_day": date.today() + timedelta(days=10),
            "duration_days": 3,
            "num_adults": 2,
            "total_budget_eur": 300,
        }

        for destination in ("Paris", "Lyon", "Strasbourg"):
            with self.subTest(destination_city=destination):
                data["destination_city"] = destination

                trip = TravelPreferences(**data)

                self.assertEqual(
                    trip.destination_city,
                    destination,
                )
    def test_strip_city_names(self):
        data = {
            "origin_city": "  Bourges  ",
            "destination_city": "  Paris  ",
            "departure_day": date.today() + timedelta(days=10),
            "duration_days": 3,
            "num_adults": 2,
            "total_budget_eur": 300,
        }

        trip = TravelPreferences(**data)

        self.assertEqual(trip.origin_city, "Bourges")
        self.assertEqual(trip.destination_city, "Paris")
    def test_strip_preferences(self):
        data = {
            "origin_city": "Bourges",
            "destination_city": "Paris",
            "departure_day": date.today() + timedelta(days=10),
            "duration_days": 3,
            "num_adults": 2,
            "total_budget_eur": 300,
            "additional_preferences": "  Thích bảo tàng và đi bộ  ",
        }

        trip = TravelPreferences(**data)

        self.assertEqual(
            trip.additional_preferences,
            "Thích bảo tàng và đi bộ",
        )
    def test_accept_minimum_adults_and_budget(self):
        data = {
            "origin_city": "Bourges",
            "destination_city": "Paris",
            "departure_day": date.today() + timedelta(days=10),
            "duration_days": 3,
            "num_adults": 1,
            "total_budget_eur": 1,
        }

        trip = TravelPreferences(**data)

        self.assertEqual(trip.num_adults, 1)
        self.assertEqual(trip.total_budget_eur, 1)
    def test_return_date_across_boundaries(self):
        future_year = date.today().year + 1
        case = (
            (
                date(future_year , 1 , 31),
                date(future_year , 2 , 2),
            ),
            (
                date(future_year , 12 , 31),
                date(future_year + 1 , 1 , 2),
            ),
        )
        for departure , expected_return in case:
            with self.subTest(departure_day = departure):
                data = {
                    "origin_city": "Bourges",
                    "destination_city": "Paris",
                    "departure_day": departure,
                    "duration_days": 3,
                    "num_adults": 2,
                    "total_budget_eur": 300,
                }
                trip = TravelPreferences(**data)
                self.assertEqual(trip.return_date , expected_return)

    def test_accept_departure_iso_string(self):
        departure = date.today() + timedelta(days=10)
        data = {
            "origin_city": "Bourges",
            "destination_city": "Paris",
            "departure_day": departure.isoformat(),
            "duration_days": 3,
            "num_adults": 2,
            "total_budget_eur": 300,
        }

        trip = TravelPreferences(**data)

        self.assertIsInstance(trip.departure_day, date)
        self.assertEqual(trip.departure_day, departure)
        self.assertEqual(trip.return_date, departure + timedelta(days=2))

    def test_reject_invalid_departure_values(self):
        data = {
            "origin_city": "Bourges",
            "destination_city": "Paris",
            "departure_day": date.today(),
            "duration_days": 3,
            "num_adults": 2,
            "total_budget_eur": 300,
        }

        for value in ("not-a-date", "2030-02-30", "", None):
            with self.subTest(departure_day=value):
                data["departure_day"] = value
                with self.assertRaises(ValidationError) as caught:
                    TravelPreferences(**data)
                self.assertEqual(
                    [error["loc"] for error in caught.exception.errors()],
                    [("departure_day",)],
                )

    def test_reject_past_departure_iso_string(self):
        data = {
            "origin_city": "Bourges",
            "destination_city": "Paris",
            "departure_day": (date.today() - timedelta(days=1)).isoformat(),
            "duration_days": 3,
            "num_adults": 2,
            "total_budget_eur": 300,
        }

        with self.assertRaises(ValidationError) as caught:
            TravelPreferences(**data)

        self.assertEqual(
            [(error["loc"], error["type"]) for error in caught.exception.errors()],
            [(("departure_day",), "value_error")],
        )


from copy import deepcopy
from datetime import time
from travel_planner.models import Activity, TripDay, Itinerary


def activity_data():
    return {
        "name": "Museum", "location": "Paris", "start_time": "09:00",
        "duration_minutes": 120, "estimated_cost_eur": 30.0,
    }


def day_data():
    return {"date": "2030-12-20", "activities": [activity_data()]}


def itinerary_data():
    return {
        "title": "Paris trip", "destination_city": "Paris",
        "days": [day_data(), {**day_data(), "date": "2030-12-21"}],
    }


class OutputModelTestCase(unittest.TestCase):
    def assert_invalid(self, model, data, location, error_type=None):
        with self.assertRaises(ValidationError) as caught:
            model.model_validate(data)
        errors = caught.exception.errors()
        self.assertIn(location, [error["loc"] for error in errors])
        if error_type is not None:
            self.assertIn(
                (location, error_type),
                [(error["loc"], error["type"]) for error in errors],
            )


class TestActivity(OutputModelTestCase):
    def test_valid_activity_and_iso_time(self):
        activity = Activity.model_validate(activity_data())
        self.assertEqual(activity.start_time, time(9, 0))
        self.assertEqual(activity.duration_minutes, 120)
        self.assertEqual(activity.estimated_cost_eur, 30.0)

    def test_required_fields(self):
        for field in activity_data():
            with self.subTest(field=field):
                data = activity_data()
                del data[field]
                self.assert_invalid(Activity, data, (field,), "missing")

    def test_empty_text(self):
        for field in ("name", "location"):
            with self.subTest(field=field):
                self.assert_invalid(
                    Activity, {**activity_data(), field: ""}, (field,),
                )

    def test_invalid_times(self):
        for value in ("24:00", "09:60", "invalid", "", None):
            with self.subTest(value=value):
                self.assert_invalid(
                    Activity, {**activity_data(), "start_time": value},
                    ("start_time",),
                )

    def test_duration_boundaries(self):
        self.assertEqual(
            Activity.model_validate(
                {**activity_data(), "duration_minutes": 1}
            ).duration_minutes, 1,
        )
        for value in (0, -1, 1.5, None):
            with self.subTest(value=value):
                self.assert_invalid(
                    Activity, {**activity_data(), "duration_minutes": value},
                    ("duration_minutes",),
                )

    def test_accept_free_and_fractional_cost(self):
        for value in (0, 0.5, 12.75):
            with self.subTest(value=value):
                activity = Activity.model_validate(
                    {**activity_data(), "estimated_cost_eur": value}
                )
                self.assertEqual(activity.estimated_cost_eur, value)

    def test_reject_invalid_cost(self):
        for value in (-1, float("nan"), float("inf"), float("-inf"), None):
            with self.subTest(value=value):
                self.assert_invalid(
                    Activity, {**activity_data(), "estimated_cost_eur": value},
                    ("estimated_cost_eur",),
                )


class TestTripDay(OutputModelTestCase):
    def test_valid_day_and_nested_conversion(self):
        day = TripDay.model_validate(day_data())
        self.assertEqual(day.date, date(2030, 12, 20))
        self.assertIsInstance(day.activities[0], Activity)

    def test_required_fields(self):
        for field in day_data():
            with self.subTest(field=field):
                data = day_data()
                del data[field]
                self.assert_invalid(TripDay, data, (field,), "missing")

    def test_invalid_dates(self):
        for value in ("2030-02-30", "invalid", "", None):
            with self.subTest(value=value):
                self.assert_invalid(
                    TripDay, {**day_data(), "date": value}, ("date",),
                )

    def test_empty_or_invalid_activities(self):
        for value in ([], None, "invalid"):
            with self.subTest(value=value):
                self.assert_invalid(
                    TripDay, {**day_data(), "activities": value},
                    ("activities",),
                )

    def test_nested_activity_error_location(self):
        data = day_data()
        data["activities"][0]["estimated_cost_eur"] = -1
        self.assert_invalid(
            TripDay, data, ("activities", 0, "estimated_cost_eur"),
        )


class TestItinerary(OutputModelTestCase):
    def test_valid_itinerary_and_nested_conversion(self):
        trip = Itinerary.model_validate(itinerary_data())
        self.assertEqual(trip.title, "Paris trip")
        self.assertIsInstance(trip.days[0], TripDay)
        self.assertIsInstance(trip.days[0].activities[0], Activity)

    def test_required_fields(self):
        for field in itinerary_data():
            with self.subTest(field=field):
                data = itinerary_data()
                del data[field]
                self.assert_invalid(Itinerary, data, (field,), "missing")

    def test_empty_title(self):
        self.assert_invalid(
            Itinerary, {**itinerary_data(), "title": ""}, ("title",),
        )

    def test_supported_destinations(self):
        for city in ("Paris", "Lyon", "Strasbourg"):
            with self.subTest(city=city):
                trip = Itinerary.model_validate(
                    {**itinerary_data(), "destination_city": city}
                )
                self.assertEqual(trip.destination_city, city)

    def test_invalid_destinations(self):
        for city in ("Nice", "paris", "", None):
            with self.subTest(city=city):
                self.assert_invalid(
                    Itinerary, {**itinerary_data(), "destination_city": city},
                    ("destination_city",),
                )

    def test_day_count_boundaries(self):
        for count in range(2, 8):
            with self.subTest(count=count):
                data = itinerary_data()
                data["days"] = [
                    {**day_data(), "date": date(2030, 12, 20) + timedelta(days=i)}
                    for i in range(count)
                ]
                self.assertEqual(
                    len(Itinerary.model_validate(data).days), count,
                )

    def test_invalid_day_counts(self):
        for count in (0, 1, 8):
            with self.subTest(count=count):
                data = itinerary_data()
                data["days"] = [day_data() for _ in range(count)]
                self.assert_invalid(Itinerary, data, ("days",))

    def test_invalid_days_type(self):
        for value in (None, "invalid"):
            with self.subTest(value=value):
                self.assert_invalid(
                    Itinerary, {**itinerary_data(), "days": value}, ("days",),
                )

    def test_nested_error_location(self):
        data = itinerary_data()
        data["days"][1]["activities"][0]["duration_minutes"] = 0
        self.assert_invalid(
            Itinerary, data, ("days", 1, "activities", 0, "duration_minutes"),
        )

    def test_total_across_multiple_days_and_activities(self):
        data = itinerary_data()
        data["days"][0]["activities"].append(
            {**activity_data(), "estimated_cost_eur": 12.75}
        )
        data["days"][1]["activities"][0]["estimated_cost_eur"] = 0.5
        trip = Itinerary.model_validate(data)
        self.assertAlmostEqual(trip.total_estimated_cost_eur, 43.25)

    def test_all_free_activities_total_is_float_zero(self):
        data = itinerary_data()
        for day in data["days"]:
            day["activities"][0]["estimated_cost_eur"] = 0
        total = Itinerary.model_validate(data).total_estimated_cost_eur
        self.assertEqual(total, 0.0)
        self.assertIsInstance(total, float)

    def test_total_recomputed_after_cost_change(self):
        trip = Itinerary.model_validate(itinerary_data())
        trip.days[0].activities[0].estimated_cost_eur = 10.0
        self.assertEqual(trip.total_estimated_cost_eur, 40.0)

    def test_json_round_trip_and_property_exclusion(self):
        trip = Itinerary.model_validate(itinerary_data())
        restored = Itinerary.model_validate_json(trip.model_dump_json())
        self.assertEqual(restored, trip)
        self.assertEqual(restored.total_estimated_cost_eur, 60.0)
        self.assertNotIn("total_estimated_cost_eur", trip.model_dump())

    def test_model_validation_does_not_mutate_input(self):
        data = itinerary_data()
        original = deepcopy(data)
        Itinerary.model_validate(data)
        self.assertEqual(data, original)
