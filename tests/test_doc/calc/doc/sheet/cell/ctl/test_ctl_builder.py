from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from pytest_mock import MockerFixture

if __name__ == "__main__":
    pytest.main([__file__])


def test_ctl_builder(loader, build_setup) -> None:
    from ooodev.calc import CalcDoc

    if TYPE_CHECKING:
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_builder import CtlBuilder
        from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_reader import CtlReader
        from oxt.___lo_pip___.basic_config import BasicConfig
    else:
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_builder import CtlBuilder
        from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl_reader import CtlReader
        from libre_pythonista.basic_config import BasicConfig

    doc = None
    try:
        config = BasicConfig()
        doc = CalcDoc.create_doc(loader=loader)
        sheet = doc.sheets[0]
        cell = sheet[0, 0]

        # Create command instance
        builder = CtlBuilder(cell=cell)

        # Execute command
        result = builder.build()
        # Verify execution
        assert builder.success

        assert result.ctl_code_name.startswith("id_")
        assert result.addr == f"sheet_index={sheet.sheet_index}&cell_addr={cell.cell_obj}"

        reader = CtlReader(cell=cell)
        ctl = reader.read()
        assert ctl.ctl_code_name == result.ctl_code_name
        assert ctl.addr == result.addr

    finally:
        if doc is not None:
            doc.close(True)
