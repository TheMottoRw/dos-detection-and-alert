import psutil
import time
import subprocess
from collections import Counter
from helper import mail_utils
from api import db
from datetime import datetime

THRESHOLD = 20  # max allowed connections per IP
TIME_WINDOW = 10 # 10 seconds
BAN_TIME = 15          # seconds to block attacker
banned_ips = {}  # {ip: unblock_time}
MAIL_RECEIVER = ""

def block_ip(ip):
    print(f"[!] Blocking IP {ip} for {BAN_TIME}s")
    subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    banned_ips[ip] = time.time() + BAN_TIME

def unblock_ip(ip):
    print(f"[+] Unblocking IP {ip}")
    subprocess.run(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"])
    banned_ips.pop(ip, None)

def monitor_connections():
    global BAN_TIME
    log_collection = db.get_log_collection()
    while True:
        # Unblock expired bans
        for ip, expiry in list(banned_ips.items()):
            if time.time() > expiry:
                data = {"ip": ip, "action": "unbanned",
                        "message": f"{ip} has been unblocked after {BAN_TIME} seconds being blocked for suspicious DOS attacks.",
                        "createdAt": datetime.now(),
                        "updatedAt": datetime.now(),
                        }
                res = log_collection.insert_one(data)
                unblock_ip(ip)
                message = f"[!] This IP: <b>{ip}</b> has been unblocked after {BAN_TIME} seconds being blocked for suspicious DOS attacks."
                # mail_utils.send_email(f"{MAIL_RECEIVER}","IP Unblocking alert",message)

        conns = psutil.net_connections(kind="inet")
        ip_counter = Counter()

        for conn in conns:
            if conn.laddr.port in [8000, 443] and conn.raddr:
                ip = conn.raddr.ip
                # skip already banned IPs
                if ip in banned_ips:
                    continue
                ip_counter[ip] += 1

        print(f"\n[+] Active connections on 8000/443")
        for ip, count in ip_counter.items():
            print(f"IP {ip} -> {count} connections")
            if count > THRESHOLD:
                message = f"<font color='red'>[!]</font> Potential DoS/DDoS detected from <font color='red'>{ip}</font> with (<b>connections: {count}</b>) and has been blocked."
                print(message)
                if ip in banned_ips:
                    continue
                # save into database
                data = {"ip": ip, "action": "banning", "message": f"{ip} with connections: {count} and has been blocked.",
                        "createdAt": datetime.now(),
                        "updatedAt": datetime.now(),
                        }
                res = log_collection.insert_one(data)
                created = log_collection.find_one({"_id": res.inserted_id})
                block_ip(ip)
                # mail_utils.send_email(f"{MAIL_RECEIVER}","DoS/DDoS detected",message)

        time.sleep(TIME_WINDOW)

if __name__ == "__main__":
    monitor_connections()
