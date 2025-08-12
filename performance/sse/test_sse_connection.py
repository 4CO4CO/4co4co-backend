import asyncio
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
import os

# .env에서 환경변수 로딩
load_dotenv()
SSE_ENDPOINT = os.getenv("SSE_ENDPOINT")

USER_COUNT = 50
DURATION = 600  # 10분
PING_TIMEOUT = 20  # 15초 ping 기준 + 여유


async def listen_to_sse(user_id, results):
    print(f"[User {user_id}] 연결 시작")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SSE_ENDPOINT, timeout=None) as resp:
                start_time = datetime.now()
                pings = 0

                async for line in resp.content:
                    decoded = line.decode().strip()
                    if decoded.startswith("data: ping"):
                        pings += 1
                        print(f"[User {user_id}] Ping 수신 총 {pings}회")

                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= DURATION:
                        break

                results[user_id] = pings
                print(f"[User {user_id}] 종료 / 총 ping 수: {pings}")
    except Exception as e:
        print(f"[User {user_id}] 오류 발생: {e}")
        results[user_id] = -1


async def main():
    results = {}
    tasks = [listen_to_sse(i, results) for i in range(USER_COUNT)]
    await asyncio.gather(*tasks)

    print("\n실험 요약 결과")
    for uid, count in results.items():
        status = "성공" if count > 0 else "실패"
        print(f" - 사용자 {uid}: {count}회 / {status}")

    success_rate = sum(1 for c in results.values() if c > 0) / USER_COUNT * 100
    print(f"\n성공률: {success_rate:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
