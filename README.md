# CameraConnectionChecker

## Description

`CameraConnectionChecker` is a Python script designed for discovering and checking connections to streams from various cameras using RTSP and HTTP protocols. The script utilizes the `asyncio` and `aiohttp` libraries for asynchronous network requests and can retrieve camera information from ZoomEye. This tool supports multiple camera brands and provides detailed logs for successful and failed connection attempts.

**Important:** This script is developed solely for scientific purposes. We do not endorse or support any actions related to hacking or unauthorized access to devices. Please use this tool only for research and understanding the functionality of network cameras.

## Features

- Support for multiple camera brands, including Dahua, Hikvision, Axis, Foscam, Samsung, Trendnet, and Sony.
- Checking the availability of HTTP and RTSP streams.
- Asynchronous network requests for improved performance.
- Logging of successful and failed connections.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ivob0bul/CameraConnectionChecker.git

2. Navigate to the project directory:
	
	```bash
	cd CameraConnectionChecker

3. Install the required libraries:

	```bash
	pip install -r requirements.txt

## Usage
1. Set up ZoomEye:
	Ensure that you have ZoomEye installed and have access to its API.

2. Edit the search query:
	Open the camera_connection_checker.py file and modify the search_query variable at the top of the script to customize the search according to your needs. For example:

	```bash
	search_query = "app:trendnet +after:'2024-01-01' +before:'2025-01-01'"

Change the value of search_query to fit your specific requirements.

3. Run the script:

	```bash
	python cam.py

## Examples
- Discovering cameras using ZoomEye and checking available streams:

	```bash
	[DEBUG] App found: dahua on IP: 192.168.1.10
	[+] Camera found 'dahua' on IP: 192.168.1.10
	[DEBUG] Checking RTSP-stream: rtsp://192.168.1.10/media/video1

## Supported Cameras
This script supports multiple camera brands with specific HTTP and RTSP endpoints:

**Dahua**
- **HTTP**: `/cgi-bin/mjpg/video.cgi`, `/cgi-bin/snapshot.cgi`
- **RTSP**: `rtsp://{ip}:554/cam/realmonitor?channel=1&subtype=0`, `rtsp://{ip}:554/cam/realmonitor?channel=1&subtype=1`

**Hikvision**
- **HTTP**: `/ISAPI/Streaming/channels/1/picture`, `/onvif-http/snapshot?Profile_1`
- **RTSP**: `rtsp://{ip}:554/Streaming/Channels/101`, `rtsp://{ip}:554/Streaming/Channels/102`

_Add similar listings for other brands (Axis, Foscam, Samsung, Trendnet, Sony) following this format._

## Contribution
If you want to contribute to the project, please fork the repository, make your changes, and submit a pull request. We welcome your suggestions and improvements!

## License
This project is licensed under the MIT License.
