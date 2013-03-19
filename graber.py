import multiprocessing
import traceback


from uatrains.engine import drv


def grab():
    with multiprocessing.Pool(processes=32) as ppool:
        #ppool.map(drv.odessa.get_train_data, [tid for tid in range(0, 5000)])
        ppool.map(drv.southwest.get_train_data, [tid for tid in range(0, 5000)])
        ppool.map(drv.passengers.get_train_data, [tid for tid in range(20000, 70000)])