import env_setup  # noqa
from Updater import Updater


if __name__ == "__main__":
    session = Updater()
    session.update_reflexes()
    session.update_MC_index()
    session.compare_inventories()
    session.export()
    del session
