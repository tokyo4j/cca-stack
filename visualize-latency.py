import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FuncFormatter
import sys
import parse


fm = matplotlib.font_manager
fm._get_fontconfig_fonts.cache_clear()

if len(sys.argv) != 2:
    print("1 args must be passed")
    sys.exit(1)

in_filename = f"{sys.argv[1]}/output-host-0.txt"
out_filename = f"{sys.argv[1]}/mem-latency.png"

victim_signals = [[], []] # ts, ipa
attacker_signals = [[], []] # ts, ipa
reclaim_signals = [[], []] # ts, ipa

for line in open(in_filename).readlines():
    if r_victim := parse.search("[{ts:^f}] From victim: ipa={ipa:x}", line):
        victim_signals[0].append(r_victim.named["ts"])
        victim_signals[1].append(r_victim.named["ipa"])
    elif r_attacker := parse.search("[{ts:^f}] From attacker: ipa={ipa:x}", line):
        attacker_signals[0].append(r_attacker.named["ts"])
        attacker_signals[1].append(r_attacker.named["ipa"])
    elif r_reclaim := parse.search("[{ts:^f}] [{:d}] Reclaimed pa={pa:x} ipa={ipa:x}", line):
        reclaim_signals[0].append(r_reclaim.named["ts"])
        reclaim_signals[1].append(r_reclaim.named["ipa"])

print(len(reclaim_signals[0]))

victim_signals[1] = [f"0x{x:x}" for x in victim_signals[1]]
attacker_signals[1] = [f"0x{x:x}" for x in attacker_signals[1]]
reclaim_signals[1] = [f"0x{x:x}" for x in reclaim_signals[1]]

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))

plt.plot(
    victim_signals[0],
    victim_signals[1],
    color="b",
    label="Victim realm sets mergeable page",
    marker=".",
    linestyle="",
    markersize=8,
)

plt.plot(
    attacker_signals[0],
    attacker_signals[1],
    color="r",
    label="Attacker realm sets mergeable page",
    marker=".",
    linestyle="",
    markersize=8,
)


plt.plot(
    reclaim_signals[0],
    reclaim_signals[1],
    color="g",
    label="VMM reclaims page from RMM",
    marker=".",
    linestyle="",
    markersize=8,
)

plt.legend()
plt.ylabel("gPA", fontsize=17)
plt.xlabel("時間 (s)", fontsize=17)

plt.grid(True)
plt.gca().xaxis.set_tick_params(labelsize=16)
plt.gca().yaxis.set_tick_params(labelsize=8)
plt.gca().yaxis.set_ticklabels([])
plt.savefig(out_filename)
