import pexpect
import os
import datetime
import sys
import time
import threading

childs: list[pexpect.spawn] = []

data_dir = "data/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.mkdir(data_dir)

no_rme = False
if len(sys.argv) == 2 and sys.argv[1] == "--no-rme":
    no_rme = True

def handle_firmware(port):
    child = pexpect.spawn(
        f"socat -,rawer TCP-LISTEN:{port},fork",
        encoding="utf-8",
        codec_errors="ignore",
        timeout=10,
    )
    childs.append(child)
    child.logfile = open(f"{data_dir}/output-firmware.txt", "w")
    child.expect(pexpect.EOF, timeout=None)


def handle_secure(port):
    child = pexpect.spawn(
        f"socat -,rawer TCP-LISTEN:{port},fork",
        encoding="utf-8",
        codec_errors="ignore",
        timeout=10,
    )
    childs.append(child)
    child.logfile = open(f"{data_dir}/output-secure.txt", "w")
    child.expect(pexpect.EOF, timeout=None)

def sleep(child: pexpect.spawn, sec):
    try:
        child.expect(pexpect.EOF, timeout=sec)
    except:  # noqa: E722
        pass

def handle_host(host_id, port):
    child = pexpect.spawn(
        f"socat -,rawer TCP-LISTEN:{port},fork",
        encoding="utf-8",
        codec_errors="ignore",
        timeout=10,
    )
    childs.append(child)
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
        cmd += "EXTRA_KPARAMS='arm_cca_guest.is_victim=1' "
        cmd += base_cmd
        child.sendline(cmd)
        child.expect("Reclaimed pa=", timeout=None)
        try:
            child.expect(pexpect.EOF, timeout=3)
        except:  # noqa: E722
            for c in childs:
                print(f"Terminating '{c.command}'")
                c.terminate(force=True)
                time.sleep(1)
            os._exit(0)
    elif host_id == 1:
        cmd = "GUEST_TTY=/dev/hvc4 "
        cmd += "EXTRA_KPARAMS='arm_cca_guest.is_attacker=1' "
        cmd += base_cmd
        child.sendline(cmd)
    elif host_id == 2:
        child.sendline("/mnt/mem.sh")

    child.expect(pexpect.EOF, timeout=None)


def handle_realm(realm_id, port):
    child = pexpect.spawn(
        f"socat -,rawer TCP-LISTEN:{port},fork",
        encoding="utf-8",
        codec_errors="ignore",
        timeout=10,
    )
    childs.append(child)
    child.logfile = open(f"{data_dir}/output-realm-{realm_id}.txt", "w")
    child.expect("buildroot login:", timeout=None)
    child.sendline("root")
    child.expect(pexpect.EOF, timeout=None)

def run_qemu():
    time.sleep(2)
    child = pexpect.spawn(
        "just run-qemu",
        encoding="utf-8",
        codec_errors="ignore",
        timeout=10,
    )
    childs.append(child)
    child.logfile = open(f"{data_dir}/output-qemu.txt", "w")
    child.expect(pexpect.EOF, timeout=None)

threading.Thread(target=handle_firmware, args=(54320,)).start()
threading.Thread(target=handle_secure, args=(54321,)).start()
threading.Thread(target=handle_host, args=(0, 54322)).start()
threading.Thread(target=handle_host, args=(1, 54323)).start()
threading.Thread(target=handle_host, args=(2, 54324)).start()
threading.Thread(target=handle_realm, args=(0, 54325)).start()
threading.Thread(target=handle_realm, args=(1, 54326)).start()
threading.Thread(target=run_qemu).start()
