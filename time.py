import matplotlib.pyplot as plt
import sys

in_filename = f"{sys.argv[1]}/output-firmware.txt"
cvm_filename = f"{sys.argv[1]}/SetPagesMergeable.png"
vmm_filename = f"{sys.argv[1]}/ReclaimMergedPages.png"
lines = open(in_filename).readlines()

cvm_data = [[], []]
vmm_data = [[], []]

for line in lines:
    cols = line.split()
    if len(cols) != 3:
        continue
    if "handle_rsi_set_pages_mergeable():ns,len=" == cols[0]:
        cvm_data[0].append(int(cols[2]))
        cvm_data[1].append(int(cols[1]) / 1000000)
    elif "smc_reclaim_mergeable_page():ns,i=" == cols[0]:
        vmm_data[0].append(int(cols[2]))
        vmm_data[1].append(int(cols[1]) / 1000000)

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.scatter(
    cvm_data[0],
    cvm_data[1],
    color="r",
)
plt.title("SetPagesMergeable")
plt.xlabel("# of pages", fontsize=17)
plt.ylabel("time [ms]", fontsize=17)
plt.savefig(cvm_filename)

plt.figure(figsize=(10, 6))
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.scatter(
    vmm_data[0],
    vmm_data[1],
    color="r",
)
plt.title("ReclaimMergedPages")
plt.xlabel("# of pages", fontsize=17)
plt.ylabel("time [ms]", fontsize=17)
plt.savefig(vmm_filename)
