import os
import time
import docker
from random import Random

image = "iotest:allinone"


def random_string(llen=6):
    string = ""
    chars = "AaBbCDdEeFfGgHhJKkLMmNnPpQqRrSTtUuVvWwXxYy3456789"
    length = len(chars) - 1
    random = Random()
    for l in range(llen):
        string += chars[random.randint(0, length)]
    return string


def build_image(path2dockerfile, img, client=docker.from_env()):
    try:
        client.images.build(path=path2dockerfile, tag=img)
        print("Build img Successfully!")
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
    _type = ["fio", "iozone","sysbench"]

    # rw_mode
    # fio: write , read
    # sysbench: seqwr, seqrd
    # iozone:  -i  x
    #  0=write/rewrite, 1=read/re-read, 2=random-read/write,  3=Read-backwards
    #  4=Re-write-record, 5=stride-read,  6=fwrite/re-fwrite,  7=fread/Re-fread
    #  8=random mix, 9=pwrite/Re-pwrite, 10=pread/Re-pread
    # 11=pwritev/Re-pwritev, 12=preadv/Re-preadv
    _rw_mode = {"fio": ["write", "read"], "sysbench": ["seqwr", "seqrd"], "iozone": ["0", "1"]}

    def __init__(self, storage_device, fs_type, mount_point, result_dir, io_flag=True):
        self._client = docker.from_env()
        self._device = storage_device
        self._fs_type = fs_type
        self._mnt_point = mount_point
        self._result_directory = result_dir
        self._io_flag = io_flag
        self._saved_image = "%s.tar" % image.replace(":", "-")

    def _pre_work(self):
        docker_svc_stop()
        mkfs_mnt(self._device, self._fs_type, "/var/lib/docker")
        os.system("systemctl restart docker")
        os.system("docker load -i %s" % os.path.join(os.getcwd(), "pkg", self._saved_image))

    def _crt_run(self, tools_type, rw, rng, cmd, volume):
        res_prefix = os.path.join(self._mnt_point, "%s-%s-%s-" % (self._fs_type, rw, str(rng)))
        for j in range(1, rng + 1):
            command = cmd + res_prefix + random_string(8)
            if tools_type is "iozone":
                command = command + ".xls"
            print(command)
            print(volume)
            self._client.containers.create(image=image, command=command, volumes=volume, working_dir="/test/")
        cntrs_list = self._client.containers.list(all=True)
        for cid in cntrs_list:
            cid.start()

    def _ex_test(self, tools_type, rw, cmd, vol, rng, spec=False):
        if not spec:
            for i in range(1, rng):
                self._crt_run(tools_type, rw, i, cmd, vol)
                while whether_wait(self._client):
                    time.sleep(30)
                rm_cntrs(self._client)
        else:
            self._crt_run(tools_type, rw, rng, cmd, vol)
            while whether_wait(self._client):
                time.sleep(30)
            rm_cntrs(self._client)

    def start(self):
        self._pre_work()
        for tool in self._type:
            print(tool + 32 * "%")
            result_directory = os.path.join(self._result_directory, tool)
            volume = {result_directory: self._mnt_point}
            os.system("mkdir  -p  %s" % result_directory)
            rw = self._rw_mode[self._type[self._type.index(tool)]]
            parm2 = "128k"
            if tool is "iozone":
                parm1 = "%s@-i@%s" % (rw[0], rw[1])
                if self._io_flag:
                    parm1 = parm1 + "@-I"
                print(parm1)
                cmd = "./run %s %s %s " % (tool, parm1, parm2)
                self._ex_test(tool, "rw", cmd, volume, 16, True)
                continue
            elif tool is "fio":
                for rw_type in self._rw_mode[tool]:
                    print(rw_type + 16 * "#")
                    parm1 = "%s@-ioengine=sync" % rw_type
                    if self._io_flag:
                        parm1 = parm1 + "@-direct=1"
                    print(parm1)
                    cmd = "./run %s %s %s " % (tool, parm1, parm2)
                    self._ex_test(tool, rw_type, cmd, volume, 16, True)

            else:  # sysbench
                for rw_type in self._rw_mode[tool]:
                    print(rw_type + 16 * "#")
                    parm1 = "%s@--file-io-mode=sync" % rw_type
                    if self._io_flag:
                        parm1 = parm1 + "@--file-extra-flags=direct"
                    fp = open(os.path.join(os.getcwd(), "image_sys/Dockerfile"), "w")
                    fp.write("FROM %s\n" % image)
                    fp.write("MAINTAINER yujinyu\n")
                    fp.write("WORKDIR /test/\n")
                    fp.write(
                        "RUN sysbench --test=fileio --file-test-mode=%s --file-block-size=%s --file-total-size=2G prepare" % (
                        parm1.replace("@"," "), parm2))
                    fp.close()
                    build_image(os.path.join(os.getcwd(), "image_sys"), image, self._client)
                    cmd = "./run %s %s %s " % (tool, parm1, parm2)
                    self._ex_test(tool, rw_type, cmd, volume, 16, True)
