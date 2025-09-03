import matplotlib.pyplot as plt

def plot(path, label):
    d_mem = [[], []]
    #d_app_start = []
    #d_alloc_start = []
    #d_alloc_end = []
    #d_ksm_start = []
    #d_madv_start = []
    #d_madv_end = []
    #d_loop_start = []

    in_filename = f"{path}/output-host-2.txt"

    lines = open(in_filename).readlines()

    for line in lines:
        cols = line.split()
        if len(cols) != 3 or not cols[0].isnumeric() or not cols[2].isnumeric():
            continue
        sec = int(cols[0]) / 1000
        val = int(cols[2])
        if sec > 8000:
            continue

        if "UsedMemory" in line:
            d_mem[0].append(sec)
            d_mem[1].append(val / 1024)
        #elif "AppStart" in line:
        #    d_app_start.append(sec)
        #elif "AllocStart" in line:
        #    d_alloc_start.append(sec)
        #elif "AllocEnd" in line:
        #    d_alloc_end.append(sec)
        #elif "KsmStart" in line:
        #    d_ksm_start.append(sec)
        #elif "MadviseStart" in line:
        #    d_madv_start.append(sec)
        #elif "MadviseEnd" in line:
        #    d_madv_end.append(sec)
        #elif "LoopStart" in line:
        #    d_loop_start.append(sec)

    plt.plot(
        d_mem[0],
        d_mem[1],
        linestyle="-",
        label=label,
    )
    #for d in d_app_start:
    #    plt.axvline(d, color="b", label="アプリケーション起動")
    #for d in d_alloc_start:
    #    plt.axvline(d, color="orange", label="メモリ確保開始")
    #for d in d_alloc_end:
    #    plt.axvline(d, color="lime", label="メモリ確保終了")
    #for d in d_ksm_start:
    #    plt.axvline(d, color="slateblue", label="KSM開始")
    #for d in d_madv_start:
    #    plt.axvline(d, color="slateblue", label="madvise()開始")
    #for d in d_madv_end:
    #    plt.axvline(d, color="lightsteelblue", label="madvise()終了")
    #for d in d_loop_start:
    #    plt.axvline(d, color="brown", label="ループ開始")


plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))
plt.ylabel("メモリ使用量 (MB)", fontsize=17)
plt.xlabel("時間 (s)", fontsize=17)
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.title("2つのCVMにおいて、それぞれ1GBのメモリを確保し、RMMでDeduplicate")

plot("data/2025-09-03_04-08-24-rmm-dedup", "Dedup有効")
plot("data/2025-09-03_17-47-45-c4df9ac-rmm-no-dedup", "Dedup無効")

plt.legend()
plt.savefig("rmm.png")
