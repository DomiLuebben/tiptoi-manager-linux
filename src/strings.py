"""
Localization module for tiptoi Manager Linux.
Loads extracted string table from LocalizationFile.txt.
"""

import os
from typing import Dict, Optional

class Strings:
    _instance = None

    def __init__(self, filepath: Optional[str] = None):
        self.strings: Dict[str, Dict[str, str]] = {}
        if not filepath:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, "LocalizationFile.txt")
        self.load(filepath)

    def load(self, filepath: str):
        if not os.path.exists(filepath):
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                return
            header = [col.strip() for col in lines[0].split("\t")]
            # Format: Key \t de \t fr \t it \t nl \t ru
            lang_indices = {lang: idx for idx, lang in enumerate(header) if idx > 0}
            for line in lines[1:]:
                parts = line.strip("\r\n").split("\t")
                if not parts or not parts[0]:
                    continue
                key = parts[0]
                self.strings[key] = {}
                for lang, idx in lang_indices.items():
                    if idx < len(parts):
                        self.strings[key][lang] = parts[idx]
        except Exception as e:
            print(f"Error loading LocalizationFile: {e}")

    def get(self, key: str, lang: str = "de", default: Optional[str] = None) -> str:
        if key in self.strings:
            translations = self.strings[key]
            if lang in translations and translations[lang]:
                return translations[lang]
            if "de" in translations and translations["de"]:
                return translations["de"]
        return default if default is not None else key

    @classmethod
    def instance(cls) -> "Strings":
        if cls._instance is None:
            cls._instance = Strings()
        return cls._instance


def tr(key: str, default: Optional[str] = None, lang: str = "de", **kwargs) -> str:
    val = Strings.instance().get(key, lang=lang, default=default)
    if kwargs:
        try:
            val = val.format(**kwargs)
        except Exception:
            pass
    return val
