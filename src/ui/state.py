"""Retained-mode UI state."""

from dataclasses import replace
from datetime import datetime

import imageio.v3 as iio
from PIL import Image

from common.camera import (
    Camera,
    CameraParams,
    interpolate_catmull_rom,
    interpolate_linear,
)
from common.reactive_params import ReactiveParams
from common.types import LUTtice

from .algo_choice import AlgoChoice
from .animations import AnimationMode, AnimationParams, ExportFormat
from .colours import ColourParams
from .constants import GIF_FOLDER, MP4_FOLDER, WEBM_FOLDER
from .utils import has_member, upscale_lat
from .widgets import TexturePanel


class UIState:
    """State of the application."""

    algo_choice: AlgoChoice
    algo_params: ReactiveParams
    texture_panel: TexturePanel
    colour_params: ColourParams
    camera: Camera
    camera_params: CameraParams
    animation_params: AnimationParams

    def __init__(self) -> None:
        """Initialise `UIState` with default values."""
        self.algo_choice = AlgoChoice.default()
        self.algo_params = AlgoChoice.get_algo_params(self.algo_choice.value)
        self.camera_params = CameraParams()
        self.colour_params = ColourParams()
        self.animation_params = AnimationParams(
            camera_access=lambda: self.camera,
            animation_generator=self.generate_animation,
        )
        # texture panel & camera need to be set via methods

    def set_texture_panel(self, texture_panel: TexturePanel) -> None:
        """Set the texture panel for `UIState`, finalising initial `UIState` setup."""
        self.texture_panel = texture_panel
        self.reset_camera()

    def reset_camera(self) -> None:
        """Reset the camera to its default position."""
        self.camera = AlgoChoice.get_algo_impl(self.algo_choice.value).default_camera(
            self.texture_panel.width,
            self.texture_panel.height,
        )

    def handle_resize(self, vp_width: int, vp_height: int) -> None:
        """Handle a resize event, keeping the view center fixed."""
        # remember the center before resize
        cx, cy = self.camera.center_xy()

        self.texture_panel.resize(vp_width, vp_height)
        self.camera.width = self.texture_panel.width
        self.camera.height = self.texture_panel.height

        # re-anchor origin so the center stays put
        self.camera.origin_x = cx + self.camera.width * self.camera.scale / 2
        self.camera.origin_y = cy + self.camera.height * self.camera.scale / 2

    def replace_algo(self, new_algo: str) -> None:
        """Replace the current algorithm with a new one."""
        self.algo_choice = AlgoChoice(new_algo)
        self.algo_params = self.algo_choice.get_algo_params(new_algo)
        self.reset_camera()

    def enable_movement_camera(self) -> None:
        """Enable movement-induced camera downscaling."""
        self.camera_params.movement_enabled_downscaling = True

    def disable_movement_camera(self) -> None:
        """Disable movement-induced camera downscaling."""
        self.camera_params.movement_enabled_downscaling = False

    def get_algo_lut_limit(self) -> int:
        """Get either `max_iter` or `num_points` from the algorithm parameters."""
        has_max_iter = has_member(self.algo_params.__class__, "max_iter")
        has_num_points = has_member(self.algo_params.__class__, "num_points")

        if not has_max_iter and not has_num_points:
            msg = "algorithm must have either max_iter or num_points"
            raise ValueError(msg)

        if has_max_iter:  # can be downscaled
            lut_limit = self.algo_params.max_iter  # type: ignore[reportAttributeAccessIssue]
        else:  # cannot be downscaled
            lut_limit = self.algo_params.num_points  # type: ignore[reportAttributeAccessIssue]

        return lut_limit

    def generate_animation(self) -> str:
        """Generate an animation file from the current animation keyframes."""
        # no animation can be generated when there aren't enough keyframes
        if len(self.animation_params.keyframes) <= 1:
            return "not enough keyframes to proceed"

        algo_impl = AlgoChoice.get_algo_impl(self.algo_choice.value)
        lut_limit = self.get_algo_lut_limit()

        frames = []

        match self.animation_params.animation_mode:
            case AnimationMode.LINEAR:
                interp_func = interpolate_linear
            case AnimationMode.SPLINE:
                interp_func = interpolate_catmull_rom
            case _x:
                msg = f"unknown animation mode: {_x}"
                raise ValueError(msg)

        interpolated_cams = interp_func(
            list(self.animation_params.keyframes),
            self.animation_params.frame_rate,
        )
        for cam in interpolated_cams:
            lattice = algo_impl.generate_frame(cam, self.algo_params)
            luttice = self.colour_params.apply_lut(lattice, lut_limit)
            frames.append(luttice)

        export_format = self.animation_params.export_format
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # noqa: DTZ005
        fps = self.animation_params.frame_rate

        match export_format:
            case ExportFormat.GIF:
                filename = f"{timestamp}.gif"
                filepath = GIF_FOLDER / filename
                frame_imgs = list(map(Image.fromarray, frames))
                frame_imgs[0].save(
                    filepath,
                    save_all=True,
                    append_images=frame_imgs[1:],
                    duration=int(1000 / fps),
                    loop=0,
                )
            case ExportFormat.MP4:
                filename = f"{timestamp}.mp4"
                filepath = MP4_FOLDER / filename
                iio.imwrite(
                    filepath,
                    frames,
                    fps=fps,
                    codec="libx264",
                    macro_block_size=1,
                )
            case ExportFormat.WEBM:
                filename = f"{timestamp}.webm"
                filepath = WEBM_FOLDER / filename
                iio.imwrite(
                    filepath,
                    frames,
                    fps=fps,
                    codec="libvpx-vp9",
                    macro_block_size=1,
                    output_params=["-crf", "30"],
                )
            case _x:
                msg = f"unknown export format: {_x}"
                raise ValueError(msg)

        return f"saved {filename}"

    def generate_frame(self) -> LUTtice:
        """Generate a frame of a chosen fractal algorithm."""
        algo_impl = AlgoChoice.get_algo_impl(self.algo_choice.value)
        has_max_iter = has_member(self.algo_params.__class__, "max_iter")
        lut_limit = self.get_algo_lut_limit()

        if (
            self.camera_params.movement_enabled_downscaling is True
            and self.camera_params.user_enabled_downscaling is True
            and has_max_iter
        ):
            max_iter = min(
                lut_limit,
                self.camera_params.iteration_limit,
            )

            temp_cam = replace(
                self.camera,
                width=self.camera.width // self.camera_params.downscale_factor,
                height=self.camera.height // self.camera_params.downscale_factor,
                scale=self.camera.scale * self.camera_params.downscale_factor,
            )

            temp_algo_params = replace(
                self.algo_params,  # type: ignore[reportAttributeAccessIssue]
                max_iter=max_iter,
            )

            small_lat = algo_impl.generate_frame(temp_cam, temp_algo_params)
            lattice = upscale_lat(
                small_lat,
                self.camera_params.downscale_factor,
                self.camera.width,
                self.camera.height,
            )
        else:
            lattice = algo_impl.generate_frame(self.camera, self.algo_params)

        return self.colour_params.apply_lut(lattice, lut_limit)
