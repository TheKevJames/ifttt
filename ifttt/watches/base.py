import asyncio
import logging
import shlex
import subprocess

from .error import ActionError


logger = logging.getLogger(__name__)


class BaseWatch:
    @staticmethod
    async def run(then_fn):
        logger.debug("running '%s'", then_fn)
        p = subprocess.Popen(shlex.split(then_fn), stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        while True:
            code = p.poll()
            if code is None:
                await asyncio.sleep(0.5)
                continue

            if code == 0:
                return

            stdout, stderr = p.communicate()
            raise ActionError('got error code running action', code, then_fn,
                              stdout, stderr)
