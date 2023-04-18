import matplotlib.pyplot as plt
import unrealcv
from unrealcv.util import read_png
import time


class UE5EnvWrapper:
    """Handles interaction between the UE5 environment and the a program."""

    def __init__(self, port: int = 9000):
        self.ue5 = unrealcv.Client(("localhost", port))
        self.ue5.connect(timeout=5)

        if self.ue5.isconnected():
            print(self.ue5.request("vget /unrealcv/status"))
        else:
            raise Exception(f"Failed to connect to the UnrealCV server at port: {port}")

    def is_connected(self):
        """Is the program connected to Unreal."""
        return self.ue5.isconnected()

    def reset(self):
        """Reset agent to start location using a UE Blueprint command."""
        self.ue5.request("vset /action/keyboard backspace 0.1")

    def get_project_name(self):
        """Returns the name of the current connected project."""
        name = self.ue5.request("vget /scene/name")
        return name

    def get_camera_location(self, cam_id: int = 0) -> tuple[float, float, float]:
        """Returns x, y, z location of a camera in the Unreal Environment."""
        x, y, z = self.ue5.request(f"vget /camera/{cam_id}/location").split()
        return float(x), float(y), float(z)

    def set_camera_location(self, x: float, y: float, z: float, cam_id: int = 0):
        """Sets X, Y, and Z values of an Unreal Camera."""
        self.ue5.request(f"vset /camera/{cam_id}/location {x} {y} {z}")

    def get_camera_rotation(self, cam_id: int = 0) -> tuple[float, float, float]:
        """Returns pitch, yaw, and roll."""
        pitch, yaw, roll = self.ue5.request(f"vget /camera/{cam_id}/rotation").split()
        return float(pitch), float(yaw), float(roll)

    def set_camera_yaw(self, yaw: float, cam_id: int = 0):
        """Set the camera yaw in degrees."""
        ue_pitch, _, ue_roll = self.get_camera_rotation(cam_id)
        self.ue5.request(f"vset /camera/{cam_id}/rotation {ue_pitch} {yaw} {ue_roll}")

    def __rotate(self, rotation: float, cam_id: int = 0):
        """Rotate camera a number of degrees."""
        ue_pitch, ue_yaw, ue_roll = self.get_camera_rotation(cam_id)
        yaw = float(ue_yaw) + rotation
        self.ue5.request(f"vset /camera/0/rotation {ue_pitch} {yaw} {ue_roll}")

    def left(self, rotation: float, cam_id: int = 0):
        """Rotate camera left a number of degrees."""
        self.__rotate(-rotation, cam_id)

    def right(self, rotation: float, cam_id: int = 0):
        """Rotate camera right a number of degrees."""
        self.__rotate(rotation, cam_id)

    def forward(self):
        """Move Robot forward."""
        self.ue5.request("vset /action/keyboard up 1")

    def back(self):
        """Move Robot backwards."""
        self.ue5.request("vset /action/keyboard down 1")

    def request_image(self, cam_id: int = 0) -> bytes:
        """Get an image from a specific camera."""
        image_data = self.ue5.request(f"vget /camera/{cam_id}/lit jpg")
        return read_png(image_data)

    def save_image(self, cam_num: int) -> None:
        """Saves image using default name and path."""
        self.ue5.request("vrun HighResShot 1")
        # TODO: we also sleep in boxunreal?
        # Sleep in order for the photo to be properly saved
        time.sleep(1)

    def show(self):
        """If matplotlib is being used, show the image taken to the plot"""
        plt.imshow(self.request_image())
