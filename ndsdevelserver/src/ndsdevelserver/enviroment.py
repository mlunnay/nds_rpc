# Copyright (c) 2008, Michael Lunnay <mlunnay@gmail.com.au>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# This is a based apon, and uses some code from Trac (http://trac.edgewall.org)

# Copyright (C) 2003-2008 Edgewall Software
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  3. The name of the author may not be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import os
import imp
from glob import glob
import pkg_resources
from pkg_resources import working_set, DistributionNotFound, VersionConflict, \
                          UnknownExtra

from config import Config
from plugin import PluginManager

__all__ = ['Environment']

# default plugins from within the module
_DEFAULT_PLUGINS = ['filetransfer', 'rpclogging', 'update']

class Environment(PluginManager):
    """Centralized environment for ndsdevelserver."""
    
    def __init__(self):
        # TODO: handle invalid config
        self.config = Config('ndsds.cfg')
        self.setup_log()
        
        load_components(self, auto_enable=False)
        self.load_default_plugins()
    
    def plugin_activated(self, component):
        """Initialize additional member variables for plugins.
        
        Every plugin activated through the `Environment` object gets three
        member variables: `env` (the environment object), `config` (the
        environment configuration) and `log` (a logger object)."""
        
        component.env = self
        component.config = self.config
        component.log = self.log

    def is_plugin_enabled(self, cls):
        """Implemented to only allow activation of plugins that are not
        disabled in the configuration.
        
        This is called by the `PluginManager` base class when a component is
        about to be activated. If this method returns false, the component does
        not get activated."""
        
        if not isinstance(cls, basestring):
            component_name = (cls.__module__ + '.' + cls.__name__).lower()
        else:
            component_name = cls.lower()

        if self.config.get('plugins', {}).has_key(component_name):
            return self.config.get('plugins', {})[component_name] == True

        # By default, all components in the ndsdevelserver package are enabled
        return component_name.startswith('ndsdevelserver.')
    
    def setup_log(self):
        cfg = self.config.get('log', {})
        logfile = cfg.get('file', 'logs/ndsdevelserve.log')
        format = cfg.get('format', '%(asctime)s %(levelname)-8s [%(module)s] %(message)s')
        level = cfg.get('level', 'ERROR')
        dateformat = cfg.get('dateformat', None)
        
        logger = logging.getLogger('ndsdevelserver')
        
        if dateformat == None:
            formatter = logging.Formatter(format)
        else:
            formatter = logging.Formatter(format, dateformat)
        
        handler = logging.FileHandler(logfile)
        logger.addHandler(handler)
        self.log = logger
    
    def load_default_plugins(self):
        """Load the default plugins from within the module."""
        
        for plugin in _DEFAULT_PLUGINS:
            module = imp.load_source(plugin, '%s.py' % plugin)

def _enable_plugin(env, module):
    """Enable the given plugin module by adding an entry to the enabled dict.
    """
    env.enabled[module] = True

def load_eggs(entry_point_name):
    """Loader that loads any eggs on the search path and `sys.path`."""
    
    def _load_eggs(env, search_path, auto_enable=None):
        # Note that the following doesn't seem to support unicode search_path
        distributions, errors = working_set.find_plugins(
            pkg_resources.Environment(search_path)
        )
        for dist in distributions:
            env.log.debug('Adding plugin %s from %s', dist, dist.location)
            working_set.add(dist)

        def _log_error(item, e):
            if isinstance(e, DistributionNotFound):
                env.log.debug('Skipping "%s": ("%s" not found)', item, e)
            elif isinstance(e, VersionConflict):
                env.log.error('Skipping "%s": (version conflict "%s")',
                              item, e)
            elif isinstance(e, UnknownExtra):
                env.log.error('Skipping "%s": (unknown extra "%s")', item, e)
            elif isinstance(e, ImportError):
                env.log.error('Skipping "%s": (can\'t import "%s")', item, e)
            else:
                env.log.error('Skipping "%s": (error "%s")', item, e)

        for dist, e in errors.iteritems():
            _log_error(dist, e)

        for entry in working_set.iter_entry_points(entry_point_name):
            env.log.debug('Loading %s from %s', entry.name,
                          entry.dist.location)
            try:
                entry.load(require=True)
            except (ImportError, DistributionNotFound, VersionConflict,
                    UnknownExtra), e:
                _log_error(entry, e)
            else:
                if os.path.dirname(entry.dist.location) == auto_enable:
                    _enable_plugin(env, entry.module_name)
    return _load_eggs

def load_py_files():
    """Loader that look for Python source files in the plugins directories,
    which simply get imported, thereby registering them with the plugin
    manager if they define any plugins.
    """
    
    def _load_py_files(env, search_path, auto_enable=None):
        for path in search_path:
            plugin_files = glob(os.path.join(path, '*.py'))
            for plugin_file in plugin_files:
                try:
                    plugin_name = os.path.basename(plugin_file[:-3])
                    env.log.debug('Loading file plugin %s from %s' % \
                                  (plugin_name, plugin_file))
                    if plugin_name not in sys.modules:
                        module = imp.load_source(plugin_name, plugin_file)
                    if path == auto_enable:
                        _enable_plugin(env, plugin_name)
                except Exception, e:
                    env.log.error('Failed to load plugin from %s', plugin_file,
                                  exc_info=True)

    return _load_py_files

def load_components(env, extra_path=None, entry_point="ndsds.plugins", loaders=None, auto_enable=False):
    """Load all plugins found on the given search path."""
    
    if loaders == None:
        loaders = (load_eggs(entry_point),load_py_files())
        
    plugins_dir = 'plugins'
    search_path = [plugins_dir]
    if extra_path:
        search_path += list(extra_path)

    if auto_enable:
        aenable = plugins_dir
    else:
        aenable = False

    for loadfunc in loaders:
        loadfunc(env, search_path, auto_enable=aenable)
