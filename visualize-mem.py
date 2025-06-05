import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import sys

samples = []

if len(sys.argv) != 3:
    print("2 args must be passed")
    sys.exit(1)

in_filename = sys.argv[1]
out_filename = sys.argv[2]

for line in open(in_filename).readlines():
    if "MemAvailable:" not in line:
        continue
    cols = line.split()
    samples.append(int(cols[1]) / 1024)

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))
plt.plot(
    samples,
    linestyle="-",
    color="r",
    label="w/o deduplication",
)

plt.ylabel("空きメモリ容量 (MB)", fontsize=17)
plt.xlabel("時間 (s)", fontsize=17)
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.savefig(out_filename)
