"""X3D validation MCP tools.

Exposes validation pipeline as MCP tools.
"""

import json
from mcp.server.fastmcp import FastMCP

from validation.validate import validate_xml, validate_json
from tools.granular import _scene


def register(mcp: FastMCP):

    @mcp.tool()
    def validate_x3d(content: str, encoding: str = "xml") -> str:
        """Validate X3D content against the X3D 4.1 schema.

        Args:
            content: The X3D content string to validate.
            encoding: Content encoding - "xml" or "json".
        """
        if encoding == "xml":
            result = validate_xml(content)
        elif encoding == "json":
            result = validate_json(content)
        else:
            result = {"valid": False, "errors": [f"Unsupported encoding: {encoding}"]}
        return json.dumps(result, indent=2)

    @mcp.tool()
    def validate_current_scene() -> str:
        """Validate the current granular scene against the X3D 4.1 schema."""
        xml_content = _scene.to_xml()
        result = validate_xml(xml_content)
        return json.dumps(result, indent=2)
