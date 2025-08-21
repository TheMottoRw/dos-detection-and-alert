from scapy.all import sniff
from scapy.layers.inet import IP, TCP
from collections import Counter

ip_counter = Counter()
TIME_WINDOW = 10  # seconds
THRESHOLD = 100  # max allowed requests per IP per time window


def packet_callback(packet):
    if packet.haslayer(IP) and packet.haslayer(TCP):
        ip_src = packet[IP].src
        dport = packet[TCP].dport

        if dport in [80, 443]:  # only monitor HTTP/HTTPS
            ip_counter[ip_src] += 1


def monitor():
    global ip_counter
    while True:
        sniff(filter="tcp port 80 or tcp port 443", prn=packet_callback, store=0, timeout=TIME_WINDOW)

        print(f"\n[+] Traffic Report (last {TIME_WINDOW}s)")
        for ip, count in ip_counter.items():
            print(f"IP {ip} -> {count} requests")
            if count > THRESHOLD:
                print(f"[!] Possible DoS/DDoS attack detected from {ip} (requests: {count})")

        ip_counter = Counter()  # reset for next window


if __name__ == "__main__":
    monitor()
