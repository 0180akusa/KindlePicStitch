from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('numpy')
datas = collect_data_files('numpy')

def pre_safe_import_module(api):
    # 添加 numpy.f2py 相关的模块
    api.add_runtime_module('numpy.f2py')
    api.add_runtime_module('numpy.f2py.diagnose')
    api.add_runtime_module('numpy.f2py.f2py2e')
    api.add_runtime_module('numpy.f2py.f90mod_rules')
    api.add_runtime_module('numpy.f2py.func2subr')
    api.add_runtime_module('numpy.f2py.rules')
    api.add_runtime_module('numpy.f2py.use_rules')
    api.add_runtime_module('numpy.f2py.crackfortran')
    api.add_runtime_module('numpy.f2py.cb_rules')
    api.add_runtime_module('numpy.f2py.auxfuncs')
    api.add_runtime_module('numpy.f2py.capi_maps')
    api.add_runtime_module('numpy.f2py.common_rules')
    api.add_runtime_module('numpy.f2py.cfuncs')
    api.add_runtime_module('numpy.f2py.rules')