import asyncio
import logging
import os
import sys

from .json_logging import configure
from .watches import WatchFactory


POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', '30'))

logger = logging.getLogger('ifttt')


async def main():
    watches = list(WatchFactory.build_all())

    while True:
        await asyncio.gather(*{w.poll() for w in watches})
        await asyncio.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    configure()

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit(0)
