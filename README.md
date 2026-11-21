# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/hiduplahzomb/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/hiduplahzomb/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

THE WORLD TODAY — a newspaper front page drawn entirely in code (Python
standard library only: a hand-written rasterizer, a 5×7 bitmap font, and a
hand-written PNG encoder) summing up Saturday 21 November 2026's world news
in one 1024×1024 image.

The day's stories: Russia's biggest strike on Ukraine (400+ drones,
110 missiles; two land in Poland); the AI stock sell-off (US stocks −3.7%,
S&P 500 into correction); the ICJ finding Myanmar responsible for genocide
against the Rohingya; the Trump–Putin–Xi summit in Shenzhen and its peace
declaration; and a pancreatic cancer pill that made tumours undetectable in
1 in 12 trial patients.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024×1024, deterministic — the same bytes every run).
In the grader it writes `/output/entry.png`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=2wgaefze&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
