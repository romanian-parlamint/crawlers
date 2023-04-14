# ParlaMint-RO crawlers #

This repository contains the code required for crawling the data that is used for building the `ParlaMint-RO` corpus.

Each script in the root of this repository is used for crawling specific data:

- [`crawl-lower-house-sessions.py`](./crawl-lower-house-sessions.py) - as the name implies, this script is used to crawl the transcripts of the sessions and save them in `JSON` format.
- [`crawl-mp-data.py`](./crawl-mp-data.py) - this script is used to crawl profile info data of MPs and save them in `CSV` format.
