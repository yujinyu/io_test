import os
import time
import docker
from pkg.test import Test, build_image, image, fs_type
from pkg.analysis import Analysis

device = "/dev/sdb"
result_dir = "/home/result"
# blocksize = ["4k", "8k", "16k", "1m"]
blocksize = ["8k"]
# blocksize = ["512k", "1m", "4m"]


def prepare(path2dockerfile):
    client = docker.from_env()
    os.system("docker load -i %s" % os.path.join(os.getcwd(), "pkg/fedora26.tar"))
    build_image(path2dockerfile, image, client)
    os.system("docker save %s -o %s" % (image, os.path.join(os.getcwd(), "pkg/%s.tar" % image.replace(":", "-"))))


if __name__ == "__main__":
    # prepare(os.path.join(os.getcwd(), "image_built"))
    for bs in blocksize:
        print(bs + 80 * "*")
        for fs in fs_type:
            print(fs + 64 * "*")
            io_test = Test(device, fs, bs, "/mnt", result_dir, scale_test=True, direct_io=False)
            io_test.start()
        # res = Analysis(result_dir, scale_test=True)
        # res.start()
        # os.system(
        #    "mv %s /home/Test/result-%s-%s" % (
        #         result_dir, bs, time.strftime('%y%m%d%H%M%S', time.localtime(time.time()))))
