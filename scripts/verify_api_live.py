import subprocess
import time
import requests
import sys

def verify_live_api():
    print("Launching Uvicorn backend process...")
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000", "--host", "127.0.0.1"]
    proc = subprocess.Popen(cmd, cwd="backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        # Wait for server to boot
        time.sleep(3)
        poll = proc.poll()
        if poll is not None:
            out, err = proc.communicate()
            print(f"Server exited early with code {poll}!\nSTDOUT:\n{out}\nSTDERR:\n{err}")
            sys.exit(1)

        base_url = "http://127.0.0.1:8000"

        # 1. Health check
        r1 = requests.get(f"{base_url}/health")
        print(f"GET /health: {r1.status_code} -> {r1.json()}")
        assert r1.status_code == 200

        # 2. System info
        r2 = requests.get(f"{base_url}/api/v1/system/info")
        print(f"GET /api/v1/system/info: {r2.status_code} -> {r2.json()['app_name']}")
        assert r2.status_code == 200

        # 3. Master data
        r3 = requests.get(f"{base_url}/api/v1/roles")
        print(f"GET /api/v1/roles: {r3.status_code} -> {len(r3.json())} roles")
        assert len(r3.json()) == 25

        # 4. Employees
        r4 = requests.get(f"{base_url}/api/v1/employees?page=1&page_size=2")
        print(f"GET /api/v1/employees: {r4.status_code} -> {r4.json()['total']} total employees")
        assert r4.json()["total"] == 5000

        # 5. Auth login
        r5 = requests.post(f"{base_url}/api/v1/auth/login", json={"username": "admin", "password": "AdminPassword123!"})
        print(f"POST /api/v1/auth/login: {r5.status_code} -> Token generated for {r5.json()['username']}")
        assert r5.status_code == 200
        token = r5.json()["access_token"]

        # 6. Exceptions
        r6 = requests.get(f"{base_url}/api/v1/exceptions", headers={"Authorization": f"Bearer {token}"})
        print(f"GET /api/v1/exceptions: {r6.status_code} -> {len(r6.json())} exceptions")
        assert len(r6.json()) > 0

        print("\nALL LIVE BACKEND ENDPOINTS VERIFIED SUCCESSFULLY!")

    finally:
        proc.terminate()
        proc.wait()
        print("Backend process cleanly terminated.")

if __name__ == "__main__":
    verify_live_api()
