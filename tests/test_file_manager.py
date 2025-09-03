#!/usr/bin/env python3
"""
Exemple d'utilisation de la classe FileManager améliorée.
"""
import os
import sys
import tempfile
from pathlib import Path

from configs import *
from blocks.base.organizer import FileManager, FileError

if __name__ == "__main__":
    
    """Fonction principale d'exemple."""
    print("=== Démonstration du FileManager amélioré ===\n")
    
    # Créer un gestionnaire de fichiers avec journalisation activée
    file_manager = FileManager(base_directory="~/",
                               log_enabled=True)
    print(f"Répertoire de base: {file_manager.base_directory}\n")
    
    # Créer un répertoire temporaire pour nos tests
    temp_dir = tempfile.mkdtemp()
    print(f"Répertoire temporaire créé: {temp_dir}\n")
    
    try:
        # 1. Créer un répertoire
        test_dir = os.path.join(temp_dir, "test_files")
        name_dirr = file_manager.create_directory(test_dir)
        print(f"Répertoire créé: {name_dirr}")
        
        # 2. Écrire dans un fichier texte
        text_file = os.path.join(test_dir, "example.txt")
        file_manager.write_file(text_file, "Ceci est un exemple de texte.\nLigne 2.\nLigne 3.")
        print(f"Fichier texte créé: {text_file}")
        
        # 3. Lire le contenu du fichier
        content = file_manager.read_file(text_file)
        print(f"\nContenu du fichier texte:\n{content}")
        
        # 4. Créer un sous-répertoire
        sub_dir = os.path.join(test_dir, "subdir")
        file_manager.create_directory(sub_dir)
        
        # 5. Créer et manipuler un fichier JSON
        data = {
            "name": "Example Project",
            "version": "1.0.0",
            "tags": ["example", "demo", "file-manager"],
            "settings": {
                "debug": True,
                "max_size": 1024,
                "paths": ["/tmp", "/var/log"]
            }
        }
        
        json_file = os.path.join(test_dir, "config.json")
        file_manager.write_json(json_file, data)
        print(f"\nFichier JSON créé: {json_file}")
        
        # 6. Lire le JSON
        json_data = file_manager.read_json(json_file)
        print(f"\nContenu du fichier JSON:\n{json_data}")
        
        # 7. Créer un fichier CSV
        csv_data = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
            {"id": 3, "name": "Charlie", "age": 35}
        ]
        
        csv_file = os.path.join(test_dir, "users.csv")
        file_manager.write_csv(csv_file, csv_data)
        print(f"\nFichier CSV créé: {csv_file}")
        
        # 8. Lire le CSV
        csv_content = file_manager.read_csv(csv_file)
        print(f"\nContenu du fichier CSV:")
        for row in csv_content:
            print(f"  {row}")
        
        # 9. Créer une archive ZIP
        zip_file = os.path.join(temp_dir, "archive.zip")
        file_manager.create_zip(test_dir, zip_file)
        print(f"\nArchive ZIP créée: {zip_file}")
        
        # 10. Extraire l'archive ZIP
        extract_dir = os.path.join(temp_dir, "extracted")
        file_manager.extract_zip(zip_file, extract_dir)
        print(f"\nArchive extraite dans: {extract_dir}")
        
        # 11. Lister les fichiers
        files = file_manager.list_files(extract_dir, recursive=True)
        print(f"\nFichiers extraits:")
        for file in files:
            print(f"  {file}")
        
        # 12. Obtenir des informations sur un fichier
        file_size = file_manager.get_file_size(json_file)
        file_hash = file_manager.calculate_file_hash(json_file, 'sha256')
        print(f"\nInformations sur {json_file}:")
        print(f"  Taille: {file_size} octets")
        print(f"  Hash SHA-256: {file_hash}")
        
        # 13. Déplacer un fichier
        new_location = os.path.join(temp_dir, "moved_file.txt")
        file_manager.move_files(text_file, new_location)
        print(f"\nFichier déplacé: {text_file} -> {new_location}")
        
        # 14. Vérifier si le fichier existe à sa nouvelle location
        exists = file_manager.file_exists(new_location)
        print(f"Le fichier existe à sa nouvelle location: {exists}")
        
        # 15. Supprimer un répertoire
        #file_manager.delete_directory(sub_dir)
        print(f"\nRépertoire supprimé: {sub_dir}")
        
    except FileError as e:
        print(f"\nErreur: {e}")
    finally:
        # Nettoyer le répertoire temporaire
        print(f"\nNettoyage du répertoire temporaire: {temp_dir}")
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
    
    print("\n=== Fin de la démonstration ===")

