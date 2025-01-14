"""
This module writes the batch file for windows cleanup.
"""

from __future__ import annotations
from typing import Dict, Iterable, TYPE_CHECKING, Set, Tuple
import os
from pathlib import Path
from .batch_writer import BatchWriter
from ..pkg_install_data import PkgInstallData
from ....lo_util.str_list import StrList

if TYPE_CHECKING:
    from ..install_pkg import InstallPkg


class BatchWriterPs1(BatchWriter):
    def __init__(self, installer: InstallPkg) -> None:
        super().__init__(installer)
        self._line_sep = "\n"  # os.linesep

    def _write_remove_dirs_fn(self, sw: StrList) -> None:
        """
        Write the function to remove files and directories.

        Args:
            sw (StringWriter): The StringWriter to write to.
        """
        sw.append("function Remove-Folders {")
        with sw.indented():
            sw.append("param(")
            with sw.indented():
                sw.append("[string[]]$folders")
            sw.append(")")

        with sw.indented():
            sw.append("foreach ($folder in $folders) {")
            with sw.indented():
                sw.append("if (Test-Path $folder) {")
                with sw.indented():
                    sw.append("Remove-Item -Path $folder -Recurse -Force")
                    sw.append('Write-Host "Deleted folder: $($folder)"')
                sw.append("} else {")
                with sw.indented():
                    sw.append('Write-Warning "Folder not found: $($folder)"')
                sw.append("}")
            sw.append("}")
        sw.append("}")
        sw.append()

    def _write_remove_files_fn(self, sw: StrList) -> None:
        """
        Write the function to remove files and directories.

        Args:
            sw (StringWriter): The StringWriter to write to.
        """
        sw.append("function Remove-Files {")
        with sw.indented():
            sw.append("param(")
            with sw.indented():
                sw.append("[string[]]$files")
            sw.append(")")

        with sw.indented():
            sw.append("foreach ($file in $files) {")
            with sw.indented():
                sw.append("if (Test-Path $file) {")
                with sw.indented():
                    sw.append("Remove-Item -Path $file -Force")
                    sw.append('Write-Host "Deleted file: $($file)"')
                sw.append("} else {")
                with sw.indented():
                    sw.append('Write-Warning "File not found: $($file)"')
                sw.append("}")
            sw.append("}")
        sw.append("}")
        sw.append()

    def _write_remove_folders(self, target_path: str, sw: StrList, dirs: Iterable[str]) -> None:
        """
        Write the remove folders call.

        Args:
            sw (StringWriter): The StringWriter to write to.
            dirs (Iterable[str]): The directories to remove.
        """
        if not dirs:
            return

        dir_lines = f",{self._line_sep}".join([f'{d}"' for d in dirs]).split(self._line_sep)

        sw.append("$foldersToDelete = @(")
        with sw.indented():
            for d in dir_lines:
                p = Path(target_path, d)
                sw.append(f'"{p}')
        sw.append(")")
        sw.append()
        sw.append("Remove-Folders -folders $foldersToDelete")
        sw.append()

    def _write_remove_files(self, target_path: str, sw: StrList, files: Iterable[str]) -> None:
        """
        Write the remove files call.

        Args:
            sw (StringWriter): The StringWriter to write to.
            files (Iterable[str]): The files to remove.
        """
        if not files:
            return

        file_lines = f",{self._line_sep}".join([f'{f}"' for f in files]).split(self._line_sep)

        sw.append("$filesToDelete = @(")
        with sw.indented():
            for f in file_lines:
                p = Path(target_path, f)
                sw.append(f'"{p}')
        sw.append(")")
        sw.append()
        sw.append("Remove-Files -files $filesToDelete")
        sw.append()

    def _write_output_for_pkg(self, pkg: PkgInstallData, sw: StrList) -> None:
        """
        Get the text for a file.

        Args:
            pkg (PkgInstallData): The package data.
            sw (StringWriter): The StringWriter to write to.

        Returns:
            None: None
        """
        try:
            if not pkg.package:
                raise ValueError("Package name not found")
            target_path = Path(self.installer.target_path.get_package_target(pkg.package))

            dirs = pkg.data.new_dirs
            self._write_remove_folders(str(target_path), sw, dirs)

            files = pkg.data.new_files
            self._write_remove_files(str(target_path), sw, files)

            files = pkg.data.new_bin_files
            self._write_remove_files(str(target_path / "bin"), sw, files)

            files = pkg.data.new_lib_files
            self._write_remove_files(str(target_path / "lib"), sw, files)

            files = pkg.data.new_inc_files
            self._write_remove_files(str(target_path / "inc"), sw, files)
        except Exception as e:
            self.installer.log.exception("Error writing output for %s: %s", pkg.package or "unknown", e)

    def _get_file_names(self, sw: StrList) -> Set[str]:
        """
        Get the file names.

        Returns:
            set[str]: The file names.
        """

        f_names: Set[str] = set()
        results: Dict[Tuple[str, str], set] = {}
        pkgs = self.packages.get_all_packages(all_pkg=True)
        remove_json_files: Dict[str, Set[str]] = {}
        for tp in self.target_path.get_targets():
            if not tp in remove_json_files:
                remove_json_files[tp] = set()

            for pkg in pkgs:
                json_name = f"{self.installer.config.lo_implementation_name}_{pkg.name}.json"
                if not tp in results:
                    results[tp, json_name] = set()
                file_path = Path(tp, json_name)
                if file_path.exists():
                    str_p = str(file_path)
                    results[tp, json_name].add(str(file_path))
                    remove_json_files[tp].add(str_p)

        for tp_json, files in results.items():
            f_names.update(files)

        for key, value in remove_json_files.items():
            self._write_remove_files(key, sw, value)

        return f_names

    def get_contents(self) -> str:
        """
        Get the contents of the batch file.

        Returns:
            str: Contents of the batch file
        """
        sw = StrList(sep=self._line_sep)
        self._write_remove_dirs_fn(sw)
        self._write_remove_files_fn(sw)
        data_files = self._get_file_names(sw)
        for file in data_files:
            pkg = PkgInstallData.from_file(Path(file))
            self._write_output_for_pkg(pkg, sw)

        return sw.to_string()