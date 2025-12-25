import matplotlib.pyplot as plt
import matplotlib
import sys
import parse
import os

fm = matplotlib.font_manager
fm._get_fontconfig_fonts.cache_clear()

dirs = sorted(
    [
        os.path.join("data", name)
        for name in os.listdir("data")
        if "2025-12-09_17-08-09" <= name <= "2025-12-11_04-54-20"
    ]
)

inferences = []
diffs = []

for dir in dirs:
    d_victim = []
    d_attacker = []
    d_reclaim = []

    for line in open(f"{dir}/output-host-0.txt").readlines():
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
                    "idx": len(d_attacker),
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

    r = None
    for line in open(f"{dir}/output-realm-0.txt").readlines():
        if r_victim := parse.search("[{ts:^f}] Victim: r={r:d}", line):
            r = r_victim.named["r"]

    guess = None
    min_diff = float("inf")
    for d in d_attacker:
        diff = abs(d["ts"] - (d_reclaim[0]["ts"] - 28))
        if diff < min_diff:
            min_diff = diff
            guess = d

    ans = {}
    for d in d_attacker:
        if d["idx"] == r:
            ans = d

    inferences.append({
        "r": r,
        "reclaim": d_reclaim[0],
        "guess": guess,
        "ans": ans,
    })
    diffs.append(d_reclaim[0]["ts"] - ans["ts"])

nr_correct = sum(1 for inf in inferences if inf["guess"] == inf["ans"])
print(f"Correct guesses: {nr_correct} / {len(inferences)}")
print(f"Average difference: {sum(diffs) / len(diffs)}")

plt.scatter(range(len(diffs)), diffs)
plt.savefig("diff.png")
