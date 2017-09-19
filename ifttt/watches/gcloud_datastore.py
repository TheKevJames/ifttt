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

    def __repr__(self):
        return "DatastoreWatch '{}'".format(self.name)

    def __str__(self):
        return '[{}: {}->{}]'.format(self.__repr__(), self.kind, self.field)

    async def poll(self):
        cache_kind = '{}-{}'.format(CACHE_KIND_PREFIX, self.kind)
        query = self.client.query(kind=cache_kind)

        cache = collections.defaultdict(dict)
        for result in query.fetch():
            cache[result.key.id_or_name] = result

        query = self.client.query(kind=self.kind)
        for result in query.fetch():
            eid = result.key.id_or_name
            prev = cache[eid].get(self.field)
            curr = result.get(self.field)

            # Only run actions when if_fn denotes an activation.
            if not self.if_fn(eid, prev, curr):
                continue

            logger.info('found change for %s on id %s', self.__str__(), eid)

            # update cache
            # TODO: s/put/patch
            cache[eid][self.field] = curr
            self.client.put(cache[eid])

            try:
                for then_fn in self.then_fns:
                    await self.run(then_fn.format(id=eid, value=curr))
            except ActionError as e:
                logger.error('could not run actions for watch %s on id %s',
                             self.__str__(), eid)
                logger.exception(e)
