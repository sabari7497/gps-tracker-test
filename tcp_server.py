import socket
import threading
import logging
import django
import os

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.utils import timezone
from gps.models import GPSData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_client_connection(client_socket):
    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            logger.info(f"Received data: {data}")
            process_gps_data(data)
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client_socket.close()

def process_gps_data(data):
    # Adjust the parsing according to your GPS data format
    try:
        parts = data.split(',')
        if len(parts) >= 2:
            latitude = float(parts[0].strip())
            longitude = float(parts[1].strip())
            timestamp = timezone.now()
            GPSData.objects.create(latitude=latitude, longitude=longitude, timestamp=timestamp)
        else:
            logger.warning("Invalid data format")
    except (IndexError, ValueError) as e:
        logger.error(f"Failed to process GPS data: {e}")

def start_server(host='0.0.0.0', port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    logger.info(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        logger.info(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
