import os
import httpx
from groq import APITimeoutError, APIStatusError
import unittest
from unittest.mock import patch
from io import StringIO
import io
from contextlib import redirect_stderr, redirect_stdout
from pydantic import ValidationError

import generate_itinerary

class TestGenerateItinerary(unittest.TestCase):
    def test_missing_api_key(self):
        with patch.dict(os.environ , {} , clear=True):
            with patch("generate_itinerary.Groq") as mock_groq:
                with self.assertRaisesRegex(
                    ValueError, "GROQ_API_KEY"
                ):
                    generate_itinerary.main()
                mock_groq.assert_not_called()

    def test_invalid_model_json(self):
        with patch.dict(
            os.environ,
            {"GROQ_API_KEY": "fake-key-for-offline-test"},
        ):
            with patch("generate_itinerary.Groq") as mock_groq:
                mock_client = mock_groq.return_value
                mock_create = mock_client.chat.completions.create
                mock_create.return_value.choices[0].message.content = ("Don't be JSON")
                with self.assertRaises(ValidationError):
                    generate_itinerary.main()
                mock_create.assert_called_once()
    def test_api_timeout(self):
        with patch.dict(os.environ , {"GROQ_API_KEY": "fake_key"}):
            with patch("generate_itinerary.Groq") as mock_groq:
                mock_create = (
                    mock_groq.return_value.chat.completions.create
                )
                mock_create.side_effect = APITimeoutError(
                    request=httpx.Request(
                        "POST",
                        "https://api.groq.com/openai/v1/chat/completions",
                    )
                )
                with self.assertRaises(APITimeoutError):
                    generate_itinerary.main()
                mock_create.assert_called_once()
    def test_http_errors(self):
        for status in (401, 403, 429, 500):
            with self.subTest(status=status):
                with patch.dict(os.environ, {"GROQ_API_KEY" : "fake-key"}):
                    with patch("generate_itinerary.Groq") as mock_groq:
                        mock_create = (
                            mock_groq.return_value.chat.completions.create
                        )
                        response = httpx.Response(
                            status,
                            request=httpx.Request(
                                "POST",
                                "https://api.groq.com/openai/v1/chat/completions",
                            ),
                        )
                        mock_create.side_effect = APIStatusError(
                            "Simulated HTTP error",
                            response=response,
                            body=None,
                        )

                        with self.assertRaises(APIStatusError) as caught:
                            generate_itinerary.main()

                        self.assertEqual(
                            caught.exception.status_code, status
                        )
                        mock_create.assert_called_once()
    def test_empty_content(self):
        for content in (None, ""):
            with self.subTest(content=content):
                with patch.dict(os.environ, {"GROQ_API_KEY": "fake-key"}):
                    with patch("generate_itinerary.Groq") as mock_groq:
                        mock_create = (mock_groq.return_value.chat.completions.create)
                        mock_create.return_value.choices[0].message.content = content 
                        with self.assertRaises(ValueError):
                            generate_itinerary.main()
                        mock_create.assert_called_once()




from copy import deepcopy
from pathlib import Path
import json
from groq import APIConnectionError
from travel_planner.models import Itinerary


def sample_data():
    return {
        "destination_city": "Paris",
        "dates": ["2030-12-20", "2030-12-21"],
        "activities": [
            {"name": "Museum", "location": "Paris",
             "duration_minutes": 120, "estimated_cost_eur": 30},
            {"name": "Park", "location": "Paris",
             "duration_minutes": 60, "estimated_cost_eur": 0},
            {"name": "Exhibition", "location": "Paris",
             "duration_minutes": 90, "estimated_cost_eur": 15},
        ],
    }


def valid_output():
    sample = sample_data()
    return {
        "title": "Sample itinerary",
        "destination_city": sample["destination_city"],
        "days": [
            {"date": sample["dates"][0], "activities": [
                {**sample["activities"][0], "start_time": "09:00"},
                {**sample["activities"][1], "start_time": "12:00"},
            ]},
            {"date": sample["dates"][1], "activities": [
                {**sample["activities"][2], "start_time": "09:00"},
            ]},
        ],
    }


