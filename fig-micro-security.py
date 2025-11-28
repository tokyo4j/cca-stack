import matplotlib.pyplot as plt
import matplotlib
import sys
import parse

fm = matplotlib.font_manager
fm._get_fontconfig_fonts.cache_clear()

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.figure(figsize=(10, 6))

def draw_line(plt, p1, p2):
    plt.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        color="m",
        alpha=0.4,
        marker="",
        zorder=5,
    )

def plot(data_dir, out_filename):
    plt.figure(figsize=(10, 6))
    plt.xlim(100, 210)
    d_victim = []
    d_attacker = []
    d_reclaim = []

    for line in open(f"{data_dir}/output-host-0.txt").readlines():
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

    plt.plot(
        [d["ts"] for d in d_victim],
        [d["ipa"] for d in d_victim],
        color="b",
        label="Victim realm sets mergeable page",
        marker=".",
        linestyle="",
        markersize=6,
        zorder=10,
    )

    plt.plot(
        [d["ts"] for d in d_attacker],
        [d["ipa"] for d in d_attacker],
        color="r",
        label="Attacker realm sets mergeable page",
        marker=".",
        linestyle="",
        markersize=6,
        zorder=10,
    )

    plt.plot(
        [d["ts"] for d in d_reclaim],
        [d["ipa"] for d in d_reclaim],
        color="g",
        label="VMM reclaims page from RMM",
        marker=".",
        linestyle="",
        markersize=6,
        zorder=10,
    )

    for line in open(f"{data_dir}/output-firmware.txt").readlines():
        if r := parse.search(
            "p1->ipa={p1_ipa:x}, p2->ipa={p2_ipa:x}, ret->pa={ret_pa:x}, ret->ipa={ret_ipa:x}",
            line,
        ):
            p1_ipa = f"0x{r.named['p1_ipa']:x}"
            p2_ipa = f"0x{r.named['p2_ipa']:x}"
            ret_pa = f"0x{r.named['ret_pa']:x}"
            ret_ipa = f"0x{r.named['ret_ipa']:x}"

            p1_marked = [d for d in d_attacker if d["ipa"] == p1_ipa] + [
                d for d in d_victim if d["ipa"] == p1_ipa
            ]
            p2_marked = [d for d in d_attacker if d["ipa"] == p2_ipa] + [
                d for d in d_victim if d["ipa"] == p2_ipa
            ]
            ret_marked = [d for d in d_attacker if d["ipa"] == ret_ipa] + [
                d for d in d_victim if d["ipa"] == ret_ipa
            ]
            assert len(p1_marked) == 1
            assert len(p2_marked) == 1
            assert len(ret_marked) == 1
            p1_marked = p1_marked[0]
            p2_marked = p2_marked[0]
            ret_marked = ret_marked[0]
            ret_reclaimed = [d for d in d_reclaim if d["pa"] == ret_pa][0]

            p1_marked_p = p1_marked["ts"], p1_marked["ipa"]
            p2_marked_p = p2_marked["ts"], p2_marked["ipa"]
            ret_marked_p = ret_marked["ts"], ret_marked["ipa"]
            ret_reclaimed_p = ret_reclaimed["ts"], ret_reclaimed["ipa"]
            draw_line(plt, p1_marked_p, ret_reclaimed_p)
            draw_line(plt, p2_marked_p, ret_reclaimed_p)

    plt.legend(loc="upper left")
    plt.ylabel("Guest physical address", fontsize=17)
    plt.xlabel("Time (s)", fontsize=17)

    plt.grid(True)
    plt.gca().xaxis.set_tick_params(labelsize=16)
    plt.gca().yaxis.set_tick_params(labelsize=8)
    plt.gca().yaxis.set_ticklabels([])
    plt.savefig(out_filename)

plot("data/2025-11-28_20-43-05-no-rand", "fig-micro-security-no-rand.pdf")
plot("data/2025-11-28_20-27-48-no-spatial-rand", "fig-micro-security-no-spatial-rand.pdf")
plot("data/2025-11-28_20-37-42-no-temporal-rand", "fig-micro-security-no-temporal-rand.pdf")
plot("data/2025-11-28_20-47-33-rand", "fig-micro-security-rand.pdf")
