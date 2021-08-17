from pkg_resources import resource_filename

from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt.QtGui import QDesktopServices


def openHelp():
    locale = QSettings().value('locale/userLocale')[0:2]
    if locale not in ("fr"):
        locale = "en"

    index_path = resource_filename("dimensions_selector", "help/{}/index.html".format(locale))

    QDesktopServices.openUrl(QUrl.fromLocalFile(index_path))
