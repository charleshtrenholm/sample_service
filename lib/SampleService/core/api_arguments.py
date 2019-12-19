'''
Contains helper functions for translating between the SDK API and the core Samples code.
'''

# TODO TEST

from uuid import UUID
from typing import Dict, Any, Optional, Tuple
import datetime

from SampleService.core.core_types import PrimitiveType
from SampleService.core.sample import Sample, SampleNode as _SampleNode
from SampleService.core.sample import SubSampleType as _SubSampleType
from SampleService.core.arg_checkers import not_falsy as _not_falsy
from SampleService.core.errors import IllegalParameterError as _IllegalParameterError

ID = 'id'
''' The ID of a sample. '''


def get_id_from_object(obj: Dict[str, Any]) -> Optional[UUID]:
    '''
    Given a dict, get a sample ID from the dict if it exists, using the key 'id'.

    If None or an empty dict is passed to the method, None is returned.

    :params obj: The dict wherein the ID can be found.
    :returns: The ID, if it exists, or None.
    :raises IllegalParameterError: If the ID is provided but is invalid.
    '''
    id_ = None
    if obj and obj.get(ID):
        if type(obj[ID]) != str:
            raise _IllegalParameterError(f'Sample ID {obj[ID]} must be a UUID string')
        try:
            id_ = UUID(obj[ID])
        except ValueError as _:  # noqa F841
            raise _IllegalParameterError(f'Sample ID {obj[ID]} must be a UUID string')
    return id_


def datetime_to_epochmilliseconds(d: datetime.datetime) -> int:
    '''
    Convert a datetime object to epoch milliseconds.

    :param d: The datetime.
    :returns: The date in epoch milliseconds.
    '''
    return round(_not_falsy(d, 'd').timestamp() * 1000)


def create_sample_params(params: Dict[str, Any]) -> Tuple[Sample, Optional[UUID], Optional[int]]:
    '''
    Process the input from the create_sample API call and translate it into standard types.

    :param params: The unmarshalled JSON recieved from the API as part of the create_sample
        call.
    :returns: A tuple of the sample to save, the UUID of the sample for which a new version should
        be created or None if an entirely new sample should be created, and the previous version
        of the sample expected when saving a new version.
    '''
    if params is None:
        raise ValueError('params may not be None')
    if type(params.get('sample')) != dict:
        raise _IllegalParameterError('params must contain sample key that maps to a structure')
    s = params['sample']
    if type(s.get('node_tree')) != list:
        raise _IllegalParameterError('sample node tree must be present and a list')
    if s.get('name') is not None and type(s.get('name')) != str:
        raise _IllegalParameterError('sample name must be omitted or a string')
    nodes = []
    for i, n in enumerate(s['node_tree']):
        if type(n) != dict:
            raise _IllegalParameterError(f'Node at index {i} is not a structure')
        if type(n.get('id')) != str:
            raise _IllegalParameterError(
                f'Node at index {i} must have an id key that maps to a string')
        try:
            type_ = _SubSampleType(n.get('type'))
        except ValueError:
            raise _IllegalParameterError(
                f'Node at index {i} has an invalid sample type: {n.get("type")}')
        if n.get('parent') and type(n.get('parent')) != str:
            raise _IllegalParameterError(
                f'Node at index {i} has a parent entry that is not a string')
        nodes.append(_SampleNode(
            n.get('id'),
            type_,
            n.get('parent'),
            _check_meta(n.get('meta_controlled'), i, 'controlled metadata'),
            _check_meta(n.get('meta_user'), i, 'user metadata')))

    id_ = get_id_from_object(s)

    pv = params.get('prior_version')
    if pv is not None and type(pv) != int:
        raise _IllegalParameterError('prior_version must be an integer if supplied')
    s = Sample(nodes, s.get('name'))
    return (s, id_, pv)


def _check_meta(m, index, name) -> Optional[Dict[str, Dict[str, PrimitiveType]]]:
    if not m:
        return None
    if type(m) != dict:
        raise _IllegalParameterError(f"Node at index {index}'s {name} entry must be a mapping")
    # since this is coming from JSON we assume keys are strings
    for k1 in m:
        if type(m[k1]) != dict:
            raise _IllegalParameterError(f"Node at index {index}'s {name} entry does " +
                                         f"not have a dict as a value at key {k1}")
        for k2 in m[k1]:
            v = m[k1][k2]
            if type(v) != str and type(v) != int and type(v) != float and type(v) != bool:
                raise _IllegalParameterError(
                    f"Node at index {index}'s {name} entry does " +
                    f"not have a primitive type as the value at {k1}/{k2}")
    return m
