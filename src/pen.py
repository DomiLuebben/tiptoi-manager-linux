"""
tiptoi® Pen manager and Linux USB detection.
Handles mount scanning, .tiptoi.log parsing/writing, and .gme file analysis.
"""

import os
import shutil
import struct
import subprocess
from typing import Optional, List, Dict, Any

class InstalledProduct:
    def __init__(self, filename: str, path: str, gme_id: int, version: str, size_bytes: int):
        self.filename = filename
        self.path = path
        self.gme_id = gme_id
        self.version = version
        self.size_bytes = size_bytes
        self.product_name = ""

    @property
    def file_size(self) -> int:
        return self.size_bytes

    def __repr__(self):
        return f"<InstalledProduct id={self.gme_id} version={self.version} name={self.filename}>"


class PenInfo:
    def __init__(
        self,
        mount_path: str,
        serial_number: str = "Unknown",
        firmware_descriptor: str = "Unknown",
        language: str = "GERMAN",
        mcu: str = "",
        generation: str = "REV4",
    ):
        self.mount_path = mount_path
        self.serial_number = serial_number
        self.firmware_descriptor = firmware_descriptor
        self.language = language
        self.mcu = mcu
        self.generation = generation
        self.installed_products: List[InstalledProduct] = []
        self.total_space: int = 0
        self.free_space: int = 0
        self.used_space: int = 0
        self.update_storage_info()
        self.scan_installed_products()

    def update_storage_info(self):
        if self.mount_path and self.mount_path.endswith("mock_pen"):
            self.total_space = int(3.72 * 1024 * 1024 * 1024)
            self.free_space = int(2.36 * 1024 * 1024 * 1024)
            self.used_space = self.total_space - self.free_space
            return

        try:
            stat = os.statvfs(self.mount_path)
            self.free_space = stat.f_bavail * stat.f_frsize
            self.total_space = stat.f_blocks * stat.f_frsize
            self.used_space = self.total_space - self.free_space
        except Exception:
            self.free_space = 0
            self.total_space = 0
            self.used_space = 0

    def scan_installed_products(self):
        self.installed_products.clear()
        if not os.path.exists(self.mount_path):
            return

        for root, _, files in os.walk(self.mount_path):
            for file in files:
                if file.lower().endswith(".gme") and not file.startswith("._"):
                    full_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(full_path)
                        gme_id, version = PenDetector.parse_gme_header(full_path)
                        self.installed_products.append(
                            InstalledProduct(
                                filename=file,
                                path=full_path,
                                gme_id=gme_id,
                                version=version,
                                size_bytes=size,
                            )
                        )
                    except Exception as e:
                        print(f"Error scanning {full_path}: {e}")

    @property
    def firmware_version(self) -> str:
        return self.firmware_descriptor

    @property
    def friendly_generation(self) -> str:
        """Returns human-readable generation name."""
        fw = self.firmware_descriptor.upper()
        if "REV1" in self.generation or fw.startswith("V00"):
            return "Generation 1 (ohne Player)"
        elif "REV2" in self.generation or "REV3" in self.generation or "3202" in fw:
            return "Generation 2 (mit Player)"
        elif "3205" in self.mcu or "REV14" in self.generation or "WLAN" in fw or "7GE" in fw:
            return "Generation 4 (tiptoi® WLAN)"
        elif "3203" in self.mcu or "REV4" in self.generation or "REV5" in self.generation:
            return "Generation 3 / 4"
        return f"tiptoi® ({self.generation})"

    @property
    def pen_sprite_name(self) -> str:
        gen = self.generation.upper()
        if "REV1" in gen:
            return "PenGen1@2x"
        elif "REV2" in gen or "REV3" in gen:
            return "PenGen2@2x"
        elif "REV14" in gen or "REV13" in gen or "REV4" in gen:
            return "PenRev14@2x"
        return "PenGen3@2x"

    @property
    def full_pen_sprite_name(self) -> str:
        gen = self.generation.upper()
        if "REV1" in gen:
            return "PenFullGen1@2x"
        elif "REV2" in gen or "REV3" in gen:
            return "PenFullGen2@2x"
        elif "REV14" in gen or "REV13" in gen or "REV4" in gen:
            return "PenFullRev14@2x"
        return "PenFullGen3@2x"


