import os
import time
import docker
from random import Random

def random_string(length=6):
    string = ""
    chars = "AaBbCDdEeFfGgHhJKkLMmNnPpQqRrSTtUuVvWwXxYy3456789"
    length = len(chars) - 1
    random = Random()
    for l in range(length):
        string += chars[random.randint(0, length)]
    return string


def build_image(path2dockerfile, image, client=docker.from_env()):
    try:
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
    _type = ["fio", "sysbench", "iozone"]

    # rw_mode
    # fio: write , read
    # sysbench: seqwr, seqrd
    # iozone:  -i  x
    #  0=write/rewrite, 1=read/re-read, 2=random-read/write,  3=Read-backwards
    #  4=Re-write-record, 5=stride-read,  6=fwrite/re-fwrite,  7=fread/Re-fread
    #  8=random mix, 9=pwrite/Re-pwrite, 10=pread/Re-pread
    # 11=pwritev/Re-pwritev, 12=preadv/Re-preadv
    _rw_mode = {_type[0]: ["write", "read"], _type[1]: ["seqwr", "seqrd"], _type[2]: ["0", "1"]}

    def __init__(self, storage_device, fs_type, mount_point, dockerfile, result_dir):
        self._client = docker.from_env()
        self._device = storage_device
        self._fs_type = fs_type
        self._mnt_point = mount_point
        self._image = "filetest:%s" % fs_type
        self._path2dockerfile = dockerfile
        self._result_directory = result_dir

    def prepare(self):
        mkfs_mnt(self._device, self._fs_type, "/var/lib/docker")
        os.system("systemctl restart docker")
        self._client = docker.from_env()
        build_image(self._path2dockerfile, self._image, self._client)

    def run(self):
        for tool in self._type:
            result_directory = os.path.join(self._result_directory, tool)
            volume = {result_directory: self._mnt_point}
            # os.system("mkdir  -p  %s"%result_directory)
            if tool is "iozone":
                parm1 = "0 -i 1 -I "
                parm2 = "4k"
                continue
            for rw_type in self._rw_mode[tool]:
                res_file = os.path.join(self._mnt_point, "%s-%s-%s" % (self._fs_type, rw_type, random_string(8)))
                print("%s\n%s\n" % (result_directory, res_file))

    def _ex_test(self, tools_type, parm1, parm2, vol, rng, spec=False):
        if spec:
            for i in range(1, rng):
                while whether_wait(self._client):
                    time.sleep(30)
                rm_cntrs(self._client)
                for j in range(1, i + 1):
                    res_file = os.path.join(self._mnt_point, "%s-%s-%s" % (self._fs_type, "r&w", random_string(8)))
                    cmd = "%s.sh %s %s %s" % (self._type[self._type.index(tools_type)], parm1, parm2, res_file)
                    self._client.create(image=self._image, command=cmd, auto_remove=True, volume=vol)
                cntrs_list = self._client.containers.list(all=True)
                for cid in cntrs_list:
                    cid.star()
                print("%s-%s" % (tools_type, str(i)))
