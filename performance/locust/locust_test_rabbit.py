from locust import HttpUser, task, between

class RabbitCeleryTestUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def call_rabbitmq_celery(self):
        self.client.post("/celery")
