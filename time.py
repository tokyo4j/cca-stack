import matplotlib.pyplot as plt
import sys

def get_stat(i):
    in_filename = f"{sys.argv[i]}/output-firmware.txt"
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

    return cvm_data, vmm_data

cvm_data0, vmm_data0 = get_stat(1)
cvm_data1, vmm_data1 = get_stat(2)

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.scatter(
    cvm_data0[0],
    cvm_data0[1],
    color="r",
    label="w/o busy loop"
)
plt.scatter(
    cvm_data1[0],
    cvm_data1[1],
    color="b",
    label="w/ busy loop"
)
plt.title("Execution time of SetPagesMergeable calls")
plt.xlabel("# of pages", fontsize=17)
plt.ylabel("time [ms]", fontsize=17)
plt.legend()
plt.savefig(f"{sys.argv[2]}/compare-SetPagesMergeable.png")

plt.figure(figsize=(10, 6))
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.scatter(
    vmm_data0[0],
    vmm_data0[1],
    color="r",
    label="w/o busy loop"
)
plt.scatter(
    vmm_data1[0],
    vmm_data1[1],
    color="b",
    label="w/ busy loop"
)
plt.title("Execution time of ReclaimMergedPages calls")
plt.xlabel("# of pages", fontsize=17)
plt.ylabel("time [ms]", fontsize=17)
plt.legend()
plt.savefig(f"{sys.argv[2]}/compare-ReclaimMergedPages.png")
