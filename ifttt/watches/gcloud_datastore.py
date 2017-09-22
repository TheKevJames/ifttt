import collections
import logging
import os

import google.cloud.datastore as datastore

from .base import BaseWatch
from .error import ActionError


CACHE_KIND_PREFIX = os.environ.get('CACHE_KIND_PREFIX', 'IFTTT')
PROJECT = os.environ['GCLOUD_PROJECT']

logger = logging.getLogger(__name__)


class DatastoreWatch(BaseWatch):
    def __init__(self, name, if_fn, then_fns, kind, field):  # pylint: disable=too-many-arguments
        self.name = name
        self.if_fn = if_fn
        self.then_fns = then_fns

        self.kind = kind
        self.field = field

        self.client = datastore.Client(PROJECT)

        self.cache = collections.defaultdict(dict)

    def __repr__(self):
        return "DatastoreWatch '{}'".format(self.name)

    def __str__(self):
        return '[{}: {}->{}]'.format(self.__repr__(), self.kind, self.field)

    def collect_activations(self):
        query = self.client.query(kind=self.kind)
        for result in query.fetch():
            eid = result.key.id_or_name
            prev = self.cache[eid].get(self.field)
            curr = result.get(self.field)

            # Only run actions when if_fn denotes an activation.
            if self.if_fn(eid, prev, curr):
                yield eid, curr

    def refresh_cache(self):
        cache_kind = '{}-{}'.format(CACHE_KIND_PREFIX, self.kind)
        query = self.client.query(kind=cache_kind)

        self.cache = collections.defaultdict(dict)
        for result in query.fetch():
            self.cache[result.key.id_or_name] = result

    async def run_actions(self, eid, value):
        try:
            for then_fn in self.then_fns:
                await self.run(then_fn.format(id=eid, value=value))
        except ActionError as e:
            logger.error('could not run actions for %s on id %s', self, eid)
            logger.exception(e)

    async def poll(self):
        self.refresh_cache()

        for (eid, value) in self.collect_activations():
            logger.info('found change for %s on id %s', self, eid)

            # update cache
            with self.client.transaction():
                self.cache[eid] = self.client.get(self.cache[eid].key)
                self.cache[eid][self.field] = value
                self.client.put(self.cache[eid])

            await self.run_actions(eid, value)
