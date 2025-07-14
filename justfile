#git clone https://github.com/tokyo4j/linux -b cca-host/v7
[working-directory: 'linux']
linux-setup $CROSS_COMPILE='aarch64-linux-gnu-' $ARCH='arm64':
  mkdir -p build
  make O=./build defconfig
  scripts/config --file build/.config \
    -e VIRT_DRIVERS \
    -e ARM_CCA_GUEST \
    -e CONFIG_HZ_100 \
    -d CONFIG_HZ_250 \
    -e CONFIG_MACVLAN \
    -e CONFIG_MACVTAP \
    -d CONFIG_DRM

[working-directory: 'linux']
linux $CROSS_COMPILE='aarch64-linux-gnu-' $ARCH='arm64':
  make O=./build -j16 Image

[working-directory: 'linux']
linux-llvm $CROSS_COMPILE='aarch64-linux-gnu-' $ARCH='arm64':
  mkdir -p build-llvm
  make O=./build-llvm defconfig
  scripts/config --file build-llvm/.config \
    -e VIRT_DRIVERS \
    -e ARM_CCA_GUEST \
    -e CONFIG_HZ_100 \
    -d CONFIG_HZ_250 \
    -e CONFIG_MACVLAN \
    -e CONFIG_MACVTAP \
    -d CONFIG_DRM
  make O=./build-llvm LLVM=1 -j16 Image
  scripts/clang-tools/gen_compile_commands.py -d build-llvm

#git clone https://github.com/tianocore/edk2.git edk2
[working-directory: 'edk2']
edk2-setup:
  git switch --detach 2839fed5
  git submodule update --init --recursive

[working-directory: 'edk2']
edk2:
  #!/bin/bash
  source edksetup.sh; \
    CC=gcc-14 make -j -C BaseTools; \
    export GCC5_AARCH64_PREFIX=aarch64-linux-gnu-; \
    build -b RELEASE -a AARCH64 -t GCC5 -p ArmVirtPkg/ArmVirtQemuKernel.dsc; \
    build -b RELEASE -a AARCH64 -t GCC5 -p ArmVirtPkg/ArmVirtQemu.dsc

#git clone https://git.codelinaro.org/linaro/dcap/kvmtool -b cca/log

#git clone https://git.codelinaro.org/linaro/dcap/buildroot-external-cca.git
#git clone https://gitlab.com/buildroot.org/buildroot.git
[working-directory: 'buildroot']
buildroot-setup:
  echo "KVMTOOL_CCA_OVERRIDE_SRCDIR = ../kvmtool" > local.mk
  echo "BR2_GNU_MIRROR = https://ftp.jaist.ac.jp/pub/GNU" >> local.mk
  echo "HOSTCC = gcc-14" >> local.mk
  make BR2_EXTERNAL=../buildroot-external-cca/ cca_defconfig

[working-directory: 'buildroot']
buildroot:
  make -j16
  mkdir -p ../images/
  cp output/images/rootfs.ext4 ../images/
  cp output/images/rootfs.cpio ../images/

[working-directory: 'buildroot']
buildroot-clean-target:
  rm -rf output/target
  find output/build -name ".stamp_target_installed" -exec rm {} \;

#git clone https://git.codelinaro.org/linaro/dcap/rmm -b cca/v4
[working-directory: 'rmm']
rmm-setup $CROSS_COMPILE='aarch64-linux-gnu-':
  git submodule update --init --recursive
  cmake -B build-qemu -DCMAKE_BUILD_TYPE=Debug -DRMM_CONFIG=qemu_virt_defcfg -DCMAKE_EXPORT_COMPILE_COMMANDS=on

[working-directory: 'rmm']
rmm:
  cmake --build build-qemu

#git clone https://git.codelinaro.org/linaro/dcap/tf-a/trusted-firmware-a -b cca/v4
[working-directory: 'trusted-firmware-a']
tfa:
  make -j CROSS_COMPILE=aarch64-linux-gnu- PLAT=qemu ENABLE_RME=1 DEBUG=1 LOG_LEVEL=40 \
    QEMU_USE_GIC_DRIVER=QEMU_GICV3 RMM=../rmm/build-qemu/Debug/rmm.img \
    BL33=../edk2/Build/ArmVirtQemuKernel-AARCH64/RELEASE_GCC5/FV/QEMU_EFI.fd all fip memmap
  dd if=build/qemu/debug/bl1.bin of=flash.bin
  dd if=build/qemu/debug/fip.bin of=flash.bin seek=64 bs=4096

