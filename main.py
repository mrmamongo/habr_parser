import asyncio
import logging
from argparse import ArgumentParser

from UserParser import UserParser


async def main():
    argparser = ArgumentParser()
    argparser.add_argument('-i', '--input', default='habr.csv', type=str, help="Csv file with urls")
    argparser.add_argument('-o', '--output', default='out', type=str, help="Output directory")
    argparser.add_argument('-l', '--log', default="DEBUG", type=str, help="Log level",
                           choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    argparser.add_argument('-p', '--proxy', default='socks5://testvicky2:2a31eb@193.23.50.245:10490', type=str,
                           help="Proxy server")
    argparser.add_argument('-v', '--verbose', action='store_true', help="Verbose run")
    args = argparser.parse_args()
    logging.basicConfig(
        filename='parser.log',
        level=args.log,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    async with UserParser(args.input, args.output, args.proxy, args.verbose) as parser:
        parsed = await parser.parse_users()
        logger.info("Done. Parsed users: %s", parsed)
        logger.debug("Already parsed files: %s", parser.parsed_urls)


if __name__ == '__main__':
    asyncio.run(main())
