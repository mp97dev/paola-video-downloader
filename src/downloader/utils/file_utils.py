"""Utility functions for the video downloader."""

import re
import os
import hashlib
from pathlib import Path
from typing import Optional


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize a filename to be filesystem-safe.
    
    Args:
        filename: The filename to sanitize
        max_length: Maximum length for the filename (default: 200)
        
    Returns:
        A sanitized, filesystem-safe filename
    """
    # Remove or replace invalid characters
    # Invalid chars for most filesystems: < > : " / \ | ? *
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace multiple spaces with a single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rsplit(' ', 1)[0]  # Cut at word boundary
    
    # Ensure we have at least something
    if not sanitized:
        sanitized = 'video'
    
    return sanitized


def get_file_hash(filepath: str) -> str:
    """
    Calculate MD5 hash of a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        MD5 hash of the file
    """
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def check_duplicate(filepath: str, output_dir: str = '.') -> Optional[str]:
    """
    Check if a file with the same name already exists.
    
    Args:
        filepath: The proposed filename
        output_dir: Directory to check for duplicates
        
    Returns:
        Path to existing file if found, None otherwise
    """
    full_path = Path(output_dir) / filepath
    if full_path.exists():
        return str(full_path)
    return None


def ensure_extension(filename: str, extension: str) -> str:
    """
    Ensure filename has the correct extension.
    
    Args:
        filename: The filename
        extension: The desired extension (with or without leading dot)
        
    Returns:
        Filename with correct extension
    """
    if not extension.startswith('.'):
        extension = '.' + extension
    
    if not filename.endswith(extension):
        # Remove any existing extension
        base = os.path.splitext(filename)[0]
        filename = base + extension
    
    return filename
