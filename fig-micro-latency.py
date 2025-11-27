import matplotlib.pyplot as plt
import matplotlib
import sys
import parse

"""
- Run no app
- Set is_victim=0 and is_attacker=0
- RMM@ff6ee28737aa232bb766b871370e578b02f40957
"""

fm = matplotlib.font_manager
fm._get_fontconfig_fonts.cache_clear()

d_victim = []
d_attacker = []
d_reclaim = []

for line in open("data/2025-11-27_19-43-06/output-host-0.txt").readlines():
    if r_victim := parse.search("[{ts:^f}] From victim: ipa={ipa:x}", line):
        d_victim.append(
            {
                "ts": r_victim.named["ts"],
                "ipa": f"0x{r_victim.named['ipa']:x}",
            }
        )
    elif r_attacker := parse.search("[{ts:^f}] From attacker: ipa={ipa:x}", line):
        d_attacker.append(
            {
                "ts": r_attacker.named["ts"],
                "ipa": f"0x{r_attacker.named['ipa']:x}",
            }
        )
    elif r_reclaim := parse.search(
        "[{ts:^f}] [{:d}] Reclaimed pa={pa:x} ipa={ipa:x}", line
    ):
        d_reclaim.append(
            {
                "ts": r_reclaim.named["ts"],
                "ipa": f"0x{r_reclaim.named['ipa']:x}",
                "pa": f"0x{r_reclaim.named['pa']:x}",
            }
        )

print(len(d_reclaim))

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))

plt.plot(
    [d["ts"] for d in d_victim],
    [d["ipa"] for d in d_victim],
    color="b",
    label="Victim realm sets mergeable page",
    marker=".",
    linestyle="",
    markersize=4,
)

plt.plot(
    [d["ts"] for d in d_attacker],
    [d["ipa"] for d in d_attacker],
    color="r",
    label="Attacker realm sets mergeable page",
    marker=".",
    linestyle="",
    markersize=4,
)

plt.plot(
    [d["ts"] for d in d_reclaim],
    [d["ipa"] for d in d_reclaim],
    color="g",
    label="VMM reclaims page from RMM",
    marker=".",
    linestyle="",
    markersize=4,
)


def draw_line(plt, p1, p2, color):
    plt.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        color=color,
        alpha=0.4,
        marker="",
        linewidth=0.5,
    )


for line in open("data/2025-11-27_19-43-06/output-firmware.txt").readlines():
    if r := parse.search(
        "scan->ipa={scan_ipa:x}, dup->ipa={dup_ipa:x}, rand->pa={rand_pa:x}, rand->ipa={rand_ipa:x}",
        line,
    ):
        scan_ipa = f"0x{r.named['scan_ipa']:x}"
        dup_ipa = f"0x{r.named['dup_ipa']:x}"
        rand_pa = f"0x{r.named['rand_pa']:x}"
        rand_ipa = f"0x{r.named['rand_ipa']:x}"

        scan = [d for d in d_attacker if d["ipa"] == scan_ipa] + [
            d for d in d_victim if d["ipa"] == scan_ipa
        ]
        dup = [d for d in d_attacker if d["ipa"] == dup_ipa] + [
            d for d in d_victim if d["ipa"] == dup_ipa
        ]
        rand = [d for d in d_attacker if d["ipa"] == rand_ipa] + [
            d for d in d_victim if d["ipa"] == rand_ipa
        ]
        assert len(scan) == 1
        assert len(dup) == 1
        assert len(rand) == 1
        scan = scan[0]
        dup = dup[0]
        rand = rand[0]
        ret = [d for d in d_reclaim if d["pa"] == rand_pa][0]

        p1 = scan["ts"], scan["ipa"]
        p2 = dup["ts"], dup["ipa"]
        p3 = rand["ts"], rand["ipa"]
        p4 = ret["ts"], ret["ipa"]
        draw_line(plt, p1, p4, "r")
        draw_line(plt, p2, p4, "b")
        # draw_line(plt, p3, p4, "g")

plt.legend()
plt.ylabel("Guest physical address", fontsize=17)
plt.xlabel("Time (s)", fontsize=17)

plt.grid(True)
plt.gca().xaxis.set_tick_params(labelsize=16)
plt.gca().yaxis.set_tick_params(labelsize=8)
plt.gca().yaxis.set_ticklabels([])
plt.savefig("fig-micro-latency.pdf")
