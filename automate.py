import pexpect
import multiprocessing
import time
import os
import datetime

data_dir = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.mkdir(data_dir)


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
    if host_id == 0:
        child.sendline("RECLAIM_MERGED_PAGES=1 "
                       "GUEST_TTY=/dev/hvc3 "
                       "EXTRA_KPARAMS='arm_cca_guest.is_attacker=0' "
                       "./gen-run-vmm.sh --kvmtool --tap --extcon")
    elif host_id == 1:
        child.sendline("GUEST_TTY=/dev/hvc4 "
                       "EXTRA_KPARAMS='arm_cca_guest.is_attacker=1' "
                       "./gen-run-vmm.sh --kvmtool --tap --extcon")
    elif host_id == 2:
        time.sleep(3)
        child.sendline("/mnt/mem.sh")
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
    child.sendline("/mnt/gtest")
    child.expect(pexpect.EOF, timeout=None)

multiprocessing.Process(target=handle_firmware, args=(54320,)).start()
multiprocessing.Process(target=handle_secure, args=(54321,)).start()
multiprocessing.Process(target=handle_host, args=(0, 54322)).start()
multiprocessing.Process(target=handle_host, args=(1, 54323)).start()
multiprocessing.Process(target=handle_host, args=(2, 54324)).start()
multiprocessing.Process(target=handle_realm, args=(0, 54325)).start()
multiprocessing.Process(target=handle_realm, args=(1, 54326)).start()
