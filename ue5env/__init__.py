import shutil
from pathlib import Path
import matplotlib.pyplot as plt
import unrealcv
from unrealcv.util import read_png
import time

__author__ = "Simon Heck"


class UE5EnvWrapper:
    """Wrapper that handles interactions between the program and Unreal Engine and takes the forwarded port as an input"""

    def __init__(self, port: int = 8500):
        self.ue5 = unrealcv.Client(("localhost", port))
        self.ue5.connect(timeout=5)
        if self.ue5.isconnected():
            print(self.ue5.request("vget /unrealcv/status"))
        else:
            raise Exception(f"Failed to connect to the UnrealCV server at port: {port}")

    def isconnected(self):
        """Is the program connected to Unreal"""
        return self.ue5.isconnected()

    def reset(self):
        """Reset robot to start location. Interacts with UE5 Blueprint."""
        self.ue5.request(f"vset /action/keyboard backspace 0.1")

    def getCameraLocation(self, cameraID: int = 0) -> tuple[float, float, float]:
        """Returns X, Y, Z location of a camera in the Unreal Environment."""
        x, y, z = self.ue5.request(f"vget /camera/{cameraID}/location").split()
        return float(x), float(y), float(z)

    def setCameraLocation(self, x: float, y: float, z: float, cameraID: int = 0):
        """Sets X, Y, and Z values of an Unreal Camera."""
        self.ue5.request(f"vset /camera/{cameraID}/location {x} {y} {z}")

    def getCameraRotation(self, cameraID: int = 0) -> tuple[float, float, float]:
        """Returns Pitch, Yaw, and Roll values for Camera number."""
        pitch, yaw, roll = self.ue5.request(f"vget /camera/{cameraID}/rotation").split()
        return float(pitch), float(yaw), float(roll)

    def setCameraYaw(self, yawDegree: float, cameraID: int = 0):
        """Set Camera Yaw value in unreal for a specific camera."""
        currentPitch, _, currentRoll = self.getCameraRotation(cameraID)
        self.ue5.request(
            f"vset /camera/{cameraID}/rotation {currentPitch} {yawDegree} {currentRoll}"
        )

    def left(self, degreeRot: float, cameraID: int = 0) -> None:
        """Rotate camera left a number of degrees."""
        currentPitch, currentYaw, currentRoll = self.getCameraRotation(cameraID)
        self.ue5.request(
            f"vset /camera/0/rotation {currentPitch} {float(currentYaw) - degreeRot} {currentRoll}"
        )

    def right(self, degreeRot: float, cameraID: int = 0) -> None:
        """Rotate camera right a number of degrees."""
        currentPitch, currentYaw, currentRoll = self.getCameraRotation(cameraID)
        self.ue5.request(
            f"vset /camera/0/rotation {currentPitch} {float(currentYaw) + degreeRot} {currentRoll}"
        )

    def forward(self, value: float) -> None:
        """Move Robot forward a number of centimeters. Interacts with UE5 Blueprint"""
        self.ue5.request(f"vset /action/keyboard up 1")

    def back(self, value: float) -> None:
        """Move Robot backwards a number of centimeters. Interacts with UE5 Blueprint"""
        self.ue5.request(f"vset /action/keyboard down 1")

    def request_image(self, cameraID: int):
        """Get an image from a specific camera, used with matplotlib"""
        image_data = self.ue5.request(f"vget /camera/{cameraID}/lit jpg")
        return read_png(image_data)

    def save_image(self, cam_num: int) -> None:
        """Saves Image to a specific path

        Args:
            cameraNum (Int): Camera to get picture from
            annotation (Str): File extension for image(jpg, png)
            path_to_unreal_project (Str): Path to the unreal project currently running

        Returns:
            str: path where the image was saved.
        """
        self.ue5.request("vset /action/keyboard tab 0.1")
        # Sleep in order for the photo to be properly saved
        time.sleep(1)

    def show(self):
        """If matplotlib is being used, show the image taken to the plot"""
        plt.imshow(self.request_image())
