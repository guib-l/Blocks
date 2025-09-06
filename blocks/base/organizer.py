import os
import sys
import shutil
import tempfile
import zipfile
import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable, Iterator, BinaryIO, TextIO



class FileError(Exception):
    """Exception levée pour les erreurs liées aux opérations sur les fichiers."""
    pass



class FileManager:
    """
    Gestionnaire de fichiers et de répertoires.
    Fournit des méthodes pour manipuler des fichiers et des répertoires
    avec gestion des erreurs et options de configuration.
    """

    def __init__(self, 
                 base_directory: Optional[str] = None, 
                 auto_create: bool = True, 
                 log_enabled: bool = False, 
                 log_level: int = logging.INFO):
        """
        Initialise le gestionnaire de fichiers.
        
        Args:
            base_directory (str, optional): Répertoire de base pour les opérations relatives.
                                           Si None, le répertoire de travail actuel est utilisé.
            auto_create (bool): Si True, crée automatiquement les répertoires manquants.
            log_enabled (bool): Si True, active la journalisation des opérations.
            log_level (int): Niveau de journalisation (logging.DEBUG, logging.INFO, etc.)
        """
        self.base_directory = base_directory or os.getcwd()
        self.auto_create = auto_create
        self.log_enabled = log_enabled

        origin = os.path.join(self.base_directory,'../')
        self.origin = os.path.abspath(os.path.expanduser(origin))
        
        # Configuration de la journalisation
        self.logger = logging.getLogger("FileManager")
        self.logger.setLevel(log_level)
        
        if log_enabled and not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Vérifier et créer le répertoire de base si nécessaire
        if auto_create and not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)
            self._log(f"Répertoire de base créé: {self.base_directory}", logging.INFO)

    def move_files(self, 
                   src: Union[str, Path], 
                   dest: Union[str, Path], 
                   overwrite: bool = False) -> str:
        """
        Déplace un fichier ou un répertoire de src vers dest.
        
        Args:
            src (str or Path): Chemin source
            dest (str or Path): Chemin de destination
            overwrite (bool): Si True, écrase la destination si elle existe
            
        Returns:
            str: Chemin de destination complet
            
        Raises:
            FileError: Si le fichier/répertoire source n'existe pas ou si la destination
                      existe déjà et overwrite=False
        """
        src_path = self._resolve_path(src)
        dest_path = self._resolve_path(dest)
        
        if not os.path.exists(src_path):
            raise FileError(f"Le chemin source n'existe pas: {src_path}")
            
        if os.path.exists(dest_path) and not overwrite:
            raise FileError(f"Le chemin de destination existe déjà: {dest_path}")
            
        try:
            # Créer le répertoire parent de destination si nécessaire
            dest_dir = os.path.dirname(dest_path)
            if self.auto_create and not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                
            shutil.move(src_path, dest_path)
            self._log(f"Déplacé de {src_path} vers {dest_path}", logging.INFO)
            return dest_path
        except Exception as e:
            error_msg = f"Erreur lors du déplacement de {src_path} vers {dest_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e

    def copy_files(self, src: Union[str, Path], dest: Union[str, Path], 
                 ignore: Optional[Callable] = None, overwrite: bool = False) -> str:
        """
        Copie un fichier ou un répertoire de src vers dest.
        
        Args:
            src (str or Path): Chemin source
            dest (str or Path): Chemin de destination
            ignore (callable, optional): Fonction de filtrage pour ignorer certains fichiers
            overwrite (bool): Si True, écrase la destination si elle existe
            
        Returns:
            str: Chemin de destination complet
            
        Raises:
            FileError: Si le fichier/répertoire source n'existe pas ou si une erreur survient
        """
        src_path = self._resolve_path(src)
        dest_path = self._resolve_path(dest)
        
        if not os.path.exists(src_path):
            raise FileError(f"Le chemin source n'existe pas: {src_path}")
            
        try:
            # Gestion des répertoires parents de destination
            dest_dir = os.path.dirname(dest_path) if os.path.isfile(src_path) else dest_path
            if self.auto_create and not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                
            # Si la destination existe et qu'on ne veut pas écraser
            if os.path.exists(dest_path) and not overwrite:
                raise FileError(f"Le chemin de destination existe déjà: {dest_path}")
                
            # Copie selon le type de la source
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dest_path)
                self._log(f"Fichier copié de {src_path} vers {dest_path}", logging.INFO)
            elif os.path.isdir(src_path):
                # Supprimer la destination si elle existe et qu'on veut écraser
                if os.path.exists(dest_path) and overwrite:
                    shutil.rmtree(dest_path)
                    
                shutil.copytree(src_path, dest_path, ignore=ignore)
                self._log(f"Répertoire copié de {src_path} vers {dest_path}", logging.INFO)
                
            return dest_path
        except Exception as e:
            error_msg = f"Erreur lors de la copie de {src_path} vers {dest_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e

    def create_directory(self, path: Union[str, Path], mode: int = 0o755, 
                         exist_ok: bool = True) -> str:
        """
        Crée un répertoire s'il n'existe pas.
        
        Args:
            path (str or Path): Chemin du répertoire à créer
            mode (int): Permissions du répertoire (mode octal)
            exist_ok (bool): Si True, ne lève pas d'erreur si le répertoire existe déjà
            
        Returns:
            str: Chemin du répertoire créé
            
        Raises:
            FileError: Si le répertoire ne peut pas être créé
        """
        full_path = self._resolve_path(path)

        try:
            os.makedirs(full_path, mode=mode, exist_ok=exist_ok)
            self._log(f"Répertoire créé: {full_path}", logging.INFO)
            return full_path
        except Exception as e:
            error_msg = f"Erreur lors de la création du répertoire {full_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e

    def delete_directory(self, path: Union[str, Path], ignore_errors: bool = False) -> None:
        """
        Supprime un répertoire s'il existe.
        
        Args:
            path (str or Path): Chemin du répertoire à supprimer
            ignore_errors (bool): Si True, ignore les erreurs lors de la suppression
            
        Raises:
            FileError: Si le répertoire ne peut pas être supprimé et ignore_errors=False
        """
        full_path = self._resolve_path(path)
        
        if not os.path.exists(full_path):
            self._log(f"Répertoire non trouvé pour suppression: {full_path}", logging.WARNING)
            return
            
        if not os.path.isdir(full_path):
            raise FileError(f"Le chemin n'est pas un répertoire: {full_path}")
            
        try:
            shutil.rmtree(full_path, ignore_errors=ignore_errors)
            self._log(f"Répertoire supprimé: {full_path}", logging.INFO)
        except Exception as e:
            error_msg = f"Erreur lors de la suppression du répertoire {full_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e

    def list_files(self, path: Union[str, Path], pattern: str = "*", 
                  recursive: bool = False, only_files: bool = False, 
                  only_dirs: bool = False) -> List[str]:
        """
        Liste tous les fichiers dans un répertoire.
        
        Args:
            path (str or Path): Chemin du répertoire à lister
            pattern (str): Motif de filtrage (ex: "*.txt")
            recursive (bool): Si True, liste récursivement les sous-répertoires
            only_files (bool): Si True, ne liste que les fichiers
            only_dirs (bool): Si True, ne liste que les répertoires
            
        Returns:
            list: Une liste de noms de fichiers/répertoires
            
        Raises:
            FileError: Si le répertoire n'existe pas ou n'est pas un répertoire
        """
        full_path = self._resolve_path(path)
        
        if not os.path.exists(full_path):
            raise FileError(f"Le répertoire n'existe pas: {full_path}")
            
        if not os.path.isdir(full_path):
            raise FileError(f"Le chemin n'est pas un répertoire: {full_path}")
            
        result = []
        
        try:
            if recursive:
                for root, dirs, files in os.walk(full_path):
                    relative_root = os.path.relpath(root, full_path)
                    if relative_root == ".":
                        relative_root = ""
                        
                    if not only_files:
                        for d in dirs:
                            if Path(d).match(pattern):
                                result.append(os.path.join(relative_root, d) if relative_root else d)
                    
                    if not only_dirs:
                        for f in files:
                            if Path(f).match(pattern):
                                result.append(os.path.join(relative_root, f) if relative_root else f)
            else:
                entries = os.listdir(full_path)
                for entry in entries:
                    entry_path = os.path.join(full_path, entry)
                    
                    if (not only_files and not only_dirs) or \
                       (only_files and os.path.isfile(entry_path)) or \
                       (only_dirs and os.path.isdir(entry_path)):
                        if Path(entry).match(pattern):
                            result.append(entry)
                            
            self._log(f"Listage de {full_path}: {len(result)} entrées trouvées", logging.DEBUG)
            return result
        except Exception as e:
            error_msg = f"Erreur lors du listage du répertoire {full_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e

    def file_exists(self, path: Union[str, Path]) -> bool:
        """
        Vérifie si un fichier existe.
        
        Args:
            path (str or Path): Chemin du fichier à vérifier
            
        Returns:
            bool: True si le fichier existe, False sinon
        """
        full_path = self._resolve_path(path)
        exists = os.path.exists(full_path) and os.path.isfile(full_path)
        self._log(f"Vérification d'existence du fichier {full_path}: {exists}", logging.DEBUG)
        return exists
        
    def directory_exists(self, path: Union[str, Path]) -> bool:
        """
        Vérifie si un répertoire existe.
        
        Args:
            path (str or Path): Chemin du répertoire à vérifier
            
        Returns:
            bool: True si le répertoire existe, False sinon
        """
        full_path = self._resolve_path(path)
        exists = os.path.exists(full_path) and os.path.isdir(full_path)
        self._log(f"Vérification d'existence du répertoire {full_path}: {exists}", logging.DEBUG)
        return exists
    
    def read_file(self, path: Union[str, Path], encoding: str = 'utf-8', 
                 binary: bool = False) -> Union[str, bytes, None]:
        """
        Lit le contenu d'un fichier.
        
        Args:
            path (str or Path): Chemin du fichier à lire
            encoding (str): Encodage à utiliser pour les fichiers texte
            binary (bool): Si True, lit le fichier en mode binaire
            
        Returns:
            str, bytes or None: Le contenu du fichier, ou None si le fichier n'existe pas
            
        Raises:
            FileError: Si une erreur survient lors de la lecture
        """
        full_path = self._resolve_path(path)
        
        if not self.file_exists(full_path):
            self._log(f"Fichier non trouvé pour lecture: {full_path}", logging.WARNING)
            return None
            
        try:
            mode = 'rb' if binary else 'r'
            with open(full_path, mode, encoding=None if binary else encoding) as file:
                content = file.read()
                self._log(f"Fichier lu: {full_path}", logging.DEBUG)
                return content
        except Exception as e:
            error_msg = f"Erreur lors de la lecture du fichier {full_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e

    def write_file(self, 
                   path: Union[str, Path], 
                   content: Union[str, bytes], 
                   encoding: str = 'utf-8', 
                   binary: bool = False, 
                   append: bool = False,
                   auto_create: bool = None) -> str:
        """
        Écrit du contenu dans un fichier.
        
        Args:
            path (str or Path): Chemin du fichier à écrire
            content (str or bytes): Contenu à écrire
            encoding (str): Encodage à utiliser pour les fichiers texte
            binary (bool): Si True, écrit en mode binaire
            append (bool): Si True, ajoute au fichier au lieu de l'écraser
            
        Returns:
            str: Chemin complet du fichier écrit
            
        Raises:
            FileError: Si une erreur survient lors de l'écriture
        """
        full_path = self._resolve_path(path)

        auto_create = auto_create if auto_create is not None else self.auto_create
        
        # Créer le répertoire parent si nécessaire
        parent_dir = os.path.dirname(full_path)
        if auto_create and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
            
        try:
            mode = 'ab' if binary and append else 'wb' if binary else 'a' if append else 'w'
            with open(full_path, mode, encoding=None if binary else encoding) as file:
                file.write(content)
                
            action = "ajouté à" if append else "écrit dans"
            self._log(f"Contenu {action} {full_path}", logging.INFO)
            return full_path
        except Exception as e:
            error_msg = f"Erreur lors de l'écriture dans le fichier {full_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e

    # -----------------------------------------------------
    # Méthodes pour les formats de fichiers spécifiques
    # -----------------------------------------------------
    
    def read_json(self, path: Union[str, Path], encoding: str = 'utf-8') -> Optional[Dict]:
        """
        Lit un fichier JSON et le convertit en dictionnaire.
        
        Args:
            path (str or Path): Chemin du fichier JSON
            encoding (str): Encodage du fichier
            
        Returns:
            dict or None: Le dictionnaire JSON, ou None si le fichier n'existe pas
            
        Raises:
            FileError: Si le fichier n'est pas un JSON valide
        """
        content = self.read_file(path, encoding=encoding)
        if content is None:
            return None
            
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            error_msg = f"Erreur de décodage JSON pour {path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e
            
    def write_json(self, path: Union[str, Path], data: Dict, 
                   encoding: str = 'utf-8', indent: int = 2) -> str:
        """
        Écrit un dictionnaire dans un fichier JSON.
        
        Args:
            path (str or Path): Chemin du fichier JSON
            data (dict): Données à écrire
            encoding (str): Encodage du fichier
            indent (int): Nombre d'espaces pour l'indentation
            
        Returns:
            str: Chemin complet du fichier écrit
            
        Raises:
            FileError: Si les données ne peuvent pas être sérialisées en JSON
        """
        try:
            json_content = json.dumps(data, indent=indent)
            return self.write_file(path, json_content, encoding=encoding)
        except (TypeError, ValueError) as e:
            error_msg = f"Erreur lors de la sérialisation JSON pour {path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e
            
    def read_csv(self, path: Union[str, Path], delimiter: str = ',', 
                 has_header: bool = True, encoding: str = 'utf-8') -> List[Dict]:
        """
        Lit un fichier CSV et le convertit en liste de dictionnaires.
        
        Args:
            path (str or Path): Chemin du fichier CSV
            delimiter (str): Délimiteur de champs
            has_header (bool): Si True, utilise la première ligne comme en-têtes
            encoding (str): Encodage du fichier
            
        Returns:
            list: Liste de dictionnaires représentant les lignes du CSV,
                 ou None si le fichier n'existe pas
            
        Raises:
            FileError: Si le fichier CSV ne peut pas être lu
        """
        full_path = self._resolve_path(path)
        
        if not self.file_exists(full_path):
            self._log(f"Fichier CSV non trouvé: {full_path}", logging.WARNING)
            return None
            
        try:
            result = []
            with open(full_path, 'r', encoding=encoding, newline='') as csvfile:
                if has_header:
                    reader = csv.DictReader(csvfile, delimiter=delimiter)
                    result = list(reader)
                else:
                    reader = csv.reader(csvfile, delimiter=delimiter)
                    rows = list(reader)
                    # Créer des dictionnaires avec des clés numériques
                    result = [dict(enumerate(row)) for row in rows]
                    
            self._log(f"Fichier CSV lu: {full_path}, {len(result)} lignes", logging.DEBUG)
            return result
        except Exception as e:
            error_msg = f"Erreur lors de la lecture du fichier CSV {full_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e
            
    def write_csv(self, path: Union[str, Path], data: List[Dict], 
                  fieldnames: Optional[List[str]] = None, delimiter: str = ',', 
                  encoding: str = 'utf-8') -> str:
        """
        Écrit une liste de dictionnaires dans un fichier CSV.
        
        Args:
            path (str or Path): Chemin du fichier CSV
            data (list): Liste de dictionnaires à écrire
            fieldnames (list, optional): Liste des noms de champs à inclure et leur ordre
            delimiter (str): Délimiteur de champs
            encoding (str): Encodage du fichier
            
        Returns:
            str: Chemin complet du fichier écrit
            
        Raises:
            FileError: Si les données ne peuvent pas être écrites en CSV
        """
        full_path = self._resolve_path(path)
        
        # Créer le répertoire parent si nécessaire
        parent_dir = os.path.dirname(full_path)
        if self.auto_create and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
            
        try:
            # Déterminer les noms de champs si non spécifiés
            if not fieldnames and data:
                fieldnames = list(data[0].keys())
                
            with open(full_path, 'w', encoding=encoding, newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
                
            self._log(f"Fichier CSV écrit: {full_path}, {len(data)} lignes", logging.INFO)
            return full_path
        except Exception as e:
            error_msg = f"Erreur lors de l'écriture du fichier CSV {full_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e

    # -----------------------------------------------------
    # Méthodes pour les archives et fichiers temporaires
    # -----------------------------------------------------
    
    def create_zip(self, 
                   source: Union[str, Path], 
                   destination: Union[str, Path], 
                   compression: int = zipfile.ZIP_DEFLATED, 
                   include_base_dir: bool = True) -> str:
        """
        Crée une archive ZIP à partir d'un fichier ou d'un répertoire.
        
        Args:
            source (str or Path): Chemin du fichier ou répertoire à archiver
            destination (str or Path): Chemin de l'archive ZIP de destination
            compression (int): Niveau de compression
            include_base_dir (bool): Si True, inclut le répertoire de base dans l'archive
            
        Returns:
            str: Chemin complet de l'archive créée
            
        Raises:
            FileError: Si la source n'existe pas ou si l'archive ne peut pas être créée
        """
        src_path = self._resolve_path(source)
        dest_path = self._resolve_path(destination)

        if not os.path.exists(src_path):
            raise FileError(f"Le chemin source n'existe pas: {src_path}")
        
        # Créer le répertoire parent de destination si nécessaire
        dest_dir = os.path.dirname(dest_path)
        if self.auto_create and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        try:
            with zipfile.ZipFile(dest_path, 'w', compression) as zipf:
                if os.path.isfile(src_path):
                    # Fichier unique
                    zipf.write(src_path, os.path.basename(src_path))
                    self._log(f"Fichier ajouté à l'archive: {src_path}", logging.DEBUG)
                else:
                    # Répertoire
                    base_name = os.path.basename(src_path) if include_base_dir else ''
                    for root, _, files in os.walk(src_path):
                        for file in files:
                            if file.endswith('.zip'):continue
                            file_path = os.path.join(root, file)
                            arcname = os.path.join(base_name, os.path.relpath(file_path, src_path))
                            zipf.write(file_path, arcname)
                            
            self._log(f"Archive ZIP créée: {dest_path}", logging.INFO)
            return dest_path
        except Exception as e:
            error_msg = f"Erreur lors de la création de l'archive ZIP {dest_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e
    
    def extract_zip(self, 
                    source: Union[str, Path], 
                    destination: Union[str, Path], 
                    password: Optional[bytes] = None) -> str:
        """
        Extrait une archive ZIP.
        
        Args:
            source (str or Path): Chemin de l'archive ZIP
            destination (str or Path): Répertoire de destination
            password (bytes, optional): Mot de passe pour les archives protégées
            
        Returns:
            str: Chemin complet du répertoire d'extraction
            
        Raises:
            FileError: Si l'archive n'existe pas ou ne peut pas être extraite
        """
        src_path = self._resolve_path(
                    os.path.join(self.origin, source))
        dest_path = self._resolve_path(
                    os.path.join(self.origin, destination))

        if not self.file_exists(src_path):
            raise FileError(f"L'archive ZIP n'existe pas: {src_path}")
            
        # Créer le répertoire de destination si nécessaire
        if self.auto_create and not os.path.exists(dest_path):
            os.makedirs(dest_path)
            
        try:
            with zipfile.ZipFile(src_path, 'r') as zipf:
                zipf.extractall(path=dest_path, pwd=password)
                
            self._log(f"Archive ZIP extraite: {src_path} -> {dest_path}", logging.INFO)           
            return dest_path
        except Exception as e:
            error_msg = f"Erreur lors de l'extraction de l'archive ZIP {src_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e
    
    def create_temp_directory(self, prefix: str = 'tmp', suffix: str = '') -> str:
        """
        Crée un répertoire temporaire.
        
        Args:
            prefix (str): Préfixe du nom du répertoire
            suffix (str): Suffixe du nom du répertoire
            
        Returns:
            str: Chemin complet du répertoire temporaire
            
        Raises:
            FileError: Si le répertoire temporaire ne peut pas être créé
        """
        try:
            temp_dir = tempfile.mkdtemp(suffix=suffix, prefix=prefix)
            self._log(f"Répertoire temporaire créé: {temp_dir}", logging.DEBUG)
            return temp_dir
        except Exception as e:
            error_msg = f"Erreur lors de la création du répertoire temporaire: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e
    
    def create_temp_file(self, content: Optional[Union[str, bytes]] = None, 
                        prefix: str = 'tmp', suffix: str = '', 
                        binary: bool = False) -> str:
        """
        Crée un fichier temporaire avec un contenu optionnel.
        
        Args:
            content (str or bytes, optional): Contenu à écrire dans le fichier
            prefix (str): Préfixe du nom du fichier
            suffix (str): Suffixe du nom du fichier
            binary (bool): Si True, écrit en mode binaire
            
        Returns:
            str: Chemin complet du fichier temporaire
            
        Raises:
            FileError: Si le fichier temporaire ne peut pas être créé
        """
        try:
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            os.close(fd)  # Fermer le descripteur de fichier
            
            # Écrire le contenu si fourni
            if content is not None:
                mode = 'wb' if binary else 'w'
                with open(temp_path, mode) as f:
                    f.write(content)
                    
            self._log(f"Fichier temporaire créé: {temp_path}", logging.DEBUG)
            return temp_path
        except Exception as e:
            error_msg = f"Erreur lors de la création du fichier temporaire: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e

    # -----------------------------------------------------
    # Méthodes utilitaires supplémentaires
    # -----------------------------------------------------
    
    def get_file_size(self, path: Union[str, Path]) -> Optional[int]:
        """
        Obtient la taille d'un fichier en octets.
        
        Args:
            path (str or Path): Chemin du fichier
            
        Returns:
            int or None: Taille du fichier en octets, ou None si le fichier n'existe pas
        """
        full_path = self._resolve_path(path)
        
        if not self.file_exists(full_path):
            self._log(f"Fichier non trouvé pour obtention de taille: {full_path}", logging.WARNING)
            return None
            
        try:
            size = os.path.getsize(full_path)
            self._log(f"Taille du fichier {full_path}: {size} octets", logging.DEBUG)
            return size
        except Exception as e:
            error_msg = f"Erreur lors de l'obtention de la taille du fichier {full_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e
            
    def get_file_modification_time(self, path: Union[str, Path]) -> Optional[float]:
        """
        Obtient la date de dernière modification d'un fichier.
        
        Args:
            path (str or Path): Chemin du fichier
            
        Returns:
            float or None: Timestamp de dernière modification, ou None si le fichier n'existe pas
        """
        full_path = self._resolve_path(path)
        
        if not os.path.exists(full_path):
            self._log(f"Fichier non trouvé pour obtention de date: {full_path}", logging.WARNING)
            return None
            
        try:
            mtime = os.path.getmtime(full_path)
            self._log(f"Date de modification du fichier {full_path}: {mtime}", logging.DEBUG)
            return mtime
        except Exception as e:
            error_msg = f"Erreur lors de l'obtention de la date du fichier {full_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e
            
    def find_files(self, directory: Union[str, Path], pattern: str = "*", 
                  recursive: bool = True) -> List[str]:
        """
        Recherche des fichiers correspondant à un motif dans un répertoire.
        
        Args:
            directory (str or Path): Répertoire de recherche
            pattern (str): Motif de recherche (ex: "*.txt")
            recursive (bool): Si True, recherche récursivement dans les sous-répertoires
            
        Returns:
            list: Liste des chemins de fichiers correspondants
            
        Raises:
            FileError: Si le répertoire n'existe pas
        """
        return self.list_files(directory, pattern=pattern, 
                             recursive=recursive, only_files=True)
                             
    def calculate_file_hash(self, path: Union[str, Path], 
                           hash_type: str = 'sha256') -> Optional[str]:
        """
        Calcule le hash d'un fichier.
        
        Args:
            path (str or Path): Chemin du fichier
            hash_type (str): Type de hash ('md5', 'sha1', 'sha256', etc.)
            
        Returns:
            str or None: Hash du fichier, ou None si le fichier n'existe pas
            
        Raises:
            FileError: Si le type de hash est invalide ou si une erreur survient
        """
        import hashlib
        
        full_path = self._resolve_path(path)
        
        if not self.file_exists(full_path):
            self._log(f"Fichier non trouvé pour calcul de hash: {full_path}", logging.WARNING)
            return None
            
        try:
            hash_obj = getattr(hashlib, hash_type)()
        except AttributeError:
            raise FileError(f"Type de hash invalide: {hash_type}")
            
        try:
            with open(full_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
                    
            file_hash = hash_obj.hexdigest()
            self._log(f"Hash {hash_type} du fichier {full_path}: {file_hash}", logging.DEBUG)
            return file_hash
        except Exception as e:
            error_msg = f"Erreur lors du calcul du hash du fichier {full_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e
            
    def rename(self, src: Union[str, Path], dest: Union[str, Path]) -> str:
        """
        Renomme un fichier ou un répertoire.
        
        Args:
            src (str or Path): Chemin source
            dest (str or Path): Chemin de destination
            
        Returns:
            str: Chemin de destination complet
            
        Raises:
            FileError: Si la source n'existe pas ou si la destination existe déjà
        """
        src_path = self._resolve_path(src)
        dest_path = self._resolve_path(dest)
        
        if not os.path.exists(src_path):
            raise FileError(f"Le chemin source n'existe pas: {src_path}")
            
        if os.path.exists(dest_path):
            raise FileError(f"Le chemin de destination existe déjà: {dest_path}")
            
        try:
            # Créer le répertoire parent de destination si nécessaire
            dest_dir = os.path.dirname(dest_path)
            if self.auto_create and not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                
            os.rename(src_path, dest_path)
            self._log(f"Renommé de {src_path} vers {dest_path}", logging.INFO)
            return dest_path
        except Exception as e:
            error_msg = f"Erreur lors du renommage de {src_path} vers {dest_path}: {str(e)}"
            self._log(error_msg, logging.ERROR)
            raise FileError(error_msg) from e

    def _log(self, message: str, level: int = logging.INFO) -> None:
        """
        Journalise un message si la journalisation est activée.
        
        Args:
            message (str): Message à journaliser
            level (int): Niveau de journalisation
        """
        if self.log_enabled:
            self.logger.log(level, message)
            
    def _resolve_path(self, path: Union[str, Path]) -> str:
        """
        Résout un chemin relatif ou absolu.
        Si le chemin est relatif, il est résolu par rapport au répertoire de base.
        
        Args:
            path (str or Path): Chemin à résoudre
            
        Returns:
            str: Chemin absolu résolu
        """
        path_str = str(path)
        if os.path.isabs(path_str):
            return path_str
        return os.path.join(self.base_directory, path_str)






