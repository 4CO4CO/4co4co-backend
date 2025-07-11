from locust import HttpUser, task, between
import random

class LanternUser(HttpUser):
    wait_time = between(1, 3)
    lantern_ids = []

    def on_start(self):
        """
        테스트 유저가 시작할 때 1회 호출됨.
        목록에서 랜턴 ID를 가져와서 저장해 둔다.
        """
        response = self.client.get("/api/v1/lanterns")
        if response.status_code == 200:
            try:
                data = response.json().get("data", [])
                self.lantern_ids = [item["lantern_id"] for item in data]
                print(f"랜턴 ID 목록 로드 완료: {len(self.lantern_ids)}개")
            except Exception as e:
                print(f"JSON 파싱 오류: {e}")
        else:
            print(f"목록 API 응답 실패: {response.status_code}")


    @task(3)
    def get_lantern_detail_random(self):
        """
        랜덤한 lantern_id를 선택하여 상세 조회 요청
        """
        if self.lantern_ids:
            lantern_id = random.choice(self.lantern_ids)
            self.client.get(f"/api/v1/lanterns/{lantern_id}")

    @task(1)
    def get_lantern_list(self):
        """
        랜턴 목록을 다시 불러오는 요청 (부하 분산용)
        """
        self.client.get("/api/v1/lanterns")
