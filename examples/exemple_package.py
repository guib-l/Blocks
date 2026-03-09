import os
import subprocess
from configs import *

from packages.package import Packages
from packages.load import PluginLoader, load_plugins


# ---------------------------------------------------------------------------
# 1. Créer et construire un environnement venv + pip
# ---------------------------------------------------------------------------

def example_build():
    """Créer un environnement et installer des dépendances."""

    pkg = Packages(
        directory='./.envs/',
        env_name='pip-env.01',
        env_type='venv',
        mng_type='pip',
        dependencies=['numpy', 'requests'],
        auto_build=False,   # On construit manuellement ci-dessous
    )

    # Construit le venv et initialise le manager pip
    pkg.build()

    # Installe les dépendances listées dans dependencies
    pkg.install_dependencies(pkg.dependencies)

    print(pkg)
    return pkg


# ---------------------------------------------------------------------------
# 2. Recréer un objet Packages existant et l'activer
# ---------------------------------------------------------------------------

def example_activate():
    """Activer un environnement déjà construit."""

    pkg = Packages(
        directory='./.envs/',
        env_name='pip-env.01',
        env_type='venv',
        mng_type='pip',
        auto_build=True,    # build() appelé automatiquement
    )

    # Active l'environnement (modifie sys.path pour inclure le venv)
    pkg.activate()

    # Lister les paquets installés
    deps = pkg.list_dependencies()
    print("Dépendances installées :", deps)

    # Désactiver l'environnement
    pkg.deactivate()


# ---------------------------------------------------------------------------
# 3. Gérer les dépendances dynamiquement
# ---------------------------------------------------------------------------

def example_manage_dependencies():
    """Ajouter, mettre à jour et supprimer des dépendances."""

    pkg = Packages(
        directory='./.envs/',
        env_name='pip-env.01',
        env_type='venv',
        mng_type='pip',
        dependencies=['numpy'],
        auto_build=True,
    )

    # Installer une dépendance supplémentaire
    pkg.install_dependencies(['pandas'])

    # Mettre à jour une dépendance
    pkg.update(['numpy'])

    # Désinstaller une dépendance
    pkg.uninstall_dependencies(['requests'])

    # Lister les dépendances restantes
    print("Dépendances après modifications :", pkg.list_dependencies())


# ---------------------------------------------------------------------------
# 4. Copier un environnement
# ---------------------------------------------------------------------------

def example_copy():
    """Dupliquer un environnement existant sous un nouveau nom."""

    pkg = Packages(
        directory='./.envs/',
        env_name='pip-env.01',
        env_type='venv',
        mng_type='pip',
        dependencies=['numpy'],
        auto_build=True,
    )

    # Crée une copie dans le même répertoire avec un nouveau nom
    pkg_copy = pkg.copy(new_name='pip-env.02')
    print("Copie créée :", pkg_copy)


# ---------------------------------------------------------------------------
# 5. Déplacer un environnement
# ---------------------------------------------------------------------------

def example_move():
    """Déplacer un environnement vers un autre répertoire."""

    pkg = Packages(
        directory='./.envs/',
        env_name='pip-env.01',
        env_type='venv',
        mng_type='pip',
        auto_build=True,
    )

    pkg.move_env(target='./.envs_backup/')
    print("Environnement déplacé vers ./.envs_backup/")
    print("Nouveau chemin :", pkg.directory)


# ---------------------------------------------------------------------------
# 6. Charger un script dans l'environnement isolé (ex: script.py avec numpy)
#    sans avoir numpy dans l'environnement courant
# ---------------------------------------------------------------------------

def example_run_script_in_env():
    """
    Exécuter un script Python dans un environnement virtuel isolé,
    sans que le paquet (numpy ici) soit installé dans l'environnement courant.
    On utilise directement l'interpréteur Python du venv.
    """

    pkg = Packages(
        directory='./.envs/',
        env_name='pip-env.numpy',
        env_type='venv',
        mng_type='pip',
        dependencies=['numpy'],
        auto_build=False,
    )

    pkg.build()

    # Chemin vers l'interpréteur Python du venv (version courante)
    python_bin = pkg._backend_manager.executable
    
    script_path = os.path.join(DIRECTORY, 'script', 'script.py')

    result = subprocess.run(
        [str(python_bin), script_path],
        capture_output=True,
        text=True,
    )

    if result.stderr:
        print("Error on evaluation of file:", result.stderr)


# ---------------------------------------------------------------------------
# 7. Comparer deux environnements (diff)
# ---------------------------------------------------------------------------

def example_compare():
    """Vérifier si deux objets Packages ont les mêmes dépendances."""

    pkg_a = Packages(
        directory='./.envs/',
        env_name='pip-env.01',
        env_type='venv',
        mng_type='pip',
        dependencies=['numpy', 'requests'],
        auto_build=False,
    )

    pkg_b = Packages(
        directory='./.envs/',
        env_name='pip-env.02',
        env_type='venv',
        mng_type='pip',
        dependencies=['numpy', 'requests'],
        auto_build=False,
    )

    print("Environnements identiques (dépendances) :", pkg_a == pkg_b)


# ---------------------------------------------------------------------------
# 8. Diff de deux environnements
# ---------------------------------------------------------------------------

def example_diff():
    """Afficher les différences de paquets installés entre deux environnements."""

    pkg_a = Packages(
        directory='./.envs/',
        env_name='pip-env.01',
        env_type='venv',
        mng_type='pip',
        auto_build=True,
    )

    pkg_b = Packages(
        directory='./.envs/',
        env_name='pip-env.02',
        env_type='venv',
        mng_type='pip',
        auto_build=True,
    )

    diff = pkg_a.diff(pkg_b)

    print("Uniquement dans pip-env.01 :", diff['only_in_self'])
    print("Uniquement dans pip-env.02 :", diff['only_in_other'])
    print("En commun                  :", diff['common'])


