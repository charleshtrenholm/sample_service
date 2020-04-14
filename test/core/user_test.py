from pytest import raises

from SampleService.core.errors import MissingParameterError, IllegalParameterError
from SampleService.core.user import UserID

from core.test_utils import assert_exception_correct


def test_init():
    u = UserID('foo')

    assert u.id == 'foo'
    assert str(u) == 'foo'

    u = UserID('u')

    assert u.id == 'u'
    assert str(u) == 'u'

    u = UserID('u⎇a')

    assert u.id == 'u⎇a'
    assert str(u) == 'u⎇a'


def test_init_fail():
    _init_fail(None, MissingParameterError('userid'))
    _init_fail('   \t    ', MissingParameterError('userid'))
    _init_fail('foo \t bar', IllegalParameterError('userid contains control characters'))


def _init_fail(u, expected):
    with raises(Exception) as got:
        UserID(u)
    assert_exception_correct(got.value, expected)


def test_equals():
    assert UserID('u') == UserID('u')

    assert UserID('u') != 'u'

    assert UserID('u') != UserID('v')


def test_hash():
    # string hashes will change from instance to instance of the python interpreter, and therefore
    # tests can't be written that directly test the hash value. See
    # https://docs.python.org/3/reference/datamodel.html#object.__hash__
    assert hash(UserID('u')) == hash(UserID('u'))

    assert hash(UserID('u')) != hash(UserID('v'))
