from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon


class WidgetFactory:

    @staticmethod
    def create_icon(
        parent,
        file_location,
        width,
        height,
        checkable=False,
        file_location_2=None,
        exclusive=True,
    ):
        icon = QIcon()

        icon.addFile(
            file_location,
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )

        if checkable and file_location_2:
            icon.addFile(
                file_location_2,
                QSize(),
                QIcon.Mode.Normal,
                QIcon.State.On,
            )

        parent.setIcon(icon)
        parent.setIconSize(QSize(width, height))
        parent.setCheckable(checkable)
        parent.setAutoExclusive(exclusive)
        parent.setCursor(Qt.PointingHandCursor)
