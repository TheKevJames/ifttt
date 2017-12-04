import collections
import logging
import os

from .gcloud_datastore import DatastoreWatch


CACHE_KIND_PREFIX = os.environ.get('CACHE_KIND_PREFIX', 'IFTTT')

logger = logging.getLogger(__name__)


class AggregatedDatastoreWatch(DatastoreWatch):
    def __init__(self, name, if_fn, then_fns, kind, field, aggregate_fn,
                 context_field, context_only=None):
        super().__init__(name, if_fn, then_fns, kind, field)

        self.aggregate_fn = aggregate_fn
        self.context_field = context_field
        self.context_only = {None if c == 'None' else c
                             for c in context_only or list()}

        self.cache_key = '{}-{}'.format(kind, field)
        self.kind_cacheable = '{}-{}'.format(CACHE_KIND_PREFIX, 'Aggregates')

    def __repr__(self):
        return "AggregatedDatastoreWatch '{}'".format(self.name)

    def collect_activations(self):
        collector = collections.defaultdict(list)

        query = self.client.query(kind=self.kind)
        for result in query.fetch():
            value = result.get(self.field)
            if not value:
                continue  # TODO: aggregates across nulls

            context = None
            if self.context_field:
                context = result.get(self.context_field)
                context = context or None  # TODO: consider handling nulls vs ''

                if self.context_only and context not in self.context_only:
                    logger.debug('skipping ignored context %s', context)
                    continue

            collector[context].append(value)

        for context, collection in collector.items():
            cache_key = self.cache_key
            if context:
                cache_key += '-{}'.format(context)

            prev = self.cache[cache_key].get(self.field, 0)  # TODO: aggregates across nulls
            curr = self.aggregate_fn(collection)

            # The concept of an "id" for an aggregate doesn't make too much
            # sense, since by nature we are examining the entire Kind rather
            # than just a single record with some ID. Using the cache_key here
            # encodes roughly the right amount of data to get the gist across.
            id_ = self.cache_key

            if self.if_fn(id_, prev, curr):
                yield id_, context, curr
