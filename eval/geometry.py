"""
Overlay Geometry Engine for PrivateEye.

Provides mathematically exact coordinate mapping from source screenshot space
into display space when using CSS object-fit: contain (letterboxing / pillarboxing).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ContainmentGeometry:
    scale: float
    display_width: float
    display_height: float
    offset_x: float
    offset_y: float


@dataclass(frozen=True)
class TransformedBox:
    left: float
    top: float
    width: float
    height: float

    def to_dict(self) -> dict[str, float]:
        return {
            "left": round(self.left, 2),
            "top": round(self.top, 2),
            "width": round(self.width, 2),
            "height": round(self.height, 2),
        }


def calculate_containment(
    container_width: float,
    container_height: float,
    source_width: float,
    source_height: float,
) -> ContainmentGeometry:
    """
    Computes uniform scale factor and centering offsets for an image
    contained within an arbitrary container (aspect-ratio preserving).
    """
    if container_width <= 0 or container_height <= 0 or source_width <= 0 or source_height <= 0:
        return ContainmentGeometry(
            scale=1.0,
            display_width=container_width,
            display_height=container_height,
            offset_x=0.0,
            offset_y=0.0,
        )

    scale = min(container_width / source_width, container_height / source_height)
    display_width = source_width * scale
    display_height = source_height * scale
    offset_x = (container_width - display_width) / 2.0
    offset_y = (container_height - display_height) / 2.0

    return ContainmentGeometry(
        scale=scale,
        display_width=display_width,
        display_height=display_height,
        offset_x=offset_x,
        offset_y=offset_y,
    )


def transform_bounding_box(
    x: float,
    y: float,
    width: float,
    height: float,
    geom: ContainmentGeometry,
) -> TransformedBox:
    """
    Transforms bounding box coordinates from source space into container display space.
    """
    return TransformedBox(
        left=x * geom.scale + geom.offset_x,
        top=y * geom.scale + geom.offset_y,
        width=width * geom.scale,
        height=height * geom.scale,
    )
