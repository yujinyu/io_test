import os
import docker
from random import Random


# fs_type = ["ext4", "ext4nj", "btrfs", "xfs", "zfs"]

def random_string(length=6):
    string = ""
    chars = "AaBbCDdEeFfGgHhJKkLMmNnPpQqRrSTtUuVvWwXxYy3456789"
    length = len(chars) - 1
    random = Random()
    for l in range(length):
        string += chars[random.randint(0, length)]
    return string

def build_image(path2dockerfile, image):
    try:
        client = docker.from_env()
        client.images.build(path=path2dockerfile, tag=image)
        print("Build image Successfully!")
    except Exception as e:
        print("Failed to build image!\n%s" % str(e))
        exit(-1)

def mkfs_mnt(dev, fs, mntpoint):
    if fs in ["ext4", "ext3", "ext2"]:
        os.system("echo \"y\" | mkfs.%s %s" % (fs, dev))
        os.system("mount -t %s %s %s" % (fs, dev, mntpoint))
    elif ["f2fs", "xfs", "btrfs"]:
        os.system("mkfs.%s -f %s" % (fs, dev))
        os.system("mount -t %s %s %s" % (fs, dev, mntpoint))
    elif fs == "zfs":
        os.system("zpool create -f zfspool %s" % dev)
        os.system("zfs create -o mountpoint=%s zfspool/docker" % mntpoint)
    elif "ext4nj":
        os.system("echo \"y\" | mkfs.ext4  %s" % dev)
        os.system("tune2fs -O ^has_journal %s" % dev)
        os.system("mount -t %s %s %s" % (fs, dev, mntpoint))
    else:
        print("unsupported fs %s" % fs)
        return -1
    return 0

class Test:
    type = ["fio", "sysbench", "iozone"]
    # rw_mode
        # fio: write , read
        #sysbench: seqwr, seqrd
        #iozone:  -i  x
            #  0=write/rewrite, 1=read/re-read, 2=random-read/write,  3=Read-backwards
            #  4=Re-write-record, 5=stride-read,  6=fwrite/re-fwrite,  7=fread/Re-fread
            #  8=random mix, 9=pwrite/Re-pwrite, 10=pread/Re-pread
            # 11=pwritev/Re-pwritev, 12=preadv/Re-preadv

    def __init__(self, storage_device, fs_type, mount_point, dockerfile, result_dir):
        self.device = storage_device
        self.fs_type = fs_type
        self.mnt_point = mount_point
        self.image = "filetest:%s" % fs_type
        self.path2dockerfile = dockerfile
        self.result_directory = result_dir
        self.volume = {result_dir: "/mnt"}

    def prepare(self):
        mkfs_mnt(self.device, self.fs_type, self.mnt_point)
        build_image(self.path2dockerfile, self.image)

    def run(self):
        for tool in self.type:

            pass
