from locust import HttpUser, task, between

class ThreadTestUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def call_thread_api(self):
        self.client.post("/thread")