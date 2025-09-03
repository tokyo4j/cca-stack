import matplotlib.pyplot as plt
import sys

d_mem = [[], []]
d_app_start = []
d_alloc_start = []
d_alloc_end = []
d_ksm_start = []
d_madv_start = []
d_madv_end = []
d_loop_start = []

if len(sys.argv) != 2:
    print("1 args must be passed")
    sys.exit(1)


in_filename = f"{sys.argv[1]}/output-host-2.txt"
out_filename = f"{sys.argv[1]}/mem-usage.png"

lines = open(in_filename).readlines()
# lines = lines[10:3000]

for line in lines:
    cols = line.split()
    if len(cols) != 3 or not cols[0].isnumeric() or not cols[2].isnumeric():
        continue
    sec = int(cols[0]) / 1000
    val = int(cols[2])

    if "UsedMemory" in line:
        d_mem[0].append(sec)
        d_mem[1].append(val / 1024)
    elif "AppStart" in line:
        d_app_start.append(sec)
    elif "AllocStart" in line:
        d_alloc_start.append(sec)
    elif "AllocEnd" in line:
        d_alloc_end.append(sec)
    elif "KsmStart" in line:
        d_ksm_start.append(sec)
    elif "MadviseStart" in line:
        d_madv_start.append(sec)
    elif "MadviseEnd" in line:
        d_madv_end.append(sec)
    elif "LoopStart" in line:
        d_loop_start.append(sec)

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))
plt.plot(
    d_mem[0],
    d_mem[1],
    linestyle="-",
    color="r",
)
for d in d_app_start:
    plt.axvline(d, color="b", label="アプリケーション起動")
for d in d_alloc_start:
    plt.axvline(d, color="orange", label="メモリ確保開始")
for d in d_alloc_end:
    plt.axvline(d, color="lime", label="メモリ確保終了")
for d in d_ksm_start:
    plt.axvline(d, color="slateblue", label="KSM開始")
for d in d_madv_start:
    plt.axvline(d, color="slateblue", label="madvise()開始")
for d in d_madv_end:
    plt.axvline(d, color="lightsteelblue", label="madvise()終了")
for d in d_loop_start:
    plt.axvline(d, color="brown", label="ループ開始")

plt.legend()
plt.ylabel("メモリ使用量 (MB)", fontsize=17)
plt.xlabel("時間 (s)", fontsize=17)
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.savefig(out_filename)
