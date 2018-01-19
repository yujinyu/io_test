import os
import time
import docker
from random import Random
from pkg.cpu import get_num_of_cpus

image = "test:disk-bound"
cntr_name = "blkio-target"
rw = "write"
bs = "4k"
m_limit = "4g"


def random_string(le=6):
    string = ""
    chars = "AaBbCDdEeFfGgHhJKkLMmNnPpQqRrSTtUuVvWwXxYy3456789"
    length = len(chars) - 1
    random = Random()
    for l in range(le):
        string += chars[random.randint(0, length)]
    return string


def build_image(path2dockerfile, client):
    client.login(username="yy", password="12345678", registry="192.168.3.51:5000/admin")
    try:
        client.images.build(path=path2dockerfile, tag=image)
        print("Build image Successfully!")
    except Exception as e:
        print("Failed to build image!\n%s" % str(e))
        exit(-1)


def docker_svc_stop():
    if 0 == os.system("systemctl stop docker.service"):
        os.system("umount -lf $(cat /proc/mounts | grep docker | awk '{print $2}')")
        os.system("rm -rf /var/lib/docker/*")
        return 0
    else:
        print("Failed to stop docker daemon")
        return -1


def mkfs_mnt(dev, fs, mntpoint):
    if fs in ["ext4", "ext3", "ext2"]:
        os.system("echo \"y\" | mkfs.%s %s" % (fs, dev))
        os.system("mount -t %s %s %s" % (fs, dev, mntpoint))
    elif fs in ["f2fs", "xfs", "btrfs"]:
        os.system("mkfs.%s -f %s" % (fs, dev))
        os.system("mount -t %s %s %s" % (fs, dev, mntpoint))
    elif fs == "zfs":
        os.system("zpool create -f zfspool %s" % dev)
        os.system("zfs create -o mountpoint=%s zfspool/docker" % mntpoint)
    elif fs == "ext4nj":
        os.system("echo \"y\" | mkfs.ext4  %s" % dev)
        os.system("tune2fs -O ^has_journal %s" % dev)
        os.system("mount -t %s %s %s" % ("ext4", dev, mntpoint))
    else:
        print("unsupported fs %s" % fs)
        exit(-1)
    tfs = os.popen("df -T |grep %s |awk '{print$2}'" % mntpoint).read()
    if fs != "ext4nj":
        if str(tfs).replace('\n', '') != fs:
            exit(1)
    else:
        if str(tfs).replace('\n', '') != "ext4":
            exit(1)


class Test:
    def __init__(self, storage_device, fs_type, mount_point, result_dir):
        self._device = storage_device
        self._fs_type = fs_type
        self._mnt_point = mount_point
        self._result_directory = result_dir
        self._max_num = get_num_of_cpus() + 1
        result_directory = os.path.join(self._result_directory, "blkio-%s"%time.strftime("%y%m%d%H%M", time.localtime()))
        self.volume = {result_directory: self._mnt_point}
        self.client = docker.from_env()

    def _pre_work(self):
        build_image(os.path.join(os.getcwd(), "image_built"), self.client)

    def _create(self, command, cpu_shares, blkio_weight, name):
        self.client.containers.create(command=command,
                                      cpu_shares=cpu_shares,
                                      blkio_weight=blkio_weight,
                                      name=name,
                                      image=image,
                                      mem_limit=m_limit,
                                      volumes=self.volume,
                                      working_dir="/",
                                      detach=True)

    def _run(self):
        cntrs_list = self.client.containers.list(all=True)
        for cid in cntrs_list:
            cid.start()

    def _waiting_and_rm(self):
        cntrs_list = self.client.containers.list()
        while len(cntrs_list) > 0:
            cntr = self.client.containers.get(cntr_name)
            if cntr.status != "running":
                for cid in cntrs_list:
                    cid.stop()
            time.sleep(30)
            cntrs_list = self.client.containers.list()
        self._remove()

    def _remove(self):
        cntrs_list = self.client.containers.list(all=True)
        for cid in cntrs_list:
            cid.remove()

    def start(self):
        self._pre_work()
        self._remove()
        self._create(command="./run.sh %s %s %s-%s-%s-res" % (rw, bs, "1", rw, bs),
                     cpu_shares=8,
                     blkio_weight=1000,
                     name=cntr_name)
        self._run()
        self._waiting_and_rm()

        for i in range(0, 1):
            for j in range(0, i):
                self._create(command="./run.sh %s %s res-%s-%s-%s-%s" % (rw, bs, str(i), str(j + 1), rw, bs),
                             cpu_shares=2,
                             blkio_weight=80,
                             name=random_string(8))
            self._create(command="./run.sh %s %s %s-%s-%s-res" % (rw, bs, str(i), rw, bs),
                         cpu_shares=8,
                         blkio_weight=625,
                         name=cntr_name)
            self._run()
            self._waiting_and_rm()
