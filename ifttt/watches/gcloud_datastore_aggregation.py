import os

from .gcloud_datastore import DatastoreWatch


CACHE_KIND_PREFIX = os.environ.get('CACHE_KIND_PREFIX', 'IFTTT')


class AggregatedDatastoreWatch(DatastoreWatch):
    def __init__(self, name, if_fn, then_fns, kind, field, aggregate_fn):
        super().__init__(name, if_fn, then_fns, kind, field)

        self.aggregate_fn = aggregate_fn

        self.cache_key = '{}-{}'.format(kind, field)
        self.kind_cacheable = '{}-{}'.format(CACHE_KIND_PREFIX, 'Aggregates')

    def __repr__(self):
        return "AggregatedDatastoreWatch '{}'".format(self.name)

    def collect_activations(self):
        collector = list()

        query = self.client.query(kind=self.kind)
        for result in query.fetch():
            value = result.get(self.field)
            if not value:
                continue  # TODO: aggregates across nulls

            collector.append(value)

        prev = self.cache[self.cache_key].get(self.field, 0)  # TODO: aggregates across nulls
        curr = self.aggregate_fn(collector)
        if self.if_fn(self.cache_key, prev, curr):
            yield self.cache_key, curr
