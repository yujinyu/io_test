import os
import time
import docker
from random import Random
from pkg.lockstat import start as lockstat_start, stop as lockstat_stop, get as get_lockstat
from pkg.cpu import get_num_of_cpus

image = "test:cpu-bound"
cpu_flag = ["0","1"]
m_limit = "4g"

def random_string(llen=6):
    string = ""
    chars = "AaBbCDdEeFfGgHhJKkLMmNnPpQqRrSTtUuVvWwXxYy3456789"
    length = len(chars) - 1
    random = Random()
    for l in range(llen):
        string += chars[random.randint(0, length)]
    return string


def build_image(path2dockerfile, client=docker.from_env()):
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


def whether_wait(clt):
    cntrs_list = clt.containers.list()
    if len(cntrs_list) <= 0:
        return False
    return True


def rm_cntrs(clt):
    cntrs_list = clt.containers.list(all=True)
    for cid in cntrs_list:
        cid.remove()


class Test:
    # rw_mode
    # fio: write , read
    # sysbench: seqwr, seqrd
    # iozone:  -i  x
    #  0=write/rewrite, 1=read/re-read, 2=random-read/write,  3=Read-backwards
    #  4=Re-write-record, 5=stride-read,  6=fwrite/re-fwrite,  7=fread/Re-fread
    #  8=random mix, 9=pwrite/Re-pwrite, 10=pread/Re-pread
    # 11=pwritev/Re-pwritev, 12=preadv/Re-preadv

    def __init__(self, storage_device, fs_type, mount_point, result_dir, scale_test, direct_io=True):
        self._client = docker.from_env()
        self._device = storage_device
        self._fs_type = fs_type
        self._mnt_point = mount_point
        self._result_directory = result_dir
        self._scale_test = scale_test
        self._io_flag = direct_io
        self._max_num = get_num_of_cpus() + 1
        self._saved_image = "%s.tar" % image.replace(":", "-")
        self._res_dirs = []

    def _pre_work(self):
        docker_svc_stop()
        mkfs_mnt(self._device, self._fs_type, "/var/lib/docker")
        os.system("systemctl restart docker")
        print(os.getcwd())
        build_image(os.path.join(os.getcwd(),"image_built"))

    # def _crt_run(self, rng, cmd, volume):


    # def _ex_test(self, cmd, vol, rng, scale_test=True):


    def start(self):
        self._pre_work()
