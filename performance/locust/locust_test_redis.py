from locust import HttpUser, task, between

class CeleryTestUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def call_celery_api(self):
        self.client.post("/celery")
