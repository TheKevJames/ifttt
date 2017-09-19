import asyncio
import logging
import os

import yaml

from .error import ConfigurationError
from .gcloud_datastore import DatastoreWatch


WATCH_DIR = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger(__name__)


class WatchFactory:
    @staticmethod
    def build(name, watch_config, if_fn, then_fns):
        source = watch_config.get('source')
        if not source:
            raise ConfigurationError('missing watch source', watch_config)

        if source == 'datastore':
            try:
                kind = watch_config['kind']
                field = watch_config['field']
            except KeyError as e:
                raise ConfigurationError('malformed datastore watch',
                                         watch_config) from e

            return DatastoreWatch(name, if_fn, then_fns, kind, field)

        raise ConfigurationError('unsupported watch source', source)

    @classmethod
    def build_all(cls):
        with open(os.path.join(WATCH_DIR, 'config.yaml')) as f:
            actions = yaml.load(f)

        for action in actions:
            try:
                name = action['name']
                watch = action['watch']
                if_ = action.get('if', 'prev != curr')
                if_fn = eval('lambda id, prev, curr: {}'.format(if_))  # pylint: disable=eval-used
                then_fns = action['then']
            except KeyError as e:
                raise ConfigurationError('malformed action', action) from e

            watch = cls.build(name, watch, if_fn, then_fns)
            logger.debug('configured %s', watch)
            yield watch