class PenDetector:
    @staticmethod
    def parse_gme_header(file_path: str) -> tuple[int, str]:
        """Reads GME ID (offset 20, uint32 LE) and version (offset 82, 8 bytes ASCII)."""
        with open(file_path, "rb") as f:
            header = f.read(128)
        if len(header) < 90:
            return 0, ""
        gme_id = struct.unpack("<I", header[20:24])[0]
        version = header[82:90].decode("ascii", "ignore").strip("\x00").strip()
        return gme_id, version

    @staticmethod
    def parse_log_file(log_path: str) -> Dict[str, str]:
        """
        Parses .tiptoi.log from a pen drive.
        Delimited by 0x00 and 0xFF padding.
        """
        with open(log_path, "rb") as f:
            raw = f.read()

        words = []
        cur = bytearray()
        for b in raw:
            if b in (0x00, 0xFF):
                if cur:
                    try:
                        words.append(cur.decode("utf-8", "ignore").strip())
                    except Exception:
                        pass
                    cur = bytearray()
            elif 32 <= b <= 126:
                cur.append(b)
        if cur:
            words.append(cur.decode("utf-8", "ignore").strip())

        serial = words[0] if len(words) > 0 else "Unknown"
        firmware = words[1] if len(words) > 1 else "Unknown"
        language = words[2] if len(words) > 2 else "GERMAN"
        mcu = words[3] if len(words) > 3 else ""

        # Determine generation
        generation = "REV4"
        fw_upper = firmware.upper()
        if firmware.startswith("v00") or len(words) <= 2:
            generation = "REV1"
        elif "3202MT" in fw_upper:
            generation = "REV3"
        elif "3202" in fw_upper:
            generation = "REV2"
        elif "3205" in mcu or "7GE" in fw_upper:
            generation = "REV14"
        elif "4N" in fw_upper:
            generation = "REV7"
        elif "4E" in fw_upper:
            generation = "REV8"
        elif "EMMC" in fw_upper:
            generation = "REV6"
        elif "2G" in fw_upper:
            generation = "REV5"

        return {
            "serial_number": serial,
            "firmware_descriptor": firmware,
            "language": language,
            "mcu": mcu,
            "generation": generation,
        }

    @classmethod
    def get_candidate_mount_points(cls) -> List[str]:
        """Finds all mounted filesystems that might be USB drives."""
        mounts = []
        user = os.environ.get("USER", "domi")

        # 1. Check common removable drive mount paths in Linux
        search_roots = [
            f"/run/media/{user}",
            f"/media/{user}",
            "/media",
            "/mnt",
        ]
        for sroot in search_roots:
            if os.path.exists(sroot):
                for item in os.listdir(sroot):
                    cand = os.path.join(sroot, item)
                    if os.path.isdir(cand) and cand not in mounts:
                        mounts.append(cand)

        # 2. Check /proc/mounts for FAT / vfat / msdos filesystems
        if os.path.exists("/proc/mounts"):
            try:
                with open("/proc/mounts", "r") as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 3:
                            mp = parts[1]
                            fstype = parts[2]
                            if fstype in ("vfat", "msdos", "exfat", "fuse"):
                                if mp not in mounts and not mp.startswith("/boot"):
                                    mounts.append(mp)
            except Exception:
                pass

        return mounts

    @classmethod
    def scan_path_for_pen(cls, path: str) -> Optional[PenInfo]:
        """Scans a specific folder or mount point for a connected tiptoi pen."""
        return cls.find_connected_pen(explicit_path=path)

    @classmethod
    def find_connected_pen(cls, explicit_path: Optional[str] = None) -> Optional[PenInfo]:
        """Detects if a tiptoi pen is connected to any mount point."""
        candidates = [explicit_path] if explicit_path else cls.get_candidate_mount_points()

        for cand in candidates:
            if not cand or not os.path.exists(cand):
                continue

            log_file = os.path.join(cand, ".tiptoi.log")
            if os.path.exists(log_file):
                try:
                    info = cls.parse_log_file(log_file)
                    return PenInfo(
                        mount_path=cand,
                        serial_number=info["serial_number"],
                        firmware_descriptor=info["firmware_descriptor"],
                        language=info["language"],
                        mcu=info["mcu"],
                        generation=info["generation"],
                    )
                except Exception as e:
                    print(f"Error reading .tiptoi.log in {cand}: {e}")

            # Also check if candidate directory contains tiptoi GME files
            try:
                gmes = [f for f in os.listdir(cand) if f.lower().endswith(".gme")]
                if gmes:
                    return PenInfo(
                        mount_path=cand,
                        serial_number="TIPTOI_PEN",
                        firmware_descriptor="REV4",
                        language="GERMAN",
                        generation="REV4",
                    )
            except Exception:
                pass

        return None

    @staticmethod
    def eject_pen(mount_path: str) -> bool:
        """Safely flushes and unmounts the USB drive."""
        try:
            os.sync()
        except Exception:
            pass

        # Try udisksctl first
        res = subprocess.run(["udisksctl", "unmount", "-p", mount_path], capture_output=True)
        if res.returncode == 0:
            return True

        # Fallback to gio mount
        res = subprocess.run(["gio", "mount", "-u", mount_path], capture_output=True)
        if res.returncode == 0:
            return True

        # Fallback to umount
        res = subprocess.run(["umount", mount_path], capture_output=True)
        return res.returncode == 0

    @classmethod
    def create_simulated_pen(cls, folder_path: str, generation: str = "REV14") -> PenInfo:
        """Creates a mock/simulated pen structure for testing without physical hardware."""
        os.makedirs(folder_path, exist_ok=True)
        log_path = os.path.join(folder_path, ".tiptoi.log")

        # 64-byte payload matching official firmware layout
        raw = bytearray([0xFF] * 64)
        serial = b"VC151481"
        raw[0:len(serial)] = serial

        if generation in ("REV14", "REV4"):
            fw = b"7GE022"
            lang = b"GERMAN"
            mcu = b"3205L"
        elif generation == "REV2":
            fw = b"3202_de"
            lang = b"GERMAN"
            mcu = b"3202"
        else:
            fw = b"2G0031"
            lang = b"GERMAN"
            mcu = b"3203L"

        raw[16:16+len(fw)] = fw
        raw[32:32+len(lang)] = lang
        raw[48:48+len(mcu)] = mcu

        with open(log_path, "wb") as f:
            f.write(raw)

        return cls.find_connected_pen(folder_path) # type: ignore
