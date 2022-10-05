import shutil
from pathlib import Path
import matplotlib.pyplot as plt
import unrealcv
from unrealcv.util import read_png

__author__ = "Simon Heck"


class UE5EnvWrapper:
    """Wrapper that handles interactions between the program and Unreal Engine and takes the forwarded port as an input"""

    def __init__(self, port: int = 8500):
        global ue5
        ue5 = unrealcv.Client(("localhost", port))
        ue5.connect(timeout=5)
        if ue5.isconnected():
            print(ue5.request("vget /unrealcv/status"))
        else:
            raise Exception(f"Failed to connect to the UnrealCV server at port: {port}")

    def isconnected(self):
        """Is the program connected to Unreal"""
        return self.ue5.isconnected()

    def reset(self):
        """Reset robot to start location. Interacts with UE5 Blueprint."""
        ue5.request(f"vset /action/keyboard backspace 1")

    def getCameraLocation(self, cameraID: int = 0) -> tuple[float, float, float]:
        """Returns X, Y, Z location of a camera in the Unreal Environment."""
        x, y, z = ue5.request(f"vget /camera/{cameraID}/location").split()
        return float(x), float(y), float(z)

    def getCameraRotation(self, cameraID: int = 0) -> tuple[float, float, float]:
        """Returns Pitch, Yaw, and Roll values for Camera number"""
        pitch, yaw, roll = ue5.request(f"vget /camera/{cameraID}/rotation").split()
        return float(pitch), float(yaw), float(roll)

    def setCameraLocation(
        self, pitch: float, yaw: float, roll: float, cameraID: int = 0
    ):
        """Sets Pitch, Yaw, and Roll values for a specific number"""
        ue5.request(f"vset /camera/{cameraID}/rotation {pitch} {yaw} {roll}")

    def left(self, degreeRot: float, cameraID: int = 0) -> None:
        """Rotate camera left a number of degrees."""
        currentPitch, currentYaw, currentRoll = self.getCameraRotation(cameraID)
        ue5.request(
            f"vset /camera/0/rotation {currentPitch} {float(currentYaw) - degreeRot} {currentRoll}"
        )

    def right(self, degreeRot: float, cameraID: int = 0) -> None:
        """Rotate camera right a number of degrees."""
        currentPitch, currentYaw, currentRoll = self.getCameraRotation(cameraID)
        ue5.request(
            f"vset /camera/0/rotation {currentPitch} {float(currentYaw) + degreeRot} {currentRoll}"
        )

    def forward(self, value: float) -> None:
        """Move Robot forward a number of centimeters. Interacts with UE5 Blueprint"""
        ue5.request(f"vset /action/keyboard up 1")

    def back(self, value: float) -> None:
        """Move Robot backwards a number of centimeters. Interacts with UE5 Blueprint"""
        ue5.request(f"vset /action/keyboard down 1")
        ue5.request("vset /camera/0/rotation 0 0 0")

    def open_level(levelName: str) -> None:
        """Opens a new level in the UE5 Environment. UnrealCV built in command"""
        ue5.request(f"open {levelName}")

    def request_image(self, cameraID: int):
        """Get an image from a specific camera, used with matplotlib"""
        image_data = ue5.request(f"vget /camera/{cameraID}/lit jpg")
        return read_png(image_data)

    def save_image(self, cameraNum: int, annotation: str, finalPath: str) -> None:
        """Saves Image to a specific path

        Args:
            cameraNum (Int): Camera to get picture from
            annotation (Str): File extension for image(.jpg, .png)
            path (str): _description_

        Returns:
            str: path image was saved to
        """
        imagePath = ue5.request(f"vget /camera/{cameraNum}/lit {annotation}.jpg")
        # TODO change to PathLib and find out if unrealcv will store the file on the local machine or in the cloud
        shutil.move(imagePath, finalPath)

    def show(self):
        """If matplotlib is being used, show the image taken to the plot"""
        plt.imshow(self.request_image())
