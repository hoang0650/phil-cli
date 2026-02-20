import asyncio
from datetime import datetime

class AutomationBackend:
    def __init__(self):
        self.tasks = []

    async def schedule_task(self, name: str, delay: int, func, *args, **kwargs):
        print(f"Scheduling task '{name}' in {delay} seconds...")
        await asyncio.sleep(delay)
        print(f"Executing task '{name}' at {datetime.now()}")
        return await func(*args, **kwargs)

    async def run_automation_loop(self):
        # Logic chạy các tác vụ định kỳ (cron-like)
        while True:
            # Kiểm tra các tác vụ cần thực thi
            await asyncio.sleep(60)

# Ví dụ một task tự động hóa email
async def send_email_reminder(to: str, subject: str):
    print(f"Email sent to {to}: {subject}")

# backend = AutomationBackend()
# asyncio.run(backend.schedule_task("Daily Report", 5, send_email_reminder, "user@example.com", "Your daily summary"))