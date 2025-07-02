import socket
import time

def connect_to_fake_server():
    try:
        # آدرس خارجی ساختگی (تست باید روی یک سرور واقعی باشه یا localhost برای تست)
        HOST = "192.168.0.0"  # Google DNS (فقط برای شبیه‌سازی، اتصال واقعی نیاز به اینترنت دارد)
        PORT = 12345      # پورت بالا

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("Connected to fake server.")
            time.sleep(60)  # نگه‌داشتن اتصال برای دیده شدن توسط psutil
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    connect_to_fake_server()
