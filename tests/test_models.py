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
