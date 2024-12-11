from typing import Union

from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QApplication, QGraphicsDropShadowEffect, QWidget


class StyleHelper:

    @staticmethod
    def drop_shadow(
        parent,
        blur_radius=5,
        x_offset=3,
        y_offset=3,
        color: Union[str, QColor] = None,
    ):
        if color is None:
            color = QColor(0, 0, 0, 60)

        shadow_effect = QGraphicsDropShadowEffect(parent)
        shadow_effect.setBlurRadius(blur_radius)
        shadow_effect.setXOffset(x_offset)
        shadow_effect.setYOffset(y_offset)
        shadow_effect.setColor(QColor(color))
        parent.setGraphicsEffect(shadow_effect)

    @staticmethod
    def dpi_scale_set_font(
        parent: Union[QApplication, QWidget],
        font_family: str = "Open Sans",
        font_size: int = 12,
    ):

        if isinstance(parent, QApplication):
            screen = parent.primaryScreen()
        else:
            screen = parent.screen()

        logical_dpi = screen.logicalDotsPerInch() / 96.0
        font = QFont(font_family)

        adjusted_font_size = font_size * logical_dpi
        font.setPointSizeF(adjusted_font_size)

        parent.setFont(font)
