import os

def start():
    os.system("echo 0 > /proc/sys/kernel/lock_stat")
    os.system("echo 0 > /proc/lock_stat")
    os.system("echo 1 > /proc/sys/kernel/lock_stat")

def stop():
    os.system("echo 0 > /proc/sys/kernel/lock_stat")

def get(dest_file, head=False):
    if head == True:
        fp = os.popen("grep : /proc/lock_stat | head")
    else:
        fp = os.popen("cat /proc/lock_stat")
    text = fp.read()
    fp.close()
    fp = open(dest_file, "w")
    fp.write(text)
    fp.close()