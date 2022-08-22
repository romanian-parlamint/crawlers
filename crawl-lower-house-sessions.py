#!/usr/bin/env python
"""Crawl sessions of Romanian Lower House."""
from argparse import ArgumentParser
from argparse import ArgumentTypeError
import datetime
import logging
from core.navigation import UrlBuilder
from core.crawling.utils import SessionUrlsCrawler
from core.crawling.summary import SessionSummaryCrawler
from core.crawling.session import SessionTranscriptCrawler
import json
from pathlib import Path


def get_parsed_sessions(transcripts_dir):
    """Create a set of dates for which exists a session transcript in the provided directory.

    Parameters
    ----------
    transcripts_dir: str, required
        The path of the directory containing parsed session transcripts.

    Returns
    -------
    session_dates: set of str
        The dates of the parsed sessions taken from file names.
    """
    session_dates = set()
    transcripts_dir = Path(transcripts_dir)
    for file_name in transcripts_dir.glob("*.json"):
        idx = file_name.stem.rfind('-')
        session_date = file_name.stem[:idx]
        session_dates.add(session_date)
    return session_dates


def iter_session_URLs(args):
    """Iterate over session URLs from the arguments.

    Parameters
    ----------
    args: argparse.Namespace, required
        The command-line arguments of the script.

    Returns
    -------
    url_generator: generator of (datetime, str) tuples
        The collection of session dates and their URLs.
    """
    if args.date:
        url_builder = UrlBuilder()
        yield args.date, url_builder.build_URL_for_session(args.date)
    else:
        crawled_dates = set()
        if not args.force:
            crawled_dates = get_parsed_sessions(args.output_dir)
        crawler = SessionUrlsCrawler()
        for year in args.years:
            try:
                for date, url in crawler.crawl(year):
                    date_str = date.strftime("%Y-%m-%d")
                    if date_str in crawled_dates:
                        message = "Date %s is already parsed; skipping."
                        logging.info(message, date_str)
                        continue
                    else:
                        yield date, url
            except Exception as e:
                message = "Could not crawl session URLs for year %s."
                logging.error(message, year, exc_info=e)


def save_session_transcript(output_dir, transcript, session_date, session_id):
    """Save session transcript into a JSON file.

    Parameters
    ----------
    output_dir: str, required
        The directory where to save the session transcript.
    transcript: dict, required
        The transcript to save.
    session_date: datetime.date, required
        The session date; it will be included in file name.
    session_id: str, required
        The id of the session; will be included in file name to differentiate sessions from the same day.
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        logging.info("Creating directory {}.".format(str(output_dir)))
        output_dir.mkdir(parents=True, exist_ok=True)

    file_name = output_dir / "{date}-{id}.json".format(
        date=session_date.strftime("%Y-%m-%d"), id=session_id)
    with open(str(file_name), 'w', encoding='utf8') as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)


def main(args):
    """Crawl session transcripts."""
    if args.date:
        logging.info("Crawling session transcript for date {}.".format(
            args.date))
    else:
        logging.info("Crawling sessions for the following years: {}.".format(
            ", ".join([str(year) for year in args.years])))
    for date, url in iter_session_URLs(args):
        logging.info("Crawling session summary for date {} from {}.".format(
            date.strftime("%Y-%m-%d"), url))
        try:
            summaries = SessionSummaryCrawler().crawl(url)
            for summary in summaries:
                transcript = SessionTranscriptCrawler(date).crawl(
                    summary['full_transcript_url'])
                summary.update(transcript)
                session_id = summary['session_id']
                save_session_transcript(args.output_dir, summary, date,
                                        session_id)
        except Exception as e:
            logging.error("Could not crawl session contents from URL %s.",
                          url,
                          exc_info=e)


def valid_year(year):
    """Return True if provided year is valid as an argument to the script.

    Parameters
    ----------
    year: str, required
        The year to validate.
    """
    year = int(year)
    max_year = datetime.date.year
    if year <= 2000 or year > max_year:
        raise ArgumentTypeError(
            "Year must be betweer 2000 and {} inclusive.".format(max_year))
    return year


def parse_arguments():
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description='Crawl sessions of Romanian Lower House')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--date',
        help="The ISO-format date for which to crawl session transcript.",
        type=datetime.date.fromisoformat)
    group.add_argument('--year',
                       help="List of years for which to crawl transcripts.",
                       dest='years',
                       type=int,
                       choices=range(2000,
                                     datetime.date.today().year + 1),
                       nargs='+')
    parser.add_argument('--force',
                        help="""
                       When provided together with the '--year' argument specifies
                       to ignore already crawled sessions and start the crawling anew.
                       """,
                        action='store_true')
    parser.add_argument('--output-dir',
                        help="The path of the output directory.",
                        type=str,
                        default='./data/sessions/')
    parser.add_argument(
        '-l',
        '--log-level',
        help="The level of details to print when running.",
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='info')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=getattr(logging, args.log_level.upper()))
    main(args)
    logging.info("That's all folks!")
