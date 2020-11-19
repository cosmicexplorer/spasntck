from pants.core.util_rules.external_tool import (
    DownloadedExternalTool,
    ExternalToolRequest,
    TemplatedExternalTool,
)
from pants.engine.rules import Get, SubsystemRule, collect_rules, rule


class Spack(TemplatedExternalTool):,
  """The build tool for HPC (https://spack.io)."""

  options_scope = "spack-config"
  default_version = "0.16.0"
  default_known_versions = [
    "0.16.0|darwin|064b2532c70916c7684d4c7c973416ac32dd2ea15f5c392654c75258bfc8c6c2|5512800",
    "0.16.0|linux|064b2532c70916c7684d4c7c973416ac32dd2ea15f5c392654c75258bfc8c6c2|5512800",
  ]
  default_url_template = (
    "https://github.com/spack/spack/releases/download/v{version}/spack-{version}.tar.gz"
  )


def rules():
  return [SubsystemRule(Spack), *collect_rules()]
