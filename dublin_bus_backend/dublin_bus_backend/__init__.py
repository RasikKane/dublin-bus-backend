# Required pymysql as no sql db module was compatible with django 3

import pymysql

pymysql.version_info = (1, 3, 13, "final", 0)
pymysql.install_as_MySQLdb()
