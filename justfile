linux-setup:
  git clone https://gitlab.arm.com/linux-arm/linux-cca -b cca-host/v7
[working-directory: 'linux']
linux:
  make CROSS_COMPILE=aarch64-linux-gnu- ARCH=arm64 defconfig
  scripts/config -e VIRT_DRIVERS -e ARM_CCA_GUEST -e CONFIG_HZ_100 \
   -d CONFIG_HZ_250 -e CONFIG_MACVLAN -e CONFIG_MACVTAP
  make CROSS_COMPILE=aarch64-linux-gnu- ARCH=arm64 -j16 Image

edk2-guest-setup:
  git clone https://git.codelinaro.org/linaro/dcap/edk2 -b cca/latest edk2-guest
  git submodule update --init --recursive
[working-directory: 'edk2-guest']
edk2-guest:
  source edksetup.sh
  make -j -C BaseTools
  export GCC5_AARCH64_PREFIX=aarch64-linux-gnu-
  build -b RELEASE -a AARCH64 -t GCC5 -p ArmVirtPkg/ArmVirtQemu.dsc

edk2-host-setup:
  git clone https://github.com/tianocore/edk2.git edk2-host
  git switch --detach 2839fed5
  git submodule update --init --recursive
[working-directory: 'edk2-host']
edk2-host:
  source edksetup.sh
  make -j -C BaseTools
  export GCC5_AARCH64_PREFIX=aarch64-linux-gnu-
  build -b RELEASE -a AARCH64 -t GCC5 -p ArmVirtPkg/ArmVirtQemuKernel.dsc

kvmtool-setup:
  git clone https://git.codelinaro.org/linaro/dcap/kvmtool -b cca/log

buildroot-setup:
  git clone https://git.codelinaro.org/linaro/dcap/buildroot-external-cca.git
  git clone https://gitlab.com/buildroot.org/buildroot.git
  cd buildroot; echo "KVMTOOL_CCA_OVERRIDE_SRCDIR = ../kvmtool" > local.mk
  cd buildroot; make BR2_EXTERNAL=../buildroot-external-cca/ cca_defconfig
[working-directory: 'buildroot']
buildroot:
  make -j16
  cp output/images/rootfs.ext4 ../images/
  cp output/images/rootfs.cpio ../images/

rmm-setup:
  git clone https://git.codelinaro.org/linaro/dcap/rmm -b cca/v4
  git submodule update --init --recursive
  export CROSS_COMPILE=aarch64-linux-gnu-
  cmake -B build-qemu -DCMAKE_BUILD_TYPE=Debug -DRMM_CONFIG=qemu_virt_defcfg
[working-directory: 'rmm']
rmm:
  cmake --build build-qemu

tfa-setup:
  git clone https://git.codelinaro.org/linaro/dcap/tf-a/trusted-firmware-a -b cca/v4
[working-directory: 'trusted-firmware-a']
tfa:
  make -j CROSS_COMPILE=aarch64-linux-gnu- PLAT=qemu ENABLE_RME=1 DEBUG=1 LOG_LEVEL=40 \
    QEMU_USE_GIC_DRIVER=QEMU_GICV3 RMM=../rmm/build-qemu/Debug/rmm.img \
    BL33=../edk2-host/Build/ArmVirtQemuKernel-AARCH64/RELEASE_GCC5/FV/QEMU_EFI.fd all fip
  dd if=build/qemu/debug/bl1.bin of=flash.bin
  dd if=build/qemu/debug/fip.bin of=flash.bin seek=64 bs=4096

run-tmux:
  tmux new-session -d socat -,rawer TCP-LISTEN:54320
  tmux select-pane -T Firmware
  tmux split-window -v socat -,rawer TCP-LISTEN:54321
  tmux select-pane -T Secure
  tmux split-pane -t 0 -h socat -,rawer TCP-LISTEN:54322
  tmux select-pane -T Host
  tmux split-pane -t 2 -h socat -,rawer TCP-LISTEN:54323
  tmux select-pane -T Realm
  tmux set allow-set-title off
  tmux set pane-border-format "#{pane_title}"
  tmux set pane-border-status top
  tmux set mouse on
  tmux attach

run-qemu:
  qemu-system-aarch64 \
    -M virt,virtualization=on,secure=on,gic-version=3 \
    -M acpi=off -cpu max,x-rme=on,pauth-impdef=on \
    -m 8G -smp 8 \
    -nographic \
    -bios trusted-firmware-a/flash.bin \
    -kernel linux-cca/arch/arm64/boot/Image \
    -drive format=raw,if=none,file=buildroot/output/images/rootfs.ext4,id=hd0 \
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
    -append "root=/dev/vda console=hvc0" \
    -device virtio-net-pci,netdev=net0 -netdev user,id=net0 \
    -device virtio-9p-device,fsdev=shr0,mount_tag=shr0 \
    -fsdev local,security_model=none,path=.,id=shr0

#ln -s /mnt/gen-run-vmm.cfg .
#gen-run-vmm.sh --kvmtool --tap --extcon
