import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sys

mem_samples = [[], []]
app_samples = []
ksm_samples = []

if len(sys.argv) != 2:
    print("1 args must be passed")
    sys.exit(1)


in_filename = f"{sys.argv[1]}/output-host-2.txt"
out_filename = f"{sys.argv[1]}/mem-usage.png"

lines = open(in_filename).readlines()
# lines = lines[10:3000]

for line in lines:
    cols = line.split()
    if "FreeMemory" in line:
        mem_samples[0].append(int(cols[0]) / 1000)
        mem_samples[1].append(int(cols[2]) / 1024)
    elif "Starting ksm" in line:
        ksm_samples.append(int(cols[0]) / 1000)
    elif "Started app" in line and cols[0].isdigit():
        app_samples.append(int(cols[0]) / 1000)

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))
plt.plot(
    mem_samples[0],
    mem_samples[1],
    linestyle="-",
    color="r",
)
for app_sample in app_samples:
    plt.axvline(app_sample, color="b", label="アプリケーション起動")
for ksm_sample in ksm_samples:
    plt.axvline(ksm_sample, color="g", label="Loop started")

plt.legend()
plt.ylabel("メモリ使用量 (MB)", fontsize=17)
plt.xlabel("時間 (s)", fontsize=17)
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.savefig(out_filename)
