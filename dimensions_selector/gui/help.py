import os

from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt.QtGui import QDesktopServices


def openHelp():
    locale = QSettings().value('locale/userLocale')[0:2]
    if locale not in ("fr"):
        locale = "en"

    index_path = os.path.join(os.path.dirname(__file__), "..", "help", locale, "index.html")

    QDesktopServices.openUrl(QUrl.fromLocalFile(index_path))
