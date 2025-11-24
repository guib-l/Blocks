import os
import sys
import subprocess
import typing   



class DependenciesMixin:
    """Mixin class for managing dependencies and context."""
    __envtype__ = 'DependenciesMixin'

    context: typing.Optional[dict] = None
    packages: typing.List[str] = []

    def __repr__(self):
        return f"DependenciesMixin(context={self.context}, packages={self.packages})"

    def get_dependencies(self) -> typing.List[str]:
        return self.packages.copy()

    def get_context(self) -> typing.Optional[dict]:
        return self.context.copy() if self.context else None

    def diff(self, other: 'DependenciesMixin') -> bool:
        if not isinstance(other, DependenciesMixin):
            raise TypeError(f"Expected DependenciesMixin, got {type(other)}")
        return self.context != other.context

    def merge(self, other: 'DependenciesMixin') -> bool:
        if not isinstance(other, DependenciesMixin):
            raise TypeError(f"Expected DependenciesMixin, got {type(other)}")
        
        self.context = other.context
        # Avoid duplicates when merging packages
        self.packages = list(set(self.packages + other.packages))
        return True

    def install_dependencies(self, package: str) -> None:
        raise NotImplementedError("Subclasses must implement install_dependencies")
    
    def uninstall_dependencies(self, package: str) -> None:
        raise NotImplementedError("Subclasses must implement uninstall_dependencies")

    def todict(self) -> dict:
        return {
            'context': self.context,
            'packages': self.packages
        }
    
    def fromdict(self, data: dict) -> None:
        self.context = data.get('context')
        self.packages = data.get('packages', [])










