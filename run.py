import os
import time
import docker
from pkg.test import Test, build_image, image, fs_type
from pkg.analysis import Analysis

device = "/dev/sdb"
result_dir = "/home/result"


def prepare(path2dockerfile):
    client = docker.from_env()
    os.system("docker load -i %s" % os.path.join(os.getcwd(), "pkg/fedora26.tar"))
    build_image(path2dockerfile, image, client)
    os.system("docker save %s -o %s" % (image, os.path.join(os.getcwd(), "pkg/%s.tar" % image.replace(":", "-"))))


if __name__ == "__main__":
    # prepare(os.path.join(os.getcwd(), "image_built"))
    # for fs in fs_type:
    #    print(fs + 64 * "*")
    #    io_test = Test(device, fs, "4k", "/mnt", result_dir, False, True)
    #    io_test.start()
    res = Analysis(result_dir, True)
    res.start()
    # os.system("mv %s /home/Test/result-%s" % (result_dir, time.strftime('%y%m%d%H%M%S', time.localtime(time.time()))))

