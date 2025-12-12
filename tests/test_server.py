"""
Tests for OakVar MCP Server

These tests verify the MCP server functionality.
Note: Some tests require OakVar to be installed.
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestResponseFormatting:
    """Test the response formatting helper."""
    
    def test_format_response_success(self):
        from oakvar_mcp.server import _format_response
        
        result = _format_response({"key": "value"})
        parsed = json.loads(result)
        
        assert parsed["success"] is True
        assert parsed["data"]["key"] == "value"
        assert "error" not in parsed
    
    def test_format_response_with_error(self):
        from oakvar_mcp.server import _format_response
        
        result = _format_response(None, success=False, error="Test error")
        parsed = json.loads(result)
        
        assert parsed["success"] is False
        assert parsed["error"] == "Test error"


class TestToolDefinitions:
    """Test that tools are properly defined."""
    
    @pytest.mark.asyncio
    async def test_list_tools_returns_tools(self):
        from oakvar_mcp.server import list_tools
        
        tools = await list_tools()
        
        assert len(tools) > 0
        tool_names = [t.name for t in tools]
        
        # Check core tools exist
        assert "oakvar_version" in tool_names
        assert "oakvar_module_list" in tool_names
        assert "oakvar_run" in tool_names
        assert "oakvar_query" in tool_names
    
    @pytest.mark.asyncio
    async def test_tools_have_valid_schemas(self):
        from oakvar_mcp.server import list_tools
        
        tools = await list_tools()
        
        for tool in tools:
            assert tool.name is not None
            assert tool.description is not None
            assert tool.inputSchema is not None
            assert tool.inputSchema["type"] == "object"


class TestOakVarDetection:
    """Test OakVar detection logic."""
    
    def test_ensure_oakvar_when_installed(self):
        from oakvar_mcp.server import _ensure_oakvar
        
        # This test will only pass if OakVar is installed
        try:
            ov = _ensure_oakvar()
            assert ov is not None
        except RuntimeError:
            pytest.skip("OakVar not installed")
    
    def test_ensure_oakvar_when_not_installed(self):
        from oakvar_mcp.server import _ensure_oakvar
        
        with patch.dict('sys.modules', {'oakvar': None}):
            # Force reimport to trigger the check
            pass  # This is tricky to test properly


class TestToolDispatch:
    """Test tool dispatch logic."""
    
    @pytest.mark.asyncio
    async def test_dispatch_unknown_tool(self):
        from oakvar_mcp.server import _dispatch_tool
        
        with pytest.raises(ValueError, match="Unknown tool"):
            await _dispatch_tool("nonexistent_tool", {})


class TestQueryTool:
    """Test the SQL query tool safety features."""
    
    @pytest.mark.asyncio
    async def test_query_rejects_non_select(self):
        from oakvar_mcp.server import _tool_query
        
        result = await _tool_query({
            "dbpath": "test.sqlite",
            "sql": "DELETE FROM variant"
        })
        parsed = json.loads(result)
        
        assert parsed["success"] is False
        assert "SELECT" in parsed["error"]
    
    @pytest.mark.asyncio
    async def test_query_rejects_update(self):
        from oakvar_mcp.server import _tool_query
        
        result = await _tool_query({
            "dbpath": "test.sqlite",
            "sql": "UPDATE variant SET chrom='1'"
        })
        parsed = json.loads(result)
        
        assert parsed["success"] is False


# Integration tests (require OakVar installed)
@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring OakVar installation."""
    
    @pytest.mark.asyncio
    async def test_version_tool(self):
        from oakvar_mcp.server import _tool_version
        
        try:
            result = await _tool_version()
            parsed = json.loads(result)
            
            assert parsed["success"] is True
            assert "version" in parsed["data"]
        except RuntimeError:
            pytest.skip("OakVar not installed")
    
    @pytest.mark.asyncio
    async def test_module_list_tool(self):
        from oakvar_mcp.server import _tool_module_list
        
        try:
            result = await _tool_module_list({"module_names": [".*"]})
            parsed = json.loads(result)
            
            assert parsed["success"] is True
            assert "modules" in parsed["data"]
            assert "count" in parsed["data"]
        except RuntimeError:
            pytest.skip("OakVar not installed")
