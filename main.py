import logging
from argparse import ArgumentParser

import aiorun

from UserParser import UserParser


async def main():
    argparser = ArgumentParser()
    argparser.add_argument('-i', '--input', default='habr.csv', type=str, help="Csv file with urls")
    argparser.add_argument('-o', '--output', default='out', type=str, help="Output directory")
    argparser.add_argument('-l', '--log', default="INFO", type=str, help="Log level",
                           choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    args = argparser.parse_args()
    logging.basicConfig(
        level=args.log,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    async with UserParser(args.input, args.output) as parser:
        parsed = await parser.parse_users()
        logger.debug("Done. Parsed users: %s", parsed)
        logger.debug("Already parsed files: %s", parser.parsed_urls)


if __name__ == '__main__':
    aiorun.run(main())
