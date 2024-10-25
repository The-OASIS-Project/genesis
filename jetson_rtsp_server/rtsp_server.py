import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib
import argparse
import logging
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CameraType(Enum):
    CSI = "csi"
    USB = "usb"
    ZED = "zed"

class RTSPServer:
    def __init__(self, camera_type, width=1920, height=1080, framerate=30, port=8554, 
                 bitrate=4000000, device_id=0):
        Gst.init(None)
        self.server = GstRtspServer.RTSPServer()
        self.server.set_service(str(port))
        self.camera_type = CameraType(camera_type)
        self.device_id = device_id
        
        # Create a factory for the stream
        self.factory = GstRtspServer.RTSPMediaFactory()
        
        # Configure pipeline based on camera type
        pipeline = self._get_camera_pipeline(width, height, framerate, bitrate)
        
        logging.info(f"Pipeline: {pipeline}")
        self.factory.set_launch(pipeline)
        self.factory.set_shared(True)
        
        # Attach the factory to the server
        self.server.get_mount_points().add_factory("/camera", self.factory)
        
        # Start the server
        self.server.attach(None)
        logging.info(f"RTSP server started on port {port}")

    def _get_camera_pipeline(self, width, height, framerate, bitrate):
        if self.camera_type == CameraType.CSI:
            return (
                f'nvarguscamerasrc ! '
                f'video/x-raw(memory:NVMM),width={width},height={height},'
                f'framerate={framerate}/1 ! '
                f'nvv4l2h264enc bitrate={bitrate} ! '
                f'h264parse ! '
                f'rtph264pay name=pay0 pt=96'
            )
        elif self.camera_type == CameraType.USB:
            return (
                f'v4l2src device=/dev/video{self.device_id} ! '
                f'video/x-raw,width={width},height={height},framerate={framerate}/1 ! '
                f'videoconvert ! nvvidconv ! '
                f'video/x-raw(memory:NVMM) ! '
                f'nvv4l2h264enc bitrate={bitrate} ! '
                f'h264parse ! '
                f'rtph264pay name=pay0 pt=96'
            )
        elif self.camera_type == CameraType.ZED:
            return (
                # ZED SDK provides data in RGBA format
                f'zcamsrc camera-id={self.device_id} ! '
                f'video/x-raw,format=RGBA,width={width},height={height},'
                f'framerate={framerate}/1 ! '
                f'videoconvert ! nvvidconv ! '
                f'video/x-raw(memory:NVMM) ! '
                f'nvv4l2h264enc bitrate={bitrate} ! '
                f'h264parse ! '
                f'rtph264pay name=pay0 pt=96'
            )

    def run(self):
        loop = GLib.MainLoop()
        try:
            logging.info("Server is running...")
            loop.run()
        except KeyboardInterrupt:
            logging.info("Server stopped by user")
        except Exception as e:
            logging.error(f"Error: {str(e)}")
        finally:
            loop.quit()

def parse_args():
    parser = argparse.ArgumentParser(description='Multi-Camera RTSP Server for Jetson')
    parser.add_argument('--camera', type=str, choices=['csi', 'usb', 'zed'], 
                      default='csi', help='Camera type to use')
    parser.add_argument('--device-id', type=int, default=0, 
                      help='Camera device ID (for USB or ZED cameras)')
    parser.add_argument('--width', type=int, default=1920, help='Stream width')
    parser.add_argument('--height', type=int, default=1080, help='Stream height')
    parser.add_argument('--framerate', type=int, default=30, help='Stream framerate')
    parser.add_argument('--port', type=int, default=8554, help='RTSP port')
    parser.add_argument('--bitrate', type=int, default=4000000, help='Encoding bitrate')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    server = RTSPServer(
        camera_type=args.camera,
        width=args.width,
        height=args.height,
        framerate=args.framerate,
        port=args.port,
        bitrate=args.bitrate,
        device_id=args.device_id
    )
    print(f"RTSP server is running on rtsp://192.168.1.217:{args.port}/camera")
    print(f"Camera type: {args.camera.upper()}")
    server.run()