# ---------------------------------------------------------------------------
# 9. Merger deux environnements
# ---------------------------------------------------------------------------

def example_merge():
    """
    Fusionner deux environnements en un troisième.
    Les paquets exclusifs à chaque env et les paquets communs sont tous installés
    dans le nouvel environnement. En cas de conflit de version, pkg_b l'emporte.
    """

    pkg_a = Packages(
        directory='./.envs/',
        env_name='pip-env.01',
        env_type='venv',
        mng_type='pip',
        auto_build=True,
    )

    pkg_b = Packages(
        directory='./.envs/',
        env_name='pip-env.02',
        env_type='venv',
        mng_type='pip',
        auto_build=True,
    )

    merged = pkg_a.merge(
        pkg_b,
        new_name='pip-env.merged',
        directory='./.envs/',
        ignore_dependencies=['pip', 'setuptools', 'wheel'],  # méta-paquets à exclure
    )

    print("Environnement fusionné :", merged)
    print("Paquets installés      :", merged.list_dependencies())


# ---------------------------------------------------------------------------
# 10. Context manager — activation / désactivation automatique
# ---------------------------------------------------------------------------

def example_context_manager():
    """
    Utiliser Packages comme context manager.

    L'environnement est activé à l'entrée du bloc `with` et désactivé
    automatiquement à la sortie, même en cas d'exception.
    """

    # --- Cas A : construction manuelle avant le `with` ---
    pkg = Packages(
        directory='./.envs/',
        env_name='pip-env.01',
        env_type='venv',
        mng_type='pip',
        dependencies=['numpy'],
        auto_build=True, )

    with pkg as p:
        # sys.path contient le site-packages du venv ici
        deps = p.list_dependencies()
        print("Dans le contexte — dépendances :", deps)
    # env désactivé ici

    # --- Cas B : construction déléguée au `with` (auto_build=False) ---
    with Packages(
            directory='./.envs/',
            env_name='pip-env.ctx',
            env_type='venv',
            mng_type='pip',
            dependencies=['requests'],
            auto_build=False, ) as p:

        print("Environnement :", p.env_name, "activé")
        p.install_dependencies(['requests'])
        print("Dépendances installées :", p.list_dependencies())
    # env désactivé ici


# ---------------------------------------------------------------------------
# 11. Charger un plugin avec PluginLoader dans un environnement activé
# ---------------------------------------------------------------------------

def example_plugin_loader():
    """
    Charger dynamiquement un script Python (plugin) en utilisant le
    site-packages d'un venv isolé.

    Grâce à `PluginLoader`, le module est mis en cache : un second appel à
    `loader.load()` avec le même nom retourne le module déjà chargé sans
    relire le disque.
    """

    script_path = os.path.join(DIRECTORY, 'script', 'script.py')

    pkg = Packages(
        directory='./.envs/',
        env_name='pip-env.numpy',
        env_type='venv',
        mng_type='pip',
        dependencies=['numpy'],
        auto_build=False,
    )
    pkg.build()

    loader = PluginLoader()

    with pkg as p:

        site_packages = p.site_packages
        
        # Chargement du script depuis le venv
        module = loader.load(
            name='script',
            path=script_path,
            site_packages=site_packages,)

        # Appel d'une fonction du plugin
        result = module.basic_function(n=3, delay=0.0)
        print("Résultat plugin :", result)

    # Second appel : le module est servi depuis le cache (hors contexte)
    cached = loader.get_plugin('script')
    print("Module en cache :", cached)
    print("Plugins chargés :", loader.list_plugins())


# ---------------------------------------------------------------------------
# 12. Context manager + PluginLoader — chargement conditionnel
# ---------------------------------------------------------------------------

def example_context_with_loader():
    """
    Combiner le context manager et PluginLoader pour charger plusieurs
    plugins dans des environnements distincts, puis décharger proprement.

    Chaque `with` garantit que l'environnement est actif pendant le
    chargement, et le désactive ensuite sans effort.
    """

    script_path = os.path.join(DIRECTORY, 'script', 'script.py')
    loader = PluginLoader()

    envs = [
        ('pip-env.A', ['numpy']),
        ('pip-env.B', ['numpy', 'requests']),
    ]

    for env_name, deps in envs:

        with Packages(
            directory='./.envs/',
            env_name=env_name,
            env_type='venv',
            mng_type='pip',
            dependencies=deps,
            auto_build=False, ) as pkg:

            module = loader.load(
                name=f'script_{env_name}',
                path=script_path,
                site_packages=pkg.site_packages,
            )
            result = module.basic_function(n=2, delay=0.0)
            print(f"[{env_name}] résultat : {result}")

    print("Plugins actifs :", loader.list_plugins())

    # Déchargement explicite
    for env_name, _ in envs:
        loader.unload(f'script_{env_name}')

    print("Plugins après déchargement :", loader.list_plugins())


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("=== 1. Build ===")
    example_build()

    print("\n=== 2. Activate / Deactivate ===")
    example_activate()

    print("\n=== 3. Manage dependencies ===")
    example_manage_dependencies()

    print("\n=== 4. Copy ===")
    example_copy()

    print("\n=== 5. Run script in isolated env ===")
    example_run_script_in_env()

    print("\n=== 6. Compare ===")
    example_compare()

    print("\n=== 7. Diff ===")
    example_diff()

    print("\n=== 8. Merge ===")
    example_merge()

    print("\n=== 10. Context manager ===")
    example_context_manager()

    print("\n=== 11. PluginLoader ===")
    example_plugin_loader()

    print("\n=== 12. Context manager + PluginLoader ===")
    example_context_with_loader()







