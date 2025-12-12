"""
OakVar MCP Server

A Model Context Protocol server that exposes OakVar's bioinformatics 
functionality as structured MCP tools.

This server wraps an existing OakVar installation and provides:
- Pipeline execution (annotation, reporting)
- Module management (install, list, info)
- Data querying (SQLite results)
- Development workflows (create modules)
- System management (setup, check)
"""

import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("oakvar-mcp")

# Create the MCP server instance
server = Server("oakvar-mcp")


def _format_response(data: Any, success: bool = True, error: Optional[str] = None) -> str:
    """Format a response as JSON for MCP clients."""
    response = {
        "success": success,
        "data": data,
    }
    if error:
        response["error"] = error
    return json.dumps(response, default=str, indent=2)


def _ensure_oakvar():
    """Ensure OakVar is available and importable."""
    try:
        import oakvar
        return oakvar
    except ImportError:
        raise RuntimeError(
            "OakVar is not installed in the current Python environment. Install OakVar (e.g., `pip install oakvar`) into the same environment as oakvar-mcp."
        )


# =============================================================================
# Tool Definitions
# =============================================================================

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available OakVar MCP tools."""
    return [
        # --- System Tools ---
        Tool(
            name="oakvar_version",
            description="Get the installed OakVar version",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="oakvar_system_check",
            description="Perform OakVar system checkup to verify installation",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="oakvar_system_setup",
            description="Setup or configure OakVar system",
            inputSchema={
                "type": "object",
                "properties": {
                    "clean": {
                        "type": "boolean",
                        "description": "Perform clean installation",
                        "default": False,
                    },
                    "refresh_db": {
                        "type": "boolean",
                        "description": "Refresh store server data",
                        "default": False,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="oakvar_modules_dir",
            description="Get or set the OakVar modules directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "New modules directory path (optional, omit to get current)",
                    },
                },
                "required": [],
            },
        ),
        # --- Module Tools ---
        Tool(
            name="oakvar_module_list",
            description="List installed and/or available OakVar modules",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Module name patterns to filter (regex supported)",
                        "default": [".*"],
                    },
                    "module_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by module types (annotator, reporter, etc.)",
                    },
                    "search_store": {
                        "type": "boolean",
                        "description": "Include modules from OakVar store (not just locally installed)",
                        "default": False,
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (regex supported)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="oakvar_module_info",
            description="Get detailed information about a specific module",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_name": {
                        "type": "string",
                        "description": "Name of the module to get info for",
                    },
                    "local": {
                        "type": "boolean",
                        "description": "Only check local installation (skip store lookup)",
                        "default": False,
                    },
                },
                "required": ["module_name"],
            },
        ),
        Tool(
            name="oakvar_module_install",
            description="Install OakVar modules from the store",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of module names to install",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Overwrite existing modules",
                        "default": False,
                    },
                    "skip_dependencies": {
                        "type": "boolean",
                        "description": "Skip installing module dependencies",
                        "default": False,
                    },
                },
                "required": ["module_names"],
            },
        ),
        Tool(
            name="oakvar_module_uninstall",
            description="Uninstall OakVar modules",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of module names to uninstall",
                    },
                },
                "required": ["module_names"],
            },
        ),
        Tool(
            name="oakvar_module_update",
            description="Update installed OakVar modules to latest versions",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_name_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Module name patterns to update (regex supported)",
                    },
                },
                "required": [],
            },
        ),
        # --- Pipeline Tools ---
        Tool(
            name="oakvar_run",
            description="Run the OakVar annotation pipeline on input files",
            inputSchema={
                "type": "object",
                "properties": {
                    "inputs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to input files (VCF, etc.)",
                    },
                    "annotators": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of annotator modules to run",
                    },
                    "report_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Report types to generate (e.g., 'vcf', 'excel', 'csv')",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory for results",
                    },
                    "genome": {
                        "type": "string",
                        "description": "Genome assembly (e.g., 'hg38', 'hg19')",
                    },
                    "run_name": {
                        "type": "string",
                        "description": "Name for this analysis run",
                    },
                    "mp": {
                        "type": "integer",
                        "description": "Number of cores to use for parallel processing",
                    },
                },
                "required": ["inputs"],
            },
        ),
        Tool(
            name="oakvar_report",
            description="Generate reports from an existing OakVar result database",
            inputSchema={
                "type": "object",
                "properties": {
                    "dbpath": {
                        "type": "string",
                        "description": "Path to OakVar result SQLite database",
                    },
                    "report_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Report types to generate",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory for reports",
                    },
                    "filterpath": {
                        "type": "string",
                        "description": "Path to filter configuration file",
                    },
                    "filtersql": {
                        "type": "string",
                        "description": "SQL filter expression",
                    },
                    "cols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific columns to include in report",
                    },
                },
                "required": ["dbpath"],
            },
        ),
        # --- Data Tools ---
        Tool(
            name="oakvar_sqliteinfo",
            description="Get information about an OakVar result SQLite database",
            inputSchema={
                "type": "object",
                "properties": {
                    "dbpath": {
                        "type": "string",
                        "description": "Path to the SQLite database file",
                    },
                },
                "required": ["dbpath"],
            },
        ),
        Tool(
            name="oakvar_filtersqlite",
            description="Create a filtered copy of an OakVar result database",
            inputSchema={
                "type": "object",
                "properties": {
                    "dbpaths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to SQLite database files to filter",
                    },
                    "filterpath": {
                        "type": "string",
                        "description": "Path to filter configuration file",
                    },
                    "filtersql": {
                        "type": "string",
                        "description": "SQL filter expression",
                    },
                    "includesample": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Samples to include",
                    },
                    "excludesample": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Samples to exclude",
                    },
                    "suffix": {
                        "type": "string",
                        "description": "Suffix for filtered output file",
                        "default": "filtered",
                    },
                    "out": {
                        "type": "string",
                        "description": "Output directory",
                        "default": ".",
                    },
                },
                "required": ["dbpaths"],
            },
        ),
        Tool(
            name="oakvar_query",
            description="Execute a SQL query on an OakVar result database",
            inputSchema={
                "type": "object",
                "properties": {
                    "dbpath": {
                        "type": "string",
                        "description": "Path to the SQLite database file",
                    },
                    "sql": {
                        "type": "string",
                        "description": "SQL query to execute (SELECT only for safety)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return",
                        "default": 100,
                    },
                },
                "required": ["dbpath", "sql"],
            },
        ),
        # --- Development Tools ---
        Tool(
            name="oakvar_new_module",
            description="Create a new OakVar module template",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_name": {
                        "type": "string",
                        "description": "Name for the new module",
                    },
                    "module_type": {
                        "type": "string",
                        "description": "Type of module (annotator, reporter, converter, etc.)",
                        "enum": ["annotator", "reporter", "converter", "mapper", "postaggregator"],
                    },
                },
                "required": ["module_name", "module_type"],
            },
        ),
        Tool(
            name="oakvar_new_exampleinput",
            description="Create an example input file for testing",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to create the example input file in",
                        "default": ".",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="oakvar_module_pack",
            description="Pack a module for distribution/registration",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_name": {
                        "type": "string",
                        "description": "Name of the module to pack",
                    },
                    "outdir": {
                        "type": "string",
                        "description": "Output directory for the packed module",
                    },
                    "code_only": {
                        "type": "boolean",
                        "description": "Pack only code (not data)",
                        "default": False,
                    },
                },
                "required": ["module_name"],
            },
        ),
        # --- Store Tools ---
        Tool(
            name="oakvar_store_fetch",
            description="Fetch/refresh the OakVar store cache",
            inputSchema={
                "type": "object",
                "properties": {
                    "refresh_db": {
                        "type": "boolean",
                        "description": "Fetch a clean copy of the store database",
                        "default": False,
                    },
                    "clean": {
                        "type": "boolean",
                        "description": "Install store cache from scratch",
                        "default": False,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="oakvar_store_register",
            description="Register a module in the OakVar store",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_name": {
                        "type": "string",
                        "description": "Name of the module to register",
                    },
                    "code_url": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "URLs of code zip files",
                    },
                    "data_url": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "URLs of data zip files",
                    },
                },
                "required": ["module_name"],
            },
        ),
    ]


# =============================================================================
# Tool Call Handlers
# =============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls from MCP clients."""
    try:
        result = await _dispatch_tool(name, arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        logger.exception(f"Error executing tool {name}")
        error_response = _format_response(
            data=None,
            success=False,
            error=f"{type(e).__name__}: {str(e)}"
        )
        return [TextContent(type="text", text=error_response)]


async def _dispatch_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Dispatch tool calls to appropriate handlers."""
    
    # System tools
    if name == "oakvar_version":
        return await _tool_version()
    elif name == "oakvar_system_check":
        return await _tool_system_check()
    elif name == "oakvar_system_setup":
        return await _tool_system_setup(arguments)
    elif name == "oakvar_modules_dir":
        return await _tool_modules_dir(arguments)
    
    # Module tools
    elif name == "oakvar_module_list":
        return await _tool_module_list(arguments)
    elif name == "oakvar_module_info":
        return await _tool_module_info(arguments)
    elif name == "oakvar_module_install":
        return await _tool_module_install(arguments)
    elif name == "oakvar_module_uninstall":
        return await _tool_module_uninstall(arguments)
    elif name == "oakvar_module_update":
        return await _tool_module_update(arguments)
    
    # Pipeline tools
    elif name == "oakvar_run":
        return await _tool_run(arguments)
    elif name == "oakvar_report":
        return await _tool_report(arguments)
    
    # Data tools
    elif name == "oakvar_sqliteinfo":
        return await _tool_sqliteinfo(arguments)
    elif name == "oakvar_filtersqlite":
        return await _tool_filtersqlite(arguments)
    elif name == "oakvar_query":
        return await _tool_query(arguments)
    
    # Development tools
    elif name == "oakvar_new_module":
        return await _tool_new_module(arguments)
    elif name == "oakvar_new_exampleinput":
        return await _tool_new_exampleinput(arguments)
    elif name == "oakvar_module_pack":
        return await _tool_module_pack(arguments)
    
    # Store tools
    elif name == "oakvar_store_fetch":
        return await _tool_store_fetch(arguments)
    elif name == "oakvar_store_register":
        return await _tool_store_register(arguments)
    
    else:
        raise ValueError(f"Unknown tool: {name}")


# =============================================================================
# Tool Implementations
# =============================================================================

# --- System Tools ---

async def _tool_version() -> str:
    """Get OakVar version."""
    ov = _ensure_oakvar()
    version = ov.api.version()
    return _format_response({"version": version})


async def _tool_system_check() -> str:
    """Check OakVar system."""
    ov = _ensure_oakvar()
    result = ov.api.system.check()
    return _format_response({"check_passed": result})


async def _tool_system_setup(args: Dict[str, Any]) -> str:
    """Setup OakVar system."""
    ov = _ensure_oakvar()
    ov.api.system.setup(
        clean=args.get("clean", False),
        refresh_db=args.get("refresh_db", False),
    )
    return _format_response({"message": "System setup completed"})


async def _tool_modules_dir(args: Dict[str, Any]) -> str:
    """Get or set modules directory."""
    ov = _ensure_oakvar()
    directory = args.get("directory")
    result = ov.api.system.md(directory=directory)
    return _format_response({"modules_dir": str(result) if result else None})


# --- Module Tools ---

async def _tool_module_list(args: Dict[str, Any]) -> str:
    """List modules."""
    ov = _ensure_oakvar()
    modules = ov.api.module.ls(
        module_names=args.get("module_names", [".*"]),
        module_types=args.get("module_types", []),
        search_store=args.get("search_store", False),
        tags=args.get("tags", []),
    )
    return _format_response({"modules": modules, "count": len(modules)})


async def _tool_module_info(args: Dict[str, Any]) -> str:
    """Get module info."""
    ov = _ensure_oakvar()
    info = ov.api.module.info(
        module_name=args["module_name"],
        local=args.get("local", False),
    )
    if info is None:
        return _format_response(
            data=None,
            success=False,
            error=f"Module '{args['module_name']}' not found"
        )
    return _format_response(info)


async def _tool_module_install(args: Dict[str, Any]) -> str:
    """Install modules."""
    ov = _ensure_oakvar()
    result = ov.api.module.install(
        module_names=args["module_names"],
        overwrite=args.get("overwrite", False),
        skip_dependencies=args.get("skip_dependencies", False),
        yes=True,  # Auto-confirm for MCP usage
    )
    success = result is None or result is True
    return _format_response(
        {"installed": args["module_names"]},
        success=success,
        error="Installation failed" if not success else None,
    )


async def _tool_module_uninstall(args: Dict[str, Any]) -> str:
    """Uninstall modules."""
    ov = _ensure_oakvar()
    result = ov.api.module.uninstall(
        module_names=args["module_names"],
        yes=True,  # Auto-confirm for MCP usage
    )
    return _format_response(
        {"uninstalled": args["module_names"]},
        success=result,
    )


async def _tool_module_update(args: Dict[str, Any]) -> str:
    """Update modules."""
    ov = _ensure_oakvar()
    result = ov.api.module.update(
        module_name_patterns=args.get("module_name_patterns", []),
        yes=True,  # Auto-confirm for MCP usage
    )
    return _format_response(
        {"message": "Update completed" if result else "Update failed"},
        success=result,
    )


# --- Pipeline Tools ---

async def _tool_run(args: Dict[str, Any]) -> str:
    """Run OakVar pipeline."""
    ov = _ensure_oakvar()
    
    inputs = args["inputs"]
    if isinstance(inputs, str):
        inputs = [inputs]
    
    result = ov.api.run(
        inputs=inputs,
        annotators=args.get("annotators", []),
        report_types=args.get("report_types", []),
        output_dir=args.get("output_dir", []),
        genome=args.get("genome"),
        run_name=args.get("run_name", []),
        mp=args.get("mp"),
    )
    
    return _format_response({
        "message": "Pipeline completed",
        "result": result,
    })


async def _tool_report(args: Dict[str, Any]) -> str:
    """Generate reports."""
    ov = _ensure_oakvar()
    from pathlib import Path
    
    result = ov.api.report(
        dbpath=args["dbpath"],
        report_types=args.get("report_types"),
        output_dir=Path(args["output_dir"]) if args.get("output_dir") else None,
        filterpath=args.get("filterpath"),
        filtersql=args.get("filtersql"),
        cols=args.get("cols"),
    )
    
    return _format_response({
        "message": "Report generation completed",
        "reports": result,
    })


# --- Data Tools ---

async def _tool_sqliteinfo(args: Dict[str, Any]) -> str:
    """Get SQLite database info."""
    ov = _ensure_oakvar()
    info = ov.api.util.sqliteinfo(dbpath=args["dbpath"])
    return _format_response(info)


async def _tool_filtersqlite(args: Dict[str, Any]) -> str:
    """Filter SQLite database."""
    ov = _ensure_oakvar()
    ov.api.util.filtersqlite(
        dbpaths=args["dbpaths"],
        filterpath=args.get("filterpath"),
        filtersql=args.get("filtersql"),
        includesample=args.get("includesample", []),
        excludesample=args.get("excludesample", []),
        suffix=args.get("suffix", "filtered"),
        out=args.get("out", "."),
    )
    return _format_response({"message": "Filtering completed"})


async def _tool_query(args: Dict[str, Any]) -> str:
    """Execute SQL query on result database."""
    import sqlite3
    
    dbpath = args["dbpath"]
    sql = args["sql"].strip()
    limit = args.get("limit", 100)
    
    # Safety check: only allow SELECT queries
    if not sql.upper().startswith("SELECT"):
        return _format_response(
            data=None,
            success=False,
            error="Only SELECT queries are allowed for safety"
        )
    
    # Add LIMIT if not present
    if "LIMIT" not in sql.upper():
        sql = f"{sql} LIMIT {limit}"
    
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        results = [dict(row) for row in rows]
        
        return _format_response({
            "columns": columns,
            "rows": results,
            "row_count": len(results),
        })
    finally:
        conn.close()


# --- Development Tools ---

async def _tool_new_module(args: Dict[str, Any]) -> str:
    """Create new module template."""
    ov = _ensure_oakvar()
    result = ov.api.new.module(
        module_name=args["module_name"],
        module_type=args["module_type"],
    )
    return _format_response({
        "message": f"Module '{args['module_name']}' created",
        "directory": str(result) if result else None,
    })


async def _tool_new_exampleinput(args: Dict[str, Any]) -> str:
    """Create example input file."""
    ov = _ensure_oakvar()
    result = ov.api.new.exampleinput(
        directory=args.get("directory", "."),
    )
    return _format_response({
        "message": "Example input created",
        "path": str(result) if result else None,
    })


async def _tool_module_pack(args: Dict[str, Any]) -> str:
    """Pack module for distribution."""
    ov = _ensure_oakvar()
    from pathlib import Path
    
    outdir = Path(args["outdir"]) if args.get("outdir") else None
    result = ov.api.module.pack(
        module_name=args["module_name"],
        outdir=outdir,
        code_only=args.get("code_only", False),
    )
    return _format_response({
        "message": f"Module '{args['module_name']}' packed",
        "files": {k: str(v) for k, v in result.items()} if result else None,
    })


# --- Store Tools ---

async def _tool_store_fetch(args: Dict[str, Any]) -> str:
    """Fetch store cache."""
    ov = _ensure_oakvar()
    result = ov.api.store.fetch(
        refresh_db=args.get("refresh_db", False),
        clean=args.get("clean", False),
    )
    return _format_response({
        "message": "Store cache fetched",
        "success": result,
    })


async def _tool_store_register(args: Dict[str, Any]) -> str:
    """Register module in store."""
    ov = _ensure_oakvar()
    result = ov.api.store.register(
        module_name=args["module_name"],
        code_url=args.get("code_url", []),
        data_url=args.get("data_url", []),
    )
    return _format_response({
        "message": f"Module '{args['module_name']}' registered",
        "success": result,
    })


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Run the OakVar MCP server."""
    logger.info("Starting OakVar MCP Server...")
    
    # Verify OakVar is available
    try:
        _ensure_oakvar()
        logger.info("OakVar detected successfully")
    except RuntimeError as e:
        logger.error(str(e))
        raise
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def run():
    """Entry point for the MCP server."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    run()
