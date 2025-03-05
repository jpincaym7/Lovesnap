# core/utils.py
import os
import uuid

def generate_uuid():
    """Genera un UUID único"""
    return uuid.uuid4()

def generate_access_code():
    """Genera un código de acceso único de 8 caracteres"""
    return str(uuid.uuid4())[:8]

def safe_delete_file(file_path):
    """Elimina un archivo físico de manera segura"""
    if file_path and os.path.isfile(file_path):
        os.remove(file_path)