gtest:
  aarch64-linux-gnu-gcc gtest.c -static -o gtest

run-tmux:
  tmux new-session -d socat -,rawer TCP-LISTEN:54320,fork
  tmux select-pane -T Firmware
  tmux split-window -v socat -,rawer TCP-LISTEN:54321,fork
  tmux select-pane -T Secure
  tmux break-pane -d
  tmux split-pane -t 0 -h socat -,rawer TCP-LISTEN:54322,fork
  tmux select-pane -T 'Host 0'
  tmux split-pane -t 1 -h socat -,rawer TCP-LISTEN:54323,fork
  tmux select-pane -T 'Host 1'
  tmux split-pane -t 0 -v socat -,rawer TCP-LISTEN:54324,fork
  tmux select-pane -T 'Host 2'
  #tmux pipe-pane 'cat > host-2.txt'
  tmux split-pane -t 2 -v socat -,rawer TCP-LISTEN:54325,fork
  tmux select-pane -T 'Realm 0'
  tmux split-pane -t 4 -v socat -,rawer TCP-LISTEN:54326,fork
  tmux select-pane -T 'Realm 1'
  tmux set allow-set-title off
  tmux set pane-border-format "#{pane_title}"
  tmux set pane-border-status top
  tmux set mouse on
  tmux bind -n C-f copy-mode \\\; command-prompt -p "(search up)" "send -X search-backward \"%%%\""
  tmux bind -n C-e kill-session
  tmux attach

# hvc0:host1
# hvc1:host2
# hvc2:realm1
# hvc3=realm2
run-qemu:
  qemu-system-aarch64 \
    -M virt,virtualization=on,secure=on,gic-version=3 \
    -M acpi=off -cpu max,x-rme=on,pauth-impdef=on \
    -m 8G -smp 8 \
    -nographic \
    -bios trusted-firmware-a/flash.bin \
    -kernel linux/build/arch/arm64/boot/Image \
    -drive format=raw,if=none,file=./images/rootfs.ext4,id=hd0 \
    -device virtio-blk-pci,drive=hd0 \
    -nodefaults \
    -serial tcp:localhost:54320 \
    -serial tcp:localhost:54321 \
    -chardev socket,mux=on,id=hvc0,port=54322,host=localhost \
    -device virtio-serial-device \
    -device virtconsole,chardev=hvc0 \
    -chardev socket,mux=on,id=hvc1,port=54323,host=localhost \
    -device virtio-serial-device \
    -device virtconsole,chardev=hvc1 \
    -chardev socket,mux=on,id=hvc2,port=54324,host=localhost \
    -device virtio-serial-device \
    -device virtconsole,chardev=hvc2 \
    -chardev socket,mux=on,id=hvc3,port=54325,host=localhost \
    -device virtio-serial-device \
    -device virtconsole,chardev=hvc3 \
    -chardev socket,mux=on,id=hvc4,port=54326,host=localhost \
    -device virtio-serial-device \
    -device virtconsole,chardev=hvc4 \
    -append "root=/dev/vda console=hvc0" \
    -device virtio-net-pci,netdev=net0 -netdev user,id=net0 \
    -device virtio-9p-device,fsdev=shr0,mount_tag=shr0 \
    -fsdev local,security_model=none,path=.,id=shr0

#ln -s /mnt/gen-run-vmm.cfg .
#ln -s /mnt/gen-run-vmm.sh .
# GUEST_TTY=/dev/hvc3 EXTRA_KPARAMS=arm_cca_guest.is_attacker=1 ./gen-run-vmm.sh --kvmtool --tap --extcon
# GUEST_TTY=/dev/hvc4 EXTRA_KPARAMS=arm_cca_guest.is_attacker=0 ./gen-run-vmm.sh --kvmtool --tap --extcon

#mount -t 9p -o trans=virtio,version=9p2000.L shr1 /mnt
