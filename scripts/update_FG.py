import env_setup  # noqa
from Updater import Updater


session = Updater()
session.update_reflex()
session.compare_inventories()
del session
