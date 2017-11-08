# -*- coding: utf-8 -*-
"""Functionality to check for the availability and version of dependencies."""

from __future__ import print_function
from __future__ import unicode_literals

import re


# Dictionary that contains version tuples per module name.
#
# A version tuple consists of:
# (version_attribute_name, minimum_version, maximum_version, is_required)
#
# Where version_attribute_name is either a name of an attribute,
# property or method.
PYTHON_DEPENDENCIES = {
${python_dependencies}}

_VERSION_SPLIT_REGEX = re.compile(r'\.|\-')


def _CheckPythonModule(
    module_name, version_attribute_name, minimum_version,
    is_required=True, maximum_version=None, verbose_output=True):
  """Checks the availability of a Python module.

  Args:
    module_name (str): name of the module.
    version_attribute_name (str): name of the attribute that contains
       the module version or method to retrieve the module version.
    minimum_version (str): minimum required version.
    is_required (Optional[bool]): True if the Python module is a required
        dependency.
    maximum_version (Optional[str]): maximum required version. Should only be
        used if there is a later version that is not supported.
    verbose_output (Optional[bool]): True if output should be verbose.

  Returns:
    bool: True if the Python module is available and conforms to
        the minimum required version, False otherwise.
  """
  module_object = _ImportPythonModule(module_name)
  if not module_object:
    if not is_required:
      print('[OPTIONAL]\tmissing: {0:s}.'.format(module_name))
      return True

    print('[FAILURE]\tmissing: {0:s}.'.format(module_name))
    return False

  if not version_attribute_name or not minimum_version:
    if verbose_output:
      print('[OK]\t\t{0:s}'.format(module_name))
    return True

  module_version = None
  if not version_attribute_name.endswith('()'):
    module_version = getattr(module_object, version_attribute_name, None)
  else:
    version_method = getattr(module_object, version_attribute_name[:-2], None)
    if version_method:
      module_version = version_method()

  if not module_version:
    print((
        '[FAILURE]\tunable to determine version information '
        'for: {0:s}').format(module_name))
    return False

  # Make sure the module version is a string.
  module_version = '{0!s}'.format(module_version)

  # Split the version string and convert every digit into an integer.
  # A string compare of both version strings will yield an incorrect result.
  module_version_map = list(
      map(int, _VERSION_SPLIT_REGEX.split(module_version)))
  minimum_version_map = list(
      map(int, _VERSION_SPLIT_REGEX.split(minimum_version)))

  if module_version_map < minimum_version_map:
    print((
        '[FAILURE]\t{0:s} version: {1!s} is too old, {2!s} or later '
        'required.').format(module_name, module_version, minimum_version))
    return False

  if maximum_version:
    maximum_version_map = list(
        map(int, _VERSION_SPLIT_REGEX.split(maximum_version)))
    if module_version_map > maximum_version_map:
      print((
          '[FAILURE]\t{0:s} version: {1!s} is too recent, {2!s} or earlier '
          'required.').format(module_name, module_version, maximum_version))
      return False

  if verbose_output:
    print('[OK]\t\t{0:s} version: {1!s}'.format(module_name, module_version))

  return True


def _CheckSQLite3(verbose_output=True):
  """Checks the availability of sqlite3.

  Args:
    verbose_output (Optional[bool]): True if output should be verbose.

  Returns:
    bool: True if the sqlite3 Python module is available, False otherwise.
  """
  # On Windows sqlite3 can be provided by both pysqlite2.dbapi2 and
  # sqlite3. sqlite3 is provided with the Python installation and
  # pysqlite2.dbapi2 by the pysqlite2 Python module. Typically
  # pysqlite2.dbapi2 would contain a newer version of sqlite3, hence
  # we check for its presence first.
  module_name = 'pysqlite2.dbapi2'
  minimum_version = '3.7.8'

  module_object = _ImportPythonModule(module_name)
  if not module_object:
    module_name = 'sqlite3'

  module_object = _ImportPythonModule(module_name)
  if not module_object:
    print('[FAILURE]\tmissing: {0:s}.'.format(module_name))
    return False

  module_version = getattr(module_object, 'sqlite_version', None)
  if not module_version:
    return False

  # Split the version string and convert every digit into an integer.
  # A string compare of both version strings will yield an incorrect result.
  module_version_map = list(
      map(int, _VERSION_SPLIT_REGEX.split(module_version)))
  minimum_version_map = list(
      map(int, _VERSION_SPLIT_REGEX.split(minimum_version)))

  if module_version_map < minimum_version_map:
    print((
        '[FAILURE]\t{0:s} version: {1!s} is too old, {2!s} or later '
        'required.').format(module_name, module_version, minimum_version))
    return False

  if verbose_output:
    print('[OK]\t\t{0:s} version: {1!s}'.format(module_name, module_version))

  return True


def _ImportPythonModule(module_name):
  """Imports a Python module.

  Args:
    module_name (str): name of the module.

  Returns:
    module: Python module or None if the module cannot be imported.
  """
  try:
    module_object = list(map(__import__, [module_name]))[0]
  except ImportError:
    return

  # If the module name contains dots get the upper most module object.
  if '.' in module_name:
    for submodule_name in module_name.split('.')[1:]:
      module_object = getattr(module_object, submodule_name, None)

  return module_object


def CheckDependencies(verbose_output=True):
  """Checks the availability of the dependencies.

  Args:
    verbose_output (Optional[bool]): True if output should be verbose.

  Returns:
    bool: True if the dependencies are available, False otherwise.
  """
  print('Checking availability and versions of dependencies.')
  check_result = True

  for module_name, version_tuple in sorted(PYTHON_DEPENDENCIES.items()):
    if not _CheckPythonModule(
        module_name, version_tuple[0], version_tuple[1],
        is_required=version_tuple[3], maximum_version=version_tuple[2],
        verbose_output=verbose_output):
      check_result = False

  if not _CheckSQLite3(verbose_output=verbose_output):
    check_result = False

  if check_result and not verbose_output:
    print('[OK]')

  print('')
  return check_result