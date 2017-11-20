import os
from pkg.test import Test

device = "/dev/sdb"
fs_type = ["ext4", "ext4nj", "btrfs", "xfs", "zfs"]
result_dir = "/home/result"

if __name__ == "__main__":
    for fs in fs_type:
        ext4_test = Test(device, fs, "/mnt", os.path.join(os.getcwd(), "image_built"), result_dir)
        # ext4_test.prepare()
        ext4_test.run()
