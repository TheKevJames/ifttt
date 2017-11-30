import collections
import logging
import os

import google.cloud.datastore as datastore

from .base import BaseWatch


CACHE_KIND_PREFIX = os.environ.get('CACHE_KIND_PREFIX', 'IFTTT')
PROJECT = os.environ['GCLOUD_PROJECT']

logger = logging.getLogger(__name__)


class DatastoreWatch(BaseWatch):
    def __init__(self, name, if_fn, then_fns, kind, field):
        super().__init__(name, if_fn, then_fns)

        self.kind = kind
        self.kind_cacheable = '{}-{}'.format(CACHE_KIND_PREFIX, self.kind)
        self.field = field

        self.client = datastore.Client(PROJECT)

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
                context = None  # context only applies for aggregates
                yield eid, context, curr

    def refresh_cache(self):
        self.cache = collections.defaultdict(dict)

        query = self.client.query(kind=self.kind_cacheable)
        for result in query.fetch():
            self.cache[result.key.id_or_name] = result

    def update_cache(self, id_, value):
        with self.client.transaction():
            try:
                self.cache[id_] = self.client.get(self.cache[id_].key)
            except AttributeError:
                key = self.client.key(self.kind_cacheable, id_)
                self.cache[id_] = datastore.Entity(key=key)

            self.cache[id_][self.field] = value
            self.client.put(self.cache[id_])
