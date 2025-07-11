from locust import HttpUser, task, between

class PollingTestUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def call_polling_api(self):
        self.client.post("/polling")