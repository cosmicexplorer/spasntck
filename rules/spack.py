from dataclasses import dataclass

from pants.backend.python.util_rules.pex import Pex, PexRequest
from pants.core.util_rules.external_tool import (
    DownloadedExternalTool,
    ExternalToolRequest,
    TemplatedExternalTool,
)
from pants.engine.platform import Platform
from pants.engine.rules import Get, SubsystemRule, collect_rules, rule


class SpackConfig(TemplatedExternalTool):,
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


@dataclass(frozen=True)
class SpackInstance:
  pex: Pex


@rule
async def create_spack_pex(spack_config: SpackConfig) -> SpackInstance:
  spack_sources = await Get(
    DownloadedExternalTool,
    ExternalToolRequest,
    spack_config.get_request(Platform.current),
  )
  spack_pex = await Get(Pex, PexRequest(
    output_filename=f'spack-v{spack_config.version}.pex',
    sources=spack_sources.digest,
    additional_args=['--preamble-file', 'bin/spack'],
    description=f"spack v{spack_config.version} pex request"
  ))
  return SpackInstance(spack_pex)


def rules():
  return [SubsystemRule(SpackConfig), *collect_rules()]
