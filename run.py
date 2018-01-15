from pkg.test import Test
from pkg.analysis import Analysis

device = "/dev/sdb"
result_dir = "/home/result"


if __name__ == "__main__":
    # prepare(os.path.join(os.getcwd(), "image_built"))
    fs = "ext4"
    print(fs + 64 * "*")
    test = Test(device, fs, "/mnt", result_dir, scale_test=True, direct_io=False)
    test.start()
    # res = Analysis(result_dir)
    # res.start()