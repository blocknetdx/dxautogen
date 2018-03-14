import sys
from cx_Freeze import setup, Executable
import os.path
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')


if sys.argv[-1] != "build":
    sys.argv.append("build")
  
setup(name = "dxautogen", version = "0.1", description = "dxautogen", executables = [Executable("dxconfgen.py")], options = {"build_exe": {"packages":["jinja2", "jinja2.ext", "asyncio"], "excludes":["numpy", "scipy"], "build_exe": "dxautogen"}})