import pexpect
import time
import os
import datetime
import sys
import threading

class Locked:
    def __init__(self, obj):
        self._obj = obj
        self._lock = threading.Lock()
    def __enter__(self):
        self._lock.acquire()
        return self._obj
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

data_dir = "data/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.mkdir(data_dir)

PHASE_INIT = 0
PHASE_START_APP = 1
PHASE_LOOP = 2
phases = Locked({0: PHASE_INIT, 1: PHASE_INIT})

use_rme = True
if len(sys.argv) == 2 and sys.argv[1] == "--no-rme":
    use_rme = False

def handle_firmware(port):
    child = pexpect.spawn(
        f"socat -,rawer TCP-LISTEN:{port},fork",
        encoding="utf-8",
        codec_errors="ignore",
        timeout=10,
    )
    child.logfile = open(f"{data_dir}/output-firmware.txt", "w")
    child.expect(pexpect.EOF, timeout=None)


def handle_secure(port):
    child = pexpect.spawn(
        f"socat -,rawer TCP-LISTEN:{port},fork",
        encoding="utf-8",
        codec_errors="ignore",
        timeout=10,
    )
    child.logfile = open(f"{data_dir}/output-secure.txt", "w")
    child.expect(pexpect.EOF, timeout=None)

def sleep(child: pexpect.spawn, sec):
    try:
        child.expect(pexpect.EOF, timeout=sec)
    except:
        pass

def handle_host(host_id, port):
    child = pexpect.spawn(
        f"socat -,rawer TCP-LISTEN:{port},fork",
        encoding="utf-8",
        codec_errors="ignore",
        timeout=10,
    )
    child.logfile = open(f"{data_dir}/output-host-{host_id}.txt", "w")
    child.expect("buildroot login:", timeout=None)
    child.sendline("root")
    child.expect("#", timeout=None)

    base_cmd = "./gen-run-vmm.sh --kvmtool --tap --extcon "
    if not use_rme:
        base_cmd += "--no-rme "

    if host_id == 0:
        cmd = "RECLAIM_MERGED_PAGES=1 "
        cmd += "GUEST_TTY=/dev/hvc3 "
        cmd += "EXTRA_KPARAMS='arm_cca_guest.is_victim=0' "
        cmd += base_cmd
        child.sendline(cmd)
    elif host_id == 1:
        cmd = "GUEST_TTY=/dev/hvc4 "
        cmd += "EXTRA_KPARAMS='arm_cca_guest.is_attacker=0' "
        cmd += base_cmd
        child.sendline(cmd)
    elif host_id == 2:
        child.sendline("/mnt/mem.sh")
        while True:
            with phases as _phases:
                if _phases[0] >= PHASE_START_APP and _phases[1] >= PHASE_START_APP:
                    break
            sleep(child, 0.3)
        child.sendline("Started app")
        while True:
            with phases as _phases:
                if _phases[0] >= PHASE_LOOP and _phases[1] >= PHASE_LOOP:
                    break
            sleep(child, 0.3)
        sleep(child, 3)
        child.sendline("Entered loop")
    child.expect(pexpect.EOF, timeout=None)


def handle_realm(realm_id, port):
    child = pexpect.spawn(
        f"socat -,rawer TCP-LISTEN:{port},fork",
        encoding="utf-8",
        codec_errors="ignore",
        timeout=10,
    )
    child.logfile = open(f"{data_dir}/output-realm-{realm_id}.txt", "w")
    child.expect("buildroot login:", timeout=None)
    child.sendline("root")
    child.expect("#", timeout=None)
    child.sendline("mount -t 9p -o trans=virtio,version=9p2000.L shr1 /mnt")
    child.expect("#", timeout=None)
    #child.sendline(f"cat /proc/kallsyms > /mnt/{data_dir}/realm-{realm_id}-kallsyms.txt")
    #child.expect("#", timeout=None)
    child.sendline("/mnt/gtest")
    with phases as _phases:
        _phases[realm_id] = PHASE_START_APP
    child.expect("Entering infinite loop...", timeout=None)
    with phases as _phases:
        _phases[realm_id] = PHASE_LOOP
    child.expect(pexpect.EOF, timeout=None)

threading.Thread(target=handle_firmware, args=(54320,)).start()
threading.Thread(target=handle_secure, args=(54321,)).start()
threading.Thread(target=handle_host, args=(0, 54322)).start()
threading.Thread(target=handle_host, args=(1, 54323)).start()
threading.Thread(target=handle_host, args=(2, 54324)).start()
threading.Thread(target=handle_realm, args=(0, 54325)).start()
threading.Thread(target=handle_realm, args=(1, 54326)).start()
