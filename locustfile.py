from urllib import response
from locust import HttpUser, task, between
import random

# List of sample URLs to shorten (you can add or change these)
SAMPLE_URLS = [
    "https://example.com",
    "https://www.google.com",
    "https://github.com",
    "https://news.ycombinator.com",
    "https://developer.mozilla.org",
    "https://stackoverflow.com",
    "https://wikipedia.org",
    "https://medium.com",
    "https://twitter.com",
    "https://instagram.com"
]


class URLShortenerUser(HttpUser):
    host = "http://localhost:5000"  # Change if deploying online
    wait_time = between(1, 3)  # Users wait 1–3 seconds between actions

    @task
    def index(self):
        with self.client.get("/", catch_response=True) as response:
            if response.status_code != 200:
                print(
                    f"Failed request: {response.status_code} - {response.text}")

    @task(3)
    def shorten_url(self):
        # Pick a random URL from the list
        original_url = random.choice(SAMPLE_URLS)

        # Simulate form submission
        self.client.post(
            "/",
            data={"url": original_url},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            catch_response=True
        )

        # Optional: check if response contains success message
        if response.status_code == 500:
            response.failure("Server error")
