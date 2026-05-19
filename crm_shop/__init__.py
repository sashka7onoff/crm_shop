import pymysql

pymysql.install_as_MySQLdb()

# Отключение проверки версии MySQL (для MySQL 5.7)
from django.db.backends.mysql.base import DatabaseWrapper
DatabaseWrapper.check_database_version_supported = lambda *a, **kw: None
