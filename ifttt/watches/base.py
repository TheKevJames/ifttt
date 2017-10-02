import asyncio
import collections
import logging
import shlex
import subprocess

from .error import ActionError


logger = logging.getLogger(__name__)


class BaseWatch:
    def __init__(self, name, if_fn, then_fns):
        self.name = name
        self.if_fn = if_fn
        self.then_fns = then_fns

        self.cache = collections.defaultdict(dict)

    def collect_activations(self):
        raise NotImplementedError

    def refresh_cache(self):
        raise NotImplementedError

    def update_cache(self, id_, value):
        raise NotImplementedError

    async def poll(self):
        self.refresh_cache()

        for (id_, value) in self.collect_activations():
            logger.info('found change for %s on id %s', self, id_)
            self.update_cache(id_, value)
            await self.run_actions(id_, value)

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

    async def run_actions(self, id_, value):
        try:
            for then_fn in self.then_fns:
                await self.run(then_fn.format(id=id_, value=value))
        except ActionError as e:
            logger.error('could not run actions for %s on id %s', self, id_)
            logger.exception(e)
