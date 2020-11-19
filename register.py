from spasntck.rules.fetch.git_checkout import rules as git_rules
from spasntck.rules.spack import rules as spack_rules


def rules():
    return [
        *git_rules(),
        *spack_rules(),
    ]
