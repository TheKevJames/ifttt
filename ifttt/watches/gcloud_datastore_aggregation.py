import collections
import os

from .gcloud_datastore import DatastoreWatch


CACHE_KIND_PREFIX = os.environ.get('CACHE_KIND_PREFIX', 'IFTTT')


class AggregatedDatastoreWatch(DatastoreWatch):
    def __init__(self, name, if_fn, then_fns, kind, field, aggregate_fn,
                 context_field):
        super().__init__(name, if_fn, then_fns, kind, field)

        self.aggregate_fn = aggregate_fn
        self.context_field = context_field

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

            collector[context].append(value)

        for context, collection in collector.items():
            cache_key = self.cache_key
            if context:
                cache_key += '-{}'.format(context)

            prev = self.cache[cache_key].get(self.field, 0)  # TODO: aggregates across nulls
            curr = self.aggregate_fn(collection)
            if self.if_fn(self.cache_key, prev, curr):
                yield self.cache_key, context, curr
