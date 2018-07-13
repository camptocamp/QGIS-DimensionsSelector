# import qgis libs so that ve set the correct sip api version
import qgis   # pylint: disable=W0611  # NOQA

from qgis.testing import start_app
from qgis.testing.mocked import get_iface
from qgis import utils

QGIS_APP = start_app()
utils.iface = get_iface()

import pydevd
pydevd.settrace(suspend=False)
