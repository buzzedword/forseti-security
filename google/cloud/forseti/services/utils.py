# Copyright 2017 The Forseti Security Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Forseti Server utilities."""

from itertools import izip
import logging

# TODO: The next editor must remove this disable and correct issues.
# pylint: disable=missing-type-doc,missing-return-type-doc,missing-return-doc
# pylint: disable=missing-param-doc
# pylint: disable=protected-access


def autoclose_stream(f):
    """Decorator to close gRPC stream."""

    def wrapper(*args):
        """Wrapper function, checks context state to close stream.

        Args:
            *args (list): All arguments provided to the wrapped function.

        Yields:
            object: Whatever the wrapped function yields to the stream.
        """

        def closed(context):
            """Returns true iff the connection is closed."""

            return context._state.client == 'closed'
        context = args[-1]
        for result in f(*args):
            yield result
            if closed(context):
                return
    return wrapper


def logcall(f, level=logging.CRITICAL):
    """Call logging decorator."""

    def wrapper(*args, **kwargs):
        """Implements the log wrapper including parameters and result."""
        logging.log(level, 'enter %s(%s)', f.__name__, args)
        result = f(*args, **kwargs)
        logging.log(level, 'exit %s(%s) -> %s', f.__name__, args, result)
        return result
    return wrapper


def mutual_exclusive(lock):
    """ Mutex decorator. """

    def wrap(f):
        """Decorator generator."""
        def function(*args, **kw):
            """Decorated functionality, mutexing wrapped function."""
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()
        return function
    return wrap


def oneof(*args):
    """Returns true iff one of the parameters is true."""

    return len([x for x in args if x]) == 1


def full_to_type_name(full_resource_name):
    """Creates a type/name format from full resource name."""

    return '/'.join(full_resource_name.split('/')[-2:])


def to_full_resource_name(full_parent_name, resource_type_name):
    """Creates a full resource name by parent full name and type name."""

    return '{}{}/'.format(full_parent_name, resource_type_name)


def to_type_name(resource_type, resource_name):
    """Creates a type/name from type and name."""

    return '{}/{}'.format(resource_type, resource_name)


def split_type_name(resource_type_name):
    """."""

    return resource_type_name.split('/')


def resource_to_type_name(resource):
    """Creates a type/name format from a resource dbo."""

    return resource.type_name


def get_sql_dialect(session):
    """Return the active SqlAlchemy dialect."""

    return session.bind.dialect.name

def get_resources_from_full_name(full_name):
    """Parse resource info from full name.

    Args:
        full_name (str): Full name of the resource in hierarchical format.
            Example of a full_name:
            organization/88888/project/myproject/firewall/99999/
            full_name has a trailing / that needs to be removed.


    Yields:
        iterator: strings of resource_type and resource_id
    """

    full_name_parts = full_name.split('/')[:-1]
    full_name_parts.reverse()
    resource_iter = iter(full_name_parts)
    for resource_id, resource_type in izip(resource_iter, resource_iter):
        yield resource_type, resource_id