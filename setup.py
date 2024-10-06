from setuptools import setup
from setuptools.command.build_py import build_py


class BuildPyCommand(build_py):
    def run(self):
        # TODO add additional build steps
        build_py.run(self)


setup(
    cmdclass={
        "build_py": BuildPyCommand,
    },
)
