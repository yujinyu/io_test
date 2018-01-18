from pkg.test import Test

device = "/dev/sdb"
result_dir = "/home/result"


if __name__ == "__main__":
    fs = "ext4"
    test = Test(device, fs, "/mnt", result_dir)
    test.start()