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

        if sec > 2000:
            continue

        if "UsedMemory" in line:
            d_mem[0].append(sec)
            d_mem[1].append(val / 1024)

    plt.plot(
        d_mem[0],
        d_mem[1],
        linestyle="-",
        label=label,
        color=color,
    )

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))
plot("data/2025-11-25_04-23-50", "w/ dedup", "r")
plot("data/2025-11-25_05-06-11", "w/o dedup", "g")
plt.legend()
plt.ylabel("Memory consumption (MB)", fontsize=17)
plt.xlabel("Time (s)", fontsize=17)
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.savefig("fig-micro-rmmdedup.pdf")

"""
diff --git a/gtest.c b/gtest.c
index d636d03..88eb14d 100644
--- a/gtest.c
+++ b/gtest.c
@@ -22,9 +22,9 @@ int main(int argc, char *argv[]) {
 		puts("KsmStart");
 		sleep(30);
 	} else {
-		puts("MadviseStart");
-		madvise(ptr, 4096 * NR_PAGES, 26);
-		puts("MadviseEnd");
+		// puts("MadviseStart");
+		// madvise(ptr, 4096 * NR_PAGES, 26);
+		// puts("MadviseEnd");
 		sleep(30);
 	}

"""