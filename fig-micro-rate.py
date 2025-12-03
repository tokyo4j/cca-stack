import parse
import matplotlib.pyplot as plt
import sys
import pandas as pd

def get_point(dirname):
    mergeable_pages_cvm = []
    for line in (
        open(f"{dirname}/output-realm-0.txt").readlines()
        + open(f"{dirname}/output-realm-1.txt").readlines()
    ):
        if r := parse.search(
            "[{ts:^f}] setting mergeable: ipa={ipa:x}, duplicate={dup:d}, attacker={is_attacker:d}",
            line,
        ):
            mergeable_pages_cvm.append(
                {
                    "ipa": r.named["ipa"],
                    "dup": r.named["dup"],
                    "is_attacker": r.named["is_attacker"],
                }
            )
    mergeable_pages_cvm = pd.DataFrame(mergeable_pages_cvm)

    mergeable_pages_rmm = []
    deduped_pages_rmm = []
    for line in open(f"{dirname}/output-firmware.txt").readlines():
        if r := parse.search(
            "setting mergeable pa={pa:x}, ipa={ipa:x} is_attacker={is_attacker:d}",
            line,
        ):
            mergeable_pages_rmm.append(
                {
                    "ipa": r.named["ipa"],
                    "pa": r.named["pa"],
                    "is_attacker": r.named["is_attacker"],
                }
            )
        if r := parse.search(
            "merging p1->pa={p1_pa:x}, p2->pa={p2_pa:x}, ret->pa={ret_pa:x}",
            line,
        ):
            deduped_pages_rmm.append(
                {
                    "p1_pa": r.named["p1_pa"],
                    "p2_pa": r.named["p2_pa"],
                    "ret_pa": r.named["ret_pa"],
                }
            )
    mergeable_pages_rmm = pd.DataFrame(mergeable_pages_rmm)
    deduped_pages_rmm = pd.DataFrame(deduped_pages_rmm)

    mergeable_pages_cvm = pd.merge(
        mergeable_pages_cvm, mergeable_pages_rmm, on=["ipa", "is_attacker"], how="left"
    )
    deduped_pages_rmm = pd.merge(
        deduped_pages_rmm,
        mergeable_pages_cvm,
        left_on="ret_pa",
        right_on="pa",
        how="left",
    )

    return (
        len(mergeable_pages_cvm[mergeable_pages_cvm["dup"] == 1]) / len(mergeable_pages_cvm),
        len(deduped_pages_rmm[deduped_pages_rmm["dup"] == 1]) / len(deduped_pages_rmm),
    )


without_rand = (
    get_point("data/2025-12-03_02-41-35/"),
    get_point("data/2025-12-03_02-50-18/"),
    get_point("data/2025-12-03_02-58-10/"),
)

with_rand = (
    get_point("data/2025-12-03_03-12-49/"),
    get_point("data/2025-12-03_03-20-25/"),
    get_point("data/2025-12-03_03-05-33/"),
)

plt.figure(figsize=(10, 10))
plt.xlabel("Duplicates / pages")
plt.ylabel("Returned duplicates / retuned pages")
plt.xlim(0, 1.0)
plt.ylim(0, 1.1)

plt.plot(
    [p[0] for p in without_rand],
    [p[1] for p in without_rand],
    label="w/o spatial randomization",
    linestyle="-",
    marker="o",
)

plt.plot(
    [p[0] for p in with_rand],
    [p[1] for p in with_rand],
    label="w/ spatial randomization",
    linestyle="-",
    marker="o",
)
plt.legend(loc="upper left")

plt.savefig("fig-micro-rate.pdf")
