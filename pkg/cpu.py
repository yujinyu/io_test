# -*- coding: UTF-8 -*-
import glob
import os

path_proc = "/proc/cpuinfo"
path_sys = "/sys/devices/system/cpu/"


#
# 判断s是否为数字
#
def _is_int(s):
    if s.isdigit():
        return int(s)
    return s


#
# 将CPU编号（例如，“1-4,8,11-12"）处理为编号列表，即[1,2,3,4,8,11,12]
#
def _parse_range(r):
    """
        Parse an integer sequence such as '0-3,8-11'.
        '' is the empty sequence.
    """
    if not r.strip():
        return []

    res = []
    for piece in r.strip().split(","):
        lr = piece.split("-")
        if len(lr) == 1 and lr[0].isdigit():
            res.append(int(lr[0]))
        elif len(lr) == 2 and lr[0].isdigit() and lr[1].isdigit():
            res.extend(range(int(lr[0]), int(lr[1]) + 1))
        else:
            raise ValueError("Invalid range syntax: %r" % r)
    return res


#
# 从/sys/devices/system/cpu/目录下获取相应的CPU信息，
# 例如name="online"可以获得当前主机启用的CPU编号
#
def get_cpus_parse_from_sys(name):
    return _parse_range(open(path_sys + name).read())


#
# 从/proc/cpuinfo获取启用的CPU的详细信息
#
def get_cpus_info_from_proc():
    """
        Read a cpuinfo file and return [{field : value}].
    """

    res = []
    for block in open(path_proc, "r").read().split("\n\n"):
        if len(block.strip()):
            res.append({})
            for line in block.splitlines():
                k, v = map(str.strip, line.split(":", 1))
                res[-1][k] = _is_int(v)
            # Try to get additional info
            processor = res[-1]["processor"]
            node_files = glob.glob(path_sys + "cpu%d/node*" % processor)
            if len(node_files):
                res[-1]["node"] = int(os.path.basename(node_files[0])[4:])
    return res


#
# 启用或者禁用编号为cpuid的CPU，其中onoff为1表示启用，0则表示禁用
#
def set_cpu_onoff(cpuid, onoff):
    res = _parse_range(cpuid)
    for ids in res:
        fp = open(path_sys + "cpu%d/online" % int(ids), "w")
        print(onoff, file=fp)
        fp.close()


#
# 获取主机CPU的总个数
#
def get_num_of_cpus():
    return len(_parse_range(open(path_sys + "present").read()))
