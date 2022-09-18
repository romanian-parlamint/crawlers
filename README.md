# ParlaMint-RO processing pipeline #

This repository contains the code required for running the processing pipeline that builds the `ParlaMint-RO` corpus.

Each script in the root of this repository represents a step in the processing pipeline. Theese scripts can be classified as follows:

## Crawler scripts ##

- [`crawl-lower-house-sessions.py`](./crawl-lower-house-sessions.py) - as the name implies, this script is used to crawl the transcripts of the sessions and save them in `JSON` format.
- [`crawl-mp-data.py`](./crawl-mp-data.py) - this script is used to crawl profile info data of MPs and save them in `CSV` format.

## Preprocessing scripts ##

- [`build-speakers-list.py`](./build-speakers-list.py) - iterates through session transcripts in `JSON` format and builds a list of unique speaker names, which is then saved to a `CSV` file.
- [`classify-speakers.py`](./classify-speakers.py) - iterates through session transcripts in `JSON` format and classifies speakers into MPs and invited speakers; the lists are saved in `CSV` format.
