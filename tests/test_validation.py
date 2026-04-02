"""Tests for the validation pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from validation.validate import validate_xml, validate_json


def test_valid_minimal_scene():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<X3D profile="Interchange" version="4.1">
  <Scene>
    <Shape>
      <Appearance>
        <Material/>
      </Appearance>
      <Box/>
    </Shape>
  </Scene>
</X3D>"""
    result = validate_xml(xml)
    assert result["valid"] is True
    assert result["errors"] == []


def test_valid_scene_with_xsi():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<X3D profile="Interchange" version="4.1"
     xmlns:xsd="https://www.w3.org/2001/XMLSchema-instance"
     xsd:noNamespaceSchemaLocation="https://www.web3d.org/specifications/x3d-4.0.xsd">
  <Scene>
    <Shape>
      <Box/>
    </Shape>
  </Scene>
</X3D>"""
    result = validate_xml(xml)
    assert result["valid"] is True


def test_invalid_unknown_node():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<X3D profile="Interchange" version="4.1">
  <Scene>
    <FakeNode/>
  </Scene>
</X3D>"""
    result = validate_xml(xml)
    assert result["valid"] is False
    assert any("FakeNode" in e for e in result["errors"])


def test_invalid_malformed_xml():
    result = validate_xml("<broken")
    assert result["valid"] is False
    assert len(result["errors"]) > 0


def test_invalid_missing_profile():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<X3D version="4.1">
  <Scene/>
</X3D>"""
    result = validate_xml(xml)
    # XSD requires profile attribute
    assert result["valid"] is False


def test_valid_json():
    json_str = '{"X3D": {"@version": "4.0", "@profile": "Interchange", "Scene": {}}}'
    result = validate_json(json_str)
    assert result["valid"] is True


def test_invalid_json_parse():
    result = validate_json("{broken")
    assert result["valid"] is False
    assert "parse error" in result["errors"][0].lower()


def test_invalid_json_missing_x3d():
    result = validate_json('{"Scene": {}}')
    assert result["valid"] is False
    assert any("X3D" in e for e in result["errors"])


def test_invalid_json_missing_fields():
    result = validate_json('{"X3D": {}}')
    assert result["valid"] is False
    assert any("@version" in e for e in result["errors"])
    assert any("@profile" in e for e in result["errors"])
    assert any("Scene" in e for e in result["errors"])
