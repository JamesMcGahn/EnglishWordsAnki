from typing import List, Tuple, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPaintEvent, QResizeEvent
from PySide6.QtWidgets import QDialog, QWidget


class GradientDialog(QDialog):
    """
    A custom QDialog that displays a gradient background.

    Args:
        gradient_colors (List[Tuple[float, Union[QColor, str]]]): A list of tuples where each tuple
            contains a float (position) and a QColor or str (color).
        parent (Optional[QWidget]): The parent widget of the dialog.
    """

    def __init__(
        self,
        gradient_colors: List[Tuple[float, Union[QColor, str]]],
        parent: QWidget = None,
    ):

        super().__init__(parent)
        self.gradient_colors = gradient_colors
        self.xStart = 0
        self.yStart = 0
        self.xStop = self.width()
        self.yStop = self.height()

        self.setMinimumHeight(300)
        self.setMinimumWidth(300)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Handle the paint event to draw the gradient background.

        Args:
            event (QPaintEvent): The paint event object.

        Returns:
            None: This function does not return a value.
        """
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(self.xStart, self.yStart, self.xStop, self.yStop)
        for position, color in self.gradient_colors:
            gradient.setColorAt(position, color)
        painter.setBrush(Qt.NoBrush)
        painter.fillRect(self.rect(), gradient)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Handle the resize event to adjust the gradient size proportionally to the new window size.

        Args:
            event (QResizeEvent): The resize event object.

        Returns:
            None: This function does not return a value.
        """

        width_ratio = self.width() / self.xStop if self.xStop != 0 else 1
        height_ratio = self.height() / self.yStop if self.yStop != 0 else 1

        new_xStart = self.xStart * width_ratio
        new_yStart = self.yStart * height_ratio
        new_xStop = self.xStop * width_ratio
        new_yStop = self.yStop * height_ratio

        self.set_gradient_start_stop(new_xStart, new_yStart, new_xStop, new_yStop)

        super().resizeEvent(event)

    def set_gradient_start_stop(
        self, xStart: float, yStart: float, xStop: float, yStop: float
    ) -> None:
        """
        Set the start and stop coordinates for the gradient.

        Args:
            xStart (float): The x-coordinate for the start of the gradient.
            yStart (float): The y-coordinate for the start of the gradient.
            xStop (float): The x-coordinate for the stop of the gradient.
            yStop (float): The y-coordinate for the stop of the gradient.

        Returns:
            None: This function does not return a value.
        """
        self.xStart = xStart
        self.yStart = yStart
        self.xStop = xStop
        self.yStop = yStop
        self.update()

    def show(self) -> int:
        """
        Show the dialog as a modal dialog.

        Returns:
            int: returns 0 if the dialog is rejected, 1 if it is accepted.
        """
        return self.exec()
