from lib.estrutura_organizacional import OrganizationStructure, OrganizationUnit


def unit(identifier, parent, sigla, meso="GR2"):
    return OrganizationUnit(identifier, parent, sigla, sigla, "Tipo", meso, "", "", "Ativo")


def test_descendants_use_id_mae_not_mesogrupo():
    structure = OrganizationStructure(
        {
            "1": unit("1", "", "GR2"),
            "2": unit("2", "1", "CT-A", "ROTULO-DIVERGENTE"),
            "3": unit("3", "2", "UC-A"),
            "4": unit("4", "9", "FORA", "GR2"),
        },
        {"GR2": "1"},
    )
    assert {item.sigla for item in structure.descendants("1")} == {"GR2", "CT-A", "UC-A"}
    assert "FORA" not in {item.sigla for item in structure.select(regional="GR2")}


def test_structure_reports_missing_parents():
    structure = OrganizationStructure({"1": unit("1", "9", "A")}, {})
    assert structure.diagnostics()["pais_ausentes"] == ["1"]
