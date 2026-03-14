
import sys

from typing import Optional, Any, Callable, Union, Iterable, List

from blocks.base import block
from blocks import BLOCK_PATH

from blocks.engine import INSTALLER

from blocks.base.register import Register

from blocks.engine.execute import Execute

from blocks.utils.logger import *
from blocks.utils.exceptions import PrototypeError,ErrorCode

from blocks.engine.environment import EnvironmentBase


from blocks.utils.exceptions import safe_operation


class Prototype(block.Block,Register):
    """Executable block prototype.

    A `Prototype` is a `Block` with an associated environment, executor and
    installer. It can be loaded from disk and executed by forwarding inputs to a
    registered callable.

    Attributes:
        __ntype__ (str): Object type marker used by the framework.

    Notes:
        The constructor expects configuration dictionaries inside `**config`
        (e.g. `environment_config`, `executor_config`, `installer_config`).
    """

    __ntype__ = "prototype"

    __slots__ = [
        'unique_environment',
        'installer',
        'environment',
        'executor',
    ]

    def __init__(
            self,
            unique_environment: bool = False,
            language: 'dict | Callable[..., dict] | None' = None,
            *,
            installer: 'Callable[..., Any] | None' = None,
            environment: 'Callable[..., Any]' = EnvironmentBase,
            executor: 'Callable[..., Any] | None' = None,
            **config
        ):
        """Initialize a `Prototype` instance.

        Args:
            unique_environment (bool): Whether this prototype should use a
                unique environment instance (behavior depends on the provided
                environment implementation).
            language (dict | Callable[..., dict] | None): Optional language
                preset. Pass a config dict (e.g. from
                :meth:`blocks.engine.language.Language.python3_pip`) or a
                zero-argument callable returning one. Its keys populate
                `installer`, `environment`, `executor` and their `_config`
                counterparts as defaults (explicit keyword arguments take
                precedence). **Construction-time only** — `language` is NOT
                stored by :meth:`to_dict`; the round-trip is preserved because
                the resolved concrete classes and their configs are serialized
                instead.
            installer (type | Callable | None): Installer class/factory used to
                create the `installer` instance. It is called as
                `installer(self, **installer_config)`.
            environment (type | Callable | None): Environment class/factory used
                to create the `environment` instance. It is called as
                `environment(**environment_config)`.
            executor (type | Callable | None): Optional executor class/factory.
                If `None`, a default :class:`blocks.engine.execute.Execute`
                backend is created.
            **config: Additional configuration. Expected keys include:

                - `environment_config` (dict): Passed to `environment(...)`.
                - `executor_config` (dict): Passed to `executor(...)` when a
                  custom executor is provided.
                - `installer_config` (dict): Passed to `installer(self, ...)`.
                - `allowed_name` (list[str]): Allowed method names for the
                  register (if supported by the register implementation).
                - `methods` (list): Optional methods to register.
                - `files` (list[str]): Optional files to register.

                Remaining keys are forwarded to the base `Block` constructor.

        Raises:
            PrototypeError: If executor/installer initialization fails.
            KeyError: If required config keys are missing (e.g.
                `environment_config`, `executor_config`, `installer_config`).
            Exception: Any exception raised by the provided environment,
                executor, installer, register, or `Block` initialization.
        """
        logger.info("Initializing Prototype instance")

        if language is not None:
            name = config.get('name', None)
            lang_config = language(
                name = f"{name}_pip" if name is not None else None,
                directory = config.get('directory', None)
            ) if callable(language) else language
            if installer is None:
                installer = lang_config.get('installer', installer)
            if environment is EnvironmentBase:
                environment = lang_config.get('environment', environment)
            if executor is None:
                executor = lang_config.get('executor', executor)
            for key in ('installer_config', 'environment_config', 'executor_config'):
                if key not in config:
                    config[key] = lang_config.get(key, {})

        self.unique_environment = unique_environment

        self._build_environment(environment, config.pop('environment_config'))
        self._build_executor(executor, config.pop('executor_config'))
        self._build_register(
            config.pop('allowed_name', []),
            config.pop('methods', []),
            config.pop('files', []),
        )

        install_config = config.pop('installer_config')
        super().__init__(allowed_name=self.allowed_name, **config)

        if installer is None:
            installer = INSTALLER.DEFAULT
        self._build_installer(installer, install_config)


    # ===========================================
    # Private build helpers
    # ===========================================

    def _build_environment(
            self,
            environment: 'Callable[..., Any]',
            environment_config: dict,
        ) -> None:
        self.environment = environment(**environment_config)

    def _build_executor(
            self,
            executor: 'Callable[..., Any] | None',
            exec_config: dict,
        ) -> None:
        if executor is None:
            self.executor = Execute(backend='default', build_backend=True)
        else:
            try:
                self.executor = executor(**exec_config)
            except PrototypeError as e:
                logger.critical("Executor didn't loaded")
                raise PrototypeError(
                    code=ErrorCode.PROTOTYPE_INIT_EXECUTOR,
                    message="Invalid executor object in parameters",
                    cause=e
                )

    def _build_register(
            self,
            allowed_name: list,
            methods: list,
            files: list,
        ) -> None:
        try:
            self.init_register(
                allowed_name,
                methods=methods,
                files=files,
                site_packages=getattr(
                    self.environment.environment, 'site_packages', None),
            )
        except PrototypeError as e:
            logger.critical("Register didn't load")
            raise PrototypeError(
                code=ErrorCode.PROTOTYPE_INIT_EXECUTOR,
                message="Invalid register configuration",
                cause=e
            )

    def _build_installer(
            self,
            installer: 'Callable[..., Any]',
            install_config: dict,
        ) -> None:
        try:
            self.installer = installer(self, **install_config)
        except PrototypeError as e:
            logger.critical("Installer is not seting up !")
            raise PrototypeError(
                code=ErrorCode.PROTOTYPE_INIT_INSTALLER,
                message="Invalid installer object",
                cause=e
            )


    # ===========================================
    # Dict serialization / deserialization
    # ===========================================

    def to_dict(self,):
        """Serialize the prototype into a dictionary.

        The returned mapping is compatible with :meth:`from_dict`.

        Returns:
            dict: A dictionary containing the base `Block` fields plus
            installer/environment/executor classes and their configuration.

        Raises:
            PrototypeError: If serialization fails.
        """

        logger.info(f"Transform Prototype {self.name} into dictionary")

        with safe_operation(
                'dict serialisation',
                code=ErrorCode.PROTOTYPE_SERIALIZE_ERR,
                ERROR=PrototypeError ):
            
            _dict = super().to_dict()
            _dict.update({
                'installer':self.installer.__class__,
                'installer_config':self.installer.to_config(),
                'environment':self.environment.__class__,
                'environment_config':self.environment.to_config() or {},
                'executor':self.executor.__class__,
                'executor_config':self.executor.to_config() or {},
            })
        return _dict
    
    @classmethod
    def from_dict(cls, **data):
        """Deserialize a `Prototype` from a dictionary.

        Args:
            **data: Keyword arguments forwarded to the constructor.

        Returns:
            Prototype: Instantiated prototype.

        Raises:
            PrototypeError: If deserialization fails.
        """

        with safe_operation(
                'dict deserialisation',
                code=ErrorCode.PROTOTYPE_DESERIALIZE_ERR,
                ERROR=PrototypeError ):
            return cls(**data)


    # ===========================================
    # Installater / Uninstaller
    # ===========================================

    def install(self, 
                **properties):
        """Install dependencies/resources for this prototype.

        This delegates to `self.installer.__install__(...)`.

        Args:
            **properties: Installer-specific properties.

        Raises:
            PrototypeError: If the installer does not provide `__install__`.
            Exception: Any error raised by the underlying installer.
        """
        print(f" \u2699\033[1;30m Installing {self.__class__.__name__} '{self.name}'\033[0m", file=sys.stdout)
        
        assert hasattr(self.installer,'__install__'),\
            PrototypeError(
                code=ErrorCode.PROTOTYPE_INSTALLER_ERR,
                message="Installer didn't have any __install__ method"
            )

        self.installer.__install__(**properties)

    def uninstall(self,
                  **properties):
        """Uninstall dependencies/resources for this prototype.

        This delegates to `self.installer.__uninstall__(...)`.

        Args:
            **properties: Installer-specific properties.

        Raises:
            PrototypeError: If the installer does not provide `__uninstall__`.
            Exception: Any error raised by the underlying installer.
        """
        print(f" \u2699\033[1;30m Uninstalling {self.__class__.__name__} '{self.name}'\033[0m", file=sys.stdout)
        
        assert hasattr(self.installer,'__uninstall__'),\
            PrototypeError(
                code=ErrorCode.PROTOTYPE_UNINSTALLER_ERR,
                message="Installer didn't have any __uninstall__ method"
            )
        
        self.installer.__uninstall__(**properties)


    # ===========================================
    # Load methods
    # ===========================================

    @classmethod
    def load(
            cls, 
            *,
            name:str,
            directory=BLOCK_PATH,
            format='json',
            ntype='prototype',
            installer=INSTALLER.PYTHON,
            **kwargs
        ):
        """Load a prototype from persistent storage.

        Args:
            name (str): Prototype name to load.
            directory (str): Base directory where blocks are stored.
            format (str): Storage format used by the installer (e.g. `json`).
            ntype (str): Expected type marker (defaults to `prototype`).
            installer: Installer backend used to perform the loading. It must
                provide a `__load__` method returning `(content, structure)`.
            **kwargs: Extra keyword arguments merged into the loaded content
                before instantiation.

        Returns:
            Prototype: Loaded prototype instance.

        Raises:
            PrototypeError: If loading fails.
        """

        with safe_operation(
                'loading prototype',
                code=ErrorCode.PROTOTYPE_LOADING_ERR,
                ERROR=PrototypeError ):

            content, structure = installer.__load__(
                name=name,
                directory=directory,
                format=format,
                ntype=ntype,
            )

            content = content or {}
            structure = structure or {}
            content.update(**structure)
            content.update(**kwargs)
            
            obj = cls(**content)
            print(f' \033[1;30m\u21BA {obj.__ntype__} loaded "{name}"\033[0m')
            return obj



    # ===========================================
    # Execute methods
    # ===========================================
        
    def execute(self, **data):
        """Execute the prototype.

        The execution calls the executor produced by `self.executor.execute()`
        and forwards inputs to the prototype `forward` method (if present).
        During execution, `sys.stdout` is redirected to `self.stdout`.

        Args:
            **data: Input payload forwarded to the executor.

        Returns:
            Any: The execution result.

        Raises:
            PrototypeError: When execution fails and `self.ignore_error` is
                `False`.
            Exception: Any exception not handled by the executor pathway.

        Examples:
            >>> prototype = Prototype(...)
            >>> result = prototype.execute(input_data="example")
            >>> print(result)
        """
        error = False
        value = None

        _prev_stdout = sys.stdout
        sys.stdout = self.stdout

        try:
            print(f" \u25B6\033[1;30m Executing {self.__class__.__name__} '{self.name}'...\033[0m", file=sys.stdout)

            forward = getattr(self, 'forward', None)
            logger.info(f"Get forward {self.__class__.__name__} methods")

            try:
                exec  = self.executor.execute(forward=forward)
                value = exec(**data)

            except Exception as e:
                error = True
                logger.critical(f"Execution failed with message :\n{e}")

                err = PrototypeError(
                    code=ErrorCode.PROTOTYPE_EXECUTION,
                    message=f"Execution failed with message :\n{e}",
                    cause=e
                )

                if not self.ignore_error:
                    raise err

            finally:
                txt = f"Execution {self.name} complete"

                if error:
                    print(f' \u274C\033[1;30m {txt} (failed) \033[0m',
                          file=sys.stdout)
                else:
                    print(f' \u2705\033[1;30m {txt} (succes) \033[0m',
                          file=sys.stdout)

                logger.warning(f"Complete {self.__class__.__name__} execution")

        finally:
            sys.stdout = _prev_stdout

        return value




    def forward(self, name=None, **data):
        """Forward inputs to a registered method inside the environment.

        Args:
            name (str | None): Optional registered method name. If `None`, the
                register implementation decides what to call.
            **data: Input payload forwarded to the registered callable.

        Returns:
            Any: Output returned by the registered callable.

        Examples:
            >>> prototype = Prototype()
            >>> result = prototype.forward(name="example_method", data="example_data")
            >>> print(result)
        """

        #with self.environment as env:

        func   = self.get_register_methods(name=name).call
        output = func(**data)


        return output
    









        