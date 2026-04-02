"""X3D validation pipeline.

Validates X3D content against the X3D 4.1 XSD schema using lxml.
Supports XML, JSON, and basic structural checks.
"""

import json
from pathlib import Path
from lxml import etree


SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"
XSD_PATH = SCHEMAS_DIR / "x3d-4.1.xsd"

# XSI namespace attribute that x3d.py adds -- must be stripped before validation
XSI_NS = "https://www.w3.org/2001/XMLSchema-instance"

_schema = None


def _get_schema() -> etree.XMLSchema:
    """Load and cache the X3D 4.1 XSD schema."""
    global _schema
    if _schema is not None:
        return _schema
    # Parse with the schemas dir as base so includes resolve correctly
    schema_doc = etree.parse(str(XSD_PATH))
    _schema = etree.XMLSchema(schema_doc)
    return _schema


def _strip_xsi(root: etree._Element) -> None:
    """Remove xsi namespace attributes that x3d.py injects."""
    for attr in list(root.attrib):
        if XSI_NS in attr:
            del root.attrib[attr]
    # Also remove the xsd namespace prefix declaration if present
    nsmap = dict(root.nsmap)
    if "xsd" in nsmap or "xsi" in nsmap:
        # Can't remove nsmap directly, so rebuild the element
        pass


def validate_xml(xml_string: str) -> dict:
    """Validate X3D XML content against the XSD schema.

    Returns {"valid": bool, "errors": list[str]}.
    """
    errors = []

    # Step 1: Parse XML (well-formedness)
    try:
        doc = etree.fromstring(xml_string.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        return {"valid": False, "errors": [f"XML parse error: {e}"]}

    # Step 2: Strip xsi attributes that x3d.py adds
    _strip_xsi(doc)

    # Step 3: Validate against XSD
    schema = _get_schema()
    valid = schema.validate(doc)
    if not valid:
        for entry in schema.error_log:
            errors.append(f"Line {entry.line}: {entry.message}")

    return {"valid": valid, "errors": errors}


def validate_scene(scene_manager) -> dict:
    """Validate the current scene by serializing to XML and running XSD checks.

    Returns {"valid": bool, "errors": list[str]}.
    """
    xml_string = scene_manager.to_xml()
    return validate_xml(xml_string)


def validate_json(json_string: str) -> dict:
    """Basic structural validation of X3D JSON content.

    Returns {"valid": bool, "errors": list[str]}.
    """
    errors = []

    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        return {"valid": False, "errors": [f"JSON parse error: {e}"]}

    if "X3D" not in data:
        errors.append("Missing root 'X3D' object")
        return {"valid": False, "errors": errors}

    x3d = data["X3D"]
    if "@version" not in x3d:
        errors.append("Missing '@version' in X3D object")
    if "@profile" not in x3d:
        errors.append("Missing '@profile' in X3D object")
    if "Scene" not in x3d:
        errors.append("Missing 'Scene' in X3D object")

    return {"valid": len(errors) == 0, "errors": errors}
