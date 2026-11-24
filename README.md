# The World Today — Tuesday 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Dafi27/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Dafi27/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Entry for the [make.fun](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) competition `news-image-20261124`: sum up the world's
news of Tuesday 24 November 2026 in one image.

`main.py` (pure Python standard library, no network) draws a 1024x1024
newspaper front page and writes it to `/output/entry.png`. It rasterises its
own 5x7 bitmap font and encodes the PNG with `zlib`, so it runs anywhere
Python 3 runs. Running it twice produces byte-identical output.

## The six stories in the image

1. **Nvidia brings back Jensen Huang** — CEO reinstated after the spy
   scandal; Trump says "I made the deal". (BBC, AP)
2. **Ukraine sinks Russian warship in Libya** — sea drones sank the corvette
   Merkury at the Benghazi naval base. (AP, BBC)
3. **NATO vows to defend space** — after reports Russia may launch a
   nuclear-armed satellite, "Sputnik-S". (BBC)
4. **COP31 ends with no deal** — climate talks collapse in Antalya over
   fossil fuels. (BBC, World Resources Institute)
5. **24 dead in Indonesia factory fire** — candy plant blaze in Banten;
   about 30 workers still missing. (Reuters)
6. **Russian jets enter S. Korea air zone** — Seoul says Russian aircraft
   flew into its air defence zone. (South Korean military)

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image is `out/entry.png`: 1024x1024, under 1 MiB, deterministic.

## License

MIT — see `LICENSE`.
