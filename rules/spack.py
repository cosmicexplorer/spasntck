from pants.engine.rules import Get, collect_rules, rule
# from pants.backend.python.subsystems.python_tool_base import PythonToolBase


# class Spack(PythonToolBase):
#   """The build tool for HPC (https://spack.io)."""

#   options_scope = "spack-config"
#   default_version = "spack==0.16.0"


def rules():
  return [*collect_rules()]
