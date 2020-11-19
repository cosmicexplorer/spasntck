import os
from abc import ABCMeta, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import ClassVar

from pants.engine.fs import Digest
from pants.engine.process import BinaryPath, BinaryPathRequest, BinaryPathTest, BinaryPaths, ProcessResult, Process
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.unions import union
from pants.subsystem.subsystem import Subsystem


@dataclass(frozen=True)
class Git:
    inner: BinaryPath

    def get_path(self) -> str:
        return self.inner.path


@rule
async def collect_git() -> Git:
    path_value = os.environ['PATH']
    env_paths = path_value.split(':')
    git_paths = await Get(
        BinaryPaths,
        BinaryPathRequest(
            binary_name='git',
            search_paths=env_paths,
            test=BinaryPathTest(args=['--version']),
        )
    )
    git_bin = git_paths.first_path
    if git_bin is None:
        raise OSError("Could not find 'git'. The user's PATH is: {path_value}.")
    return Git(git_bin)


@dataclass(frozen=True)
class GitRepoRequest:
    origin: str


@dataclass(frozen=True)
class GitRepoResult:
    digest: Digest

@rule
async def git_clone_repo(git: Git, repo: GitRepoRequest) -> GitRepoResult:
    shallow_clone = await Get(
        ProcessResult,
        Process(
            argv=[
                git.get_path(),
                'clone',
                '--depth=1',
                repo.origin,
                'known_clone',
            ],
            output_directories=[
                'known_clone',
            ],
        )
    )
    return GitRepoResult(digest=shallow_clone.output_digest)


@dataclass(frozen=True)
class GitRevParseable:
    spec: str


@dataclass(frozen=True)
class GitCheckoutRequest:
    repo: GitRepoRequest
    rev: GitRevParseable


@dataclass(frozen=True)
class GitCheckoutResult:
    digest: Digest


@rule
async def checkout_rev(git: Git, checkout: GitCheckoutRequest) -> GitCheckoutResult:
    repo = await Get(GitRepoResult, GitRepoRequest, checkout.repo)
    checked_out = await Get(
        ProcessResult,
        Process(
            argv=[
                git.get_path(),
                'checkout',
                checkout.rev.spec,
            ]
            input_digest=repo.digest,
            output_directories=['.'],
        )
    )
    return GitCheckoutResult(digest=checked_out.digest)


@union
class GitSourceTool(Subsystem, metaclass=ABCMeta):
    """Same as the docstring for `ExternalTool`.

    TODO: upstream an ExternalToolBase which decouples the version selection from any specific URL.
    """

    default_origin: str
    default_version: ClassVar[str]

    @classproperty
    def name(cls):
        """The name of the tool, for use in user-facing messages.

        Derived from the classname, but subclasses can override, e.g., with a classproperty.
        """
        return cls.__name__.lower()

    @classmethod
    def register_options(cls, register):
        super().register_options(register)
        register(
            "--origin",
            type=str,
            default=cls.default_origin,
            advanced=True,
            help=f"Use this upstream for {cls.name}.",
        )

        register(
            "--version",
            type=str,
            default=cls.default_version,
            advanced=True,
            help=f"Use this version of {cls.name}.",
        )

    @property
    def origin(self) -> str:
        return cast(str, self.options.origin)

    @property
    def version(self) -> str:
        return cast(str, self.options.version)

    def into_checkout_request(self) -> GitCheckoutRequest:
        return GitCheckoutRequest(
            repo=GitRepoRequest(origin=self.origin),
            rev=GitRevParseable(spec=self.version),
        )


@dataclass(unsafe_hash=True)
class GitSourceRequest:
    # TODO: https://github.com/pantsbuild/pants/pull/8542 to avoid this wrapper struct!
    inner: GitSourceTool


@rule
async def fetch_git(req: GitSourceRequest) -> GitCheckoutResult:
    checkout_request = req.inner.into_checkout_request()
    return await Get(GitCheckoutResult, GitCheckoutRequest, checkout_request)


def rules():
    return [*collect_rules()]
