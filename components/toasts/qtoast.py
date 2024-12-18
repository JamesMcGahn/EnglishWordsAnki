from PySide6.QtGui import QColor, QFont

from .pyqttoast import Toast, ToastPosition, ToastPreset


class QToast(Toast):
    def __init__(self, parent, status, title, message):
        super().__init__()
        self.setDuration(5000)
        self.message = message
        self.title = title
        self.status = status

        font = QFont([".AppleSystemUIFont"], 12, QFont.Weight.Bold)
        self.setTitleFont(font)
        self.setTextFont(font)

        match (self.status):
            case "SUCCESS":
                self.applyPreset(ToastPreset.SUCCESS)
            case "ERROR":
                self.applyPreset(ToastPreset.ERROR)
            case "WARN":
                self.applyPreset(ToastPreset.WARNING)
            case "INFO":
                self.applyPreset(ToastPreset.INFORMATION)
            case "CLOSE":
                self.applyPreset(ToastPreset.CLOSE)
            case _:
                self.applyPreset(ToastPreset.INFORMATION)

        self.setTextColor(QColor("#ffffff"))
        self.setTitleColor(QColor("#FFFFFF"))
        self.setBackgroundColor(QColor("#003366"))
        self.setDurationBarColor(QColor("#00A8E8"))
        self.setIconSeparatorColor(QColor("#00A8E8"))
        self.setIconColor(QColor("#00A8E8"))
        self.setCloseButtonIconColor(QColor("#00A8E8"))
        self.setMinimumWidth(300)
        self.setMaximumWidth(350)
        self.setMinimumHeight(55)
        self.setBorderRadius(3)
        self.setPosition(ToastPosition.BOTTOM_RIGHT)
        self.setTitle(self.title)
        self.setText(self.message)
        self.show()
