import matplotlib.pyplot as plt

def plot(src, label, color):
    in_filename = f"{src}/output-host-2.txt"
    d_mem = [[], []]
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

    plt.plot(
        d_mem[0],
        d_mem[1],
        linestyle="-",
        label=label,
    )

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))
plot("data/2025-09-11_01-23-16-dedup-model", "w/ dedup", "r")
plot("data/2025-09-11_06-42-34-no-mlock-dedup", "w/o dedup", "g")
plt.legend()
plt.ylabel("Memory consumption (MB)", fontsize=17)
plt.xlabel("Time (s)", fontsize=17)
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.savefig("fig-llama-rmmdedup.pdf")
