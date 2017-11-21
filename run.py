import os
import docker
from pkg.test import Test, build_image, image

device = "/dev/sdb"
result_dir = "/home/result"
fs_type = ["ext4", "ext4nj", "btrfs", "xfs", "zfs"]


def prepare(path2dockerfile):
    client = docker.from_env()
    os.system("docker load -i %s" % os.path.join(os.getcwd(), "pkg/fedora26.tar"))
    build_image(path2dockerfile, image, client)
    os.system("docker save %s -o %s" % (image, os.path.join(os.getcwd(), "pkg/%s.tar" % image.replace(":", "-"))))


if __name__ == "__main__":
    prepare(os.path.join(os.getcwd(), "image_built"))
    for fs in fs_type:
        print(fs+64*"*")
        io_test = Test(device, fs, "/mnt", result_dir)
        io_test.start()
