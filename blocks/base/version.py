import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union



class VersionError(Exception):
    """Exception levée pour les erreurs liées aux versions."""
    pass




class VersionManager:
    """
    Gestionnaire de versions suivant la spécification de Versioning Sémantique.
    Gère les versions au format MAJOR.MINOR.PATCH (par exemple 1.2.3).
    """
    VERSION_PATTERN = re.compile(r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-ZaZ-]+)*))?$')
    
    def __init__(self, current_version="0.0.1"):
        """
        Initialise le gestionnaire de versions.
        
        Args:
            current_version (str): La version actuelle au format X.Y.Z
            
        Raises:
            VersionError: Si le format de version est invalide
        """
        if not self.is_valid_version(current_version):
            raise VersionError(f"Format de version invalide: {current_version}. Utilisez le format X.Y.Z (ex: 1.2.3)")
            
        self.current_version = current_version
        self.version_history = [(current_version, datetime.now(), "Version initiale")]

    def check_version(self, version: str) -> bool:
        """
        Vérifie si la version fournie est compatible avec la version actuelle.
        Une version est considérée compatible si elle a le même numéro majeur
        et si elle est supérieure ou égale à la version actuelle.
        
        Args:
            version (str): La version à vérifier.
            
        Returns:
            bool: True si compatible, False sinon.
            
        Raises:
            VersionError: Si le format de version est invalide
        """
        if not self.is_valid_version(version):
            raise VersionError(f"Format de version invalide: {version}")
            
        current_major, current_minor, current_patch = self.parse_version(self.current_version)
        other_major, other_minor, other_patch = self.parse_version(version)
        
        # Même version majeure et version >= version actuelle
        return (other_major == current_major and 
                (other_minor > current_minor or 
                 (other_minor == current_minor and other_patch >= current_patch)))

    def upgrade_version(self, new_version: str, changelog: str = "") -> None:
        """
        Met à jour vers une nouvelle version.
        
        Args:
            new_version (str): La nouvelle version.
            changelog (str): Description des changements apportés.
            
        Raises:
            VersionError: Si le format de version est invalide ou si la nouvelle version
                         n'est pas supérieure à la version actuelle.
        """
        if not self.is_valid_version(new_version):
            raise VersionError(f"Format de version invalide: {new_version}")
            
        if self.compare_versions(new_version, self.current_version) <= 0:
            raise VersionError(f"La nouvelle version {new_version} doit être supérieure à la version actuelle {self.current_version}")
            
        self.version_history.append((new_version, datetime.now(), changelog))
        self.current_version = new_version

    def get_version(self) -> str:
        """
        Obtient la version actuelle.
        
        Returns:
            str: La version actuelle.
        """
        return self.current_version

    def save_to_file(self, filepath: str) -> None:
        """
        Sauvegarde l'historique des versions dans un fichier.
        
        Args:
            filepath (str): Chemin du fichier où sauvegarder
            
        Raises:
            IOError: Si l'écriture dans le fichier échoue
        """
        import json
        
        # Convertir les dates en chaînes pour la sérialisation JSON
        serializable_history = [
            (version, date.isoformat(), log)
            for version, date, log in self.version_history
        ]
        
        data = {
            "current_version": self.current_version,
            "version_history": serializable_history
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise IOError(f"Erreur lors de la sauvegarde du fichier de versions: {e}")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'VersionManager':
        """
        Charge un gestionnaire de versions depuis un fichier.
        
        Args:
            filepath (str): Chemin du fichier à charger
            
        Returns:
            VersionManager: Une nouvelle instance avec les données chargées
            
        Raises:
            IOError: Si la lecture du fichier échoue
            ValueError: Si le format du fichier est invalide
        """
        import json
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            raise IOError(f"Erreur lors du chargement du fichier de versions: {e}")
        
        if not isinstance(data, dict) or "current_version" not in data or "version_history" not in data:
            raise ValueError("Format de fichier de versions invalide")
        
        manager = cls(data["current_version"])
        
        try:
            manager.version_history = [
                (version, datetime.fromisoformat(date_str), log)
                for version, date_str, log in data["version_history"]
            ]
        except (ValueError, TypeError) as e:
            raise ValueError(f"Format d'historique de versions invalide: {e}")
        
        return manager
    
    def export_to_markdown(self, filepath: str) -> None:
        """
        Exporte l'historique des versions au format Markdown.
        
        Args:
            filepath (str): Chemin du fichier Markdown à créer
            
        Raises:
            IOError: Si l'écriture dans le fichier échoue
        """
        try:
            with open(filepath, 'w') as f:
                f.write("# Historique des versions\n\n")
                
                for version, date, log in reversed(self.version_history):
                    f.write(f"## {version} ({date.strftime('%Y-%m-%d')})\n\n")
                    f.write(f"{log}\n\n")
        except Exception as e:
            raise IOError(f"Erreur lors de l'export Markdown: {e}")
    
    def create_version_file(self, directory: str = ".") -> str:
        """
        Crée un fichier VERSION dans le répertoire spécifié.
        
        Args:
            directory (str): Répertoire où créer le fichier
            
        Returns:
            str: Chemin complet du fichier créé
            
        Raises:
            IOError: Si l'écriture dans le fichier échoue
        """
        filepath = os.path.join(directory, "VERSION")
        
        try:
            with open(filepath, 'w') as f:
                f.write(f"{self.current_version}\n")
            return filepath
        except Exception as e:
            raise IOError(f"Erreur lors de la création du fichier VERSION: {e}")

    def __str__(self):
        return str(self.current_version)

    def __repr__(self):
        return f"VersionManager('{self.current_version}')"
        
    def __eq__(self, other):
        if isinstance(other, VersionManager):
            return self.current_version == other.current_version
        elif isinstance(other, str):
            return self.current_version == other
        return False
        
    def __lt__(self, other):
        if isinstance(other, VersionManager):
            return self.compare_versions(self.current_version, other.current_version) < 0
        elif isinstance(other, str):
            return self.compare_versions(self.current_version, other) < 0
        return NotImplemented
        
    def __gt__(self, other):
        if isinstance(other, VersionManager):
            return self.compare_versions(self.current_version, other.current_version) > 0
        elif isinstance(other, str):
            return self.compare_versions(self.current_version, other) > 0
        return NotImplemented
    
    @staticmethod
    def is_valid_version(version: str) -> bool:
        """
        Vérifie si une chaîne est au format de version valide (X.Y.Z).
        
        Args:
            version (str): La chaîne de version à vérifier
            
        Returns:
            bool: True si la version est valide, False sinon
        """
        return bool(VersionManager.VERSION_PATTERN.match(version))
    
    @staticmethod
    def parse_version(version: str) -> Tuple[int, int, int]:
        """
        Parse une version et retourne ses composants majeur, mineur et patch.
        
        Args:
            version (str): La version à parser (format X.Y.Z)
            
        Returns:
            Tuple[int, int, int]: Tuple (major, minor, patch)
            
        Raises:
            VersionError: Si le format de version est invalide
        """
        if not VersionManager.is_valid_version(version):
            raise VersionError(f"Format de version invalide: {version}")
            
        match = VersionManager.VERSION_PATTERN.match(version)
        return tuple(map(int, match.groups()[:3]))
    
    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare deux versions selon les règles de versioning sémantique.
        
        Args:
            version1 (str): Première version
            version2 (str): Deuxième version
            
        Returns:
            int: -1 si version1 < version2, 0 si égales, 1 si version1 > version2
            
        Raises:
            VersionError: Si l'une des versions est invalide
        """
        if not self.is_valid_version(version1) or not self.is_valid_version(version2):
            raise VersionError("Format de version invalide")
            
        v1_parts = self.parse_version(version1)
        v2_parts = self.parse_version(version2)
        
        for i in range(3):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
                
        return 0

    def increment_major(self, changelog: str = "") -> str:
        """
        Incrémente la version majeure (réinitialise mineur et patch à 0).
        
        Args:
            changelog (str): Description des changements
            
        Returns:
            str: La nouvelle version
        """
        major, _, _ = self.parse_version(self.current_version)
        new_version = f"{major + 1}.0.0"
        self.upgrade_version(new_version, changelog)
        return new_version
    
    def increment_minor(self, changelog: str = "") -> str:
        """
        Incrémente la version mineure (réinitialise patch à 0).
        
        Args:
            changelog (str): Description des changements
            
        Returns:
            str: La nouvelle version
        """
        major, minor, _ = self.parse_version(self.current_version)
        new_version = f"{major}.{minor + 1}.0"
        self.upgrade_version(new_version, changelog)
        return new_version
    
    def increment_patch(self, changelog: str = "") -> str:
        """
        Incrémente la version de patch.
        
        Args:
            changelog (str): Description des changements
            
        Returns:
            str: La nouvelle version
        """
        major, minor, patch = self.parse_version(self.current_version)
        new_version = f"{major}.{minor}.{patch + 1}"
        self.upgrade_version(new_version, changelog)
        return new_version

    def increment_version(self, 
                          major: bool = False, 
                          minor: bool = False, 
                          patch: bool = False, 
                          changelog: str = "") -> str:
        """
        Incrémente la version selon les composants spécifiés.

        Args:
            major (int): Incrément de la version majeure
            minor (int): Incrément de la version mineure
            patch (int): Incrément de la version de patch
            changelog (str): Description des changements

        Returns:
            str: La nouvelle version
        """
        if major == 0 and minor == 0 and patch == 0:
            raise VersionError(
                "At least one of major, minor, or patch must be True or greater than 0.")
        _major, _minor, _patch = self.parse_version(self.current_version)
        new_version = f"{_major + major}.{_minor + minor}.{_patch + patch}"
        self.upgrade_version(new_version, changelog)
        return new_version

    def get_version_history(self) -> List[Tuple[str, datetime, str]]:
        """
        Obtient l'historique complet des versions.
        
        Returns:
            List[Tuple[str, datetime, str]]: Liste des versions, dates et logs
        """
        return self.version_history.copy()
    
    def get_changelog(self, 
                      from_version: Optional[str] = None, 
                      to_version: Optional[str] = None) -> List[str]:
        """
        Obtient les logs de changements entre deux versions.
        
        Args:
            from_version (str, optional): Version de départ. 
                Par défaut, la première version.
            to_version (str, optional): Version d'arrivée. 
                Par défaut, la version actuelle.
            
        Returns:
            List[str]: Liste des logs de changements
            
        Raises:
            VersionError: Si une version spécifiée est invalide ou inexistante
        """
        if from_version and not self.is_valid_version(from_version):
            raise VersionError(f"Format de version invalide: {from_version}")
            
        if to_version and not self.is_valid_version(to_version):
            raise VersionError(f"Format de version invalide: {to_version}")
        
        # Convertir l'historique en dictionnaire pour faciliter la recherche
        history_dict = {version: (date, log) for version, date, log in self.version_history}
        
        if from_version and from_version not in history_dict:
            raise VersionError(f"Version non trouvée dans l'historique: {from_version}")
            
        if to_version and to_version not in history_dict:
            raise VersionError(f"Version non trouvée dans l'historique: {to_version}")
        
        # Déterminer les versions de début et de fin
        start_version = from_version if from_version else self.version_history[0][0]
        end_version = to_version if to_version else self.current_version
        
        # Obtenir les indices dans l'historique
        start_idx = next((i for i, (v, _, _) in enumerate(self.version_history) if v == start_version), 0)
        end_idx = next((i for i, (v, _, _) in enumerate(self.version_history) if v == end_version), len(self.version_history) - 1)
        
        # Si la version de départ est postérieure à la version d'arrivée, inverser
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx
        
        # Extraire les logs
        changelog = []
        for i in range(start_idx + 1, end_idx + 1):  # +1 pour inclure la version end_idx
            version, date, log = self.version_history[i]
            changelog.append(f"{version} ({date.strftime('%Y-%m-%d %H:%M:%S')}): {log}")
            
        return changelog





