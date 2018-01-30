from pkg.test import Test
from pkg.analysis import Analysis

device = "/dev/sdb"
result_dir = "/home/result"


if __name__ == "__main__":
    test = Test("/mnt", result_dir, scale_test=True, direct_io=False)
    test.start()