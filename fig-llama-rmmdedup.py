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
        color=color,
    )

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))
plot("data/2025-11-25_09-50-33", "w/ dedup", "r")
plot("data/2025-11-25_11-06-56", "w/o dedup", "g")
plt.legend()
plt.ylabel("Memory consumption (MB)", fontsize=17)
plt.xlabel("Time (s)", fontsize=17)
plt.grid(True)
plt.gca().yaxis.set_tick_params(labelsize=16)
plt.savefig("fig-llama-rmmdedup.pdf")

"""
diff --git a/automate.py b/automate.py
index 2b161dd..bbf952a 100644
--- a/automate.py
+++ b/automate.py
@@ -90,8 +90,7 @@ def handle_host(host_id, port):
         base_cmd += "--no-rme "
 
     if host_id == 0:
-        cmd = "RECLAIM_MERGED_PAGES=1 "
-        cmd += "GUEST_TTY=/dev/hvc3 "
+        cmd = "GUEST_TTY=/dev/hvc3 "
         cmd += "EXTRA_KPARAMS='arm_cca_guest.is_victim=0' "
         cmd += base_cmd
         child.sendline(cmd)
@@ -124,10 +123,11 @@ def handle_realm(realm_id, port):
     child.expect("#", timeout=None)
     #child.sendline(f"cat /proc/kallsyms > /mnt/{data_dir}/realm-{realm_id}-kallsyms.txt")
     #child.expect("#", timeout=None)
-    cmd = "/mnt/gtest"
-    if no_rme:
-        cmd += " --no-rme"
-    child.sendline(cmd)
+    #cmd = "/mnt/gtest"
+    #if no_rme:
+    #    cmd += " --no-rme"
+    #child.sendline(cmd)
+    child.sendline("/mnt/llama.cpp/build/bin/llama-cli -m /mnt/llama.cpp/ggml-model-q4_0.gguf -i")
     for i, msg in enumerate(phase_msgs):
         child.expect(msg, timeout=None)
         set_state(realm_id, i)

"""