class TestMainAdditional(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ , {"GROQ_API_KEY": "offline-secret"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.sdk = patch("generate_itinerary.Groq")
        self.groq = self.sdk.start()
        self.addCleanup(self.sdk.stop)
        self.create = self.groq.return_value.chat.completions.create
        self.fixture = patch.object(
            generate_itinerary.Path, "read_text",
            return_value=json.dumps(sample_data())
        )
        self.fixture.start()
        self.addCleanup(self.fixture.stop)

    def set_output(self, data):
        self.create.return_value.choices[0].message.content = json.dumps(data)

    def test_connection_error(self):
        self.create.side_effect = APIConnectionError(
            request=httpx.Request("POST", "https://api.groq.com")
        )
        with self.assertRaises(APIConnectionError):
            generate_itinerary.main()
        self.create.assert_called_once()

    def test_missing_output_field(self):
        data = valid_output()
        del data["days"][0]["activities"][0]["name"]
        self.set_output(data)
        with self.assertRaises(ValidationError) as caught:
            generate_itinerary.main()
        self.assertIn(
            ("days", 0, "activities", 0, "name"),
            [error["loc"] for error in caught.exception.errors()],
        )

    def test_wrong_destination_or_dates(self):
        for field, value, message in (
            ("destination_city", "Lyon", "Destination"),
            ("date", "2030-12-22", "Date"),
        ):
            with self.subTest(field=field):
                data = valid_output()
                if field == "date":
                    data["days"][1]["date"] = value
                else:
                    data[field] = value
                self.set_output(data)
                with self.assertRaisesRegex(ValueError, message):
                    generate_itinerary.main()

    def test_missing_duplicate_added_or_modified_activity(self):
        for case in ("missing", "duplicate", "added", "modified"):
            with self.subTest(case=case):
                data = valid_output()
                activities = data["days"][0]["activities"]
                if case == "missing":
                    activities.pop()
                elif case == "duplicate":
                    activities[1] = deepcopy(activities[0])
                elif case == "added":
                    activities.append(deepcopy(activities[0]))
                else:
                    activities[0]["estimated_cost_eur"] = 99
                self.set_output(data)
                with self.assertRaisesRegex(ValueError, "Activity"):
                    generate_itinerary.main()

    def test_missing_or_invalid_fixture(self):
        for error in (
            FileNotFoundError("missing"),
            json.JSONDecodeError("bad json", "{", 0),
        ):
            with self.subTest(error=type(error).__name__):
                with patch.object(
                    generate_itinerary.Path, "read_text", side_effect=error
                ):
                    with self.assertRaises(type(error)):
                        generate_itinerary.main()
                self.groq.assert_not_called()

    def test_success_and_no_automatic_retry(self):
        self.set_output(valid_output())
        output = StringIO()
        with redirect_stdout(output):
            generate_itinerary.main()
        self.assertIn("45.0", output.getvalue())
        self.groq.assert_called_once_with(timeout=30.0, max_retries=0)
        self.create.assert_called_once()


class TestCli(unittest.TestCase):
    def check_cli_error(self, error, expected):
        stdout, stderr = StringIO(), StringIO()
        with patch("generate_itinerary.main", side_effect=error) as main:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as caught:
                    generate_itinerary.cli()
        self.assertEqual(caught.exception.code, 1)
        self.assertIn(expected, stderr.getvalue())
        self.assertEqual(stdout.getvalue(), "")
        self.assertNotIn("Traceback", stderr.getvalue())
        self.assertNotIn("offline-secret", stderr.getvalue())
        main.assert_called_once()

    def test_cli_value_error(self):
        self.check_cli_error(ValueError("Invalid data"), "Invalid data")

    def test_cli_timeout(self):
        self.check_cli_error(
            APITimeoutError(
                request=httpx.Request("POST", "https://api.groq.com")
            ), "time out",
        )

    def test_cli_connection_error(self):
        self.check_cli_error(
            APIConnectionError(
                request=httpx.Request("POST", "https://api.groq.com")
            ), "connect API",
        )

    def test_cli_http_errors(self):
        for status, expected in (
            (401, "API key"), (403, "rejected"), (429, "limit"), (500, "500"),
        ):
            with self.subTest(status=status):
                response = httpx.Response(
                    status,
                    request=httpx.Request("POST", "https://api.groq.com"),
                )
                self.check_cli_error(
                    APIStatusError(
                        "offline-secret", response=response,
                        body={"private": "offline-secret"},
                    ), expected,
                )

    def test_cli_validation_error(self):
        try:
            Itinerary.model_validate_json("{}")
        except ValidationError as error:
            self.check_cli_error(error, "schema Itinerary")
        else:
            self.fail("Expected ValidationError")

    def test_cli_file_errors(self):
        self.check_cli_error(FileNotFoundError("missing"), "data sample")
        self.check_cli_error(
            json.JSONDecodeError("bad json", "{", 0), "incorrect JSON"
        )

    def test_cli_success(self):
        stdout, stderr = StringIO(), StringIO()
        with patch("generate_itinerary.main", return_value=None) as main:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = generate_itinerary.cli()
        self.assertIsNone(result)
        self.assertEqual(stderr.getvalue(), "")
        main.assert_called_once()


if __name__ == "__main__":
    unittest.main()
