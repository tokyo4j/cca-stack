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

no_rme = False
if len(sys.argv) == 2 and sys.argv[1] == "--no-rme":
    no_rme = True

phase_msgs = [
    "AppStart",
    "AllocStart",
    "AllocEnd",
]
if no_rme:
    phase_msgs += ["KsmStart"]
else:
    phase_msgs += ["MadviseStart", "MadviseEnd"]
phase_msgs += ["LoopStart"]

phases = Locked({0: -1, 1: -1}) # -1: initial phase

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
    except:  # noqa: E722
        pass

def wait_for_state(child: pexpect.spawn, state):
    while True:
        with phases as _phases:
            if _phases[0] >= state and _phases[1] >= state:
                break
        sleep(child, 0.3)

def set_state(realm_id, state):
    with phases as _phases:
        _phases[realm_id] = state

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
    if no_rme:
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
        for i, msg in enumerate(phase_msgs):
            wait_for_state(child, i)
            child.sendline(msg)

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
    cmd = "/mnt/gtest"
    if no_rme:
        cmd += " --no-rme"
    child.sendline(cmd)
    #cmd = "/mnt/llama.cpp/build/bin/llama-cli -m /mnt/llama.cpp/ggml-model-q4_0.gguf -i"
    for i, msg in enumerate(phase_msgs):
        child.expect(msg, timeout=None)
        set_state(realm_id, i)

    child.expect(pexpect.EOF, timeout=None)

threading.Thread(target=handle_firmware, args=(54320,)).start()
threading.Thread(target=handle_secure, args=(54321,)).start()
threading.Thread(target=handle_host, args=(0, 54322)).start()
threading.Thread(target=handle_host, args=(1, 54323)).start()
threading.Thread(target=handle_host, args=(2, 54324)).start()
threading.Thread(target=handle_realm, args=(0, 54325)).start()
threading.Thread(target=handle_realm, args=(1, 54326)).start()
