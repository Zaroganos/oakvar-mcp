# OakVar MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes [OakVar](https://oakvar.readthedocs.io/)'s genomic variant analysis capabilities to AI assistants.

**Supported MCP Clients:** Claude Desktop, ChatGPT Desktop, and other MCP-compatible clients.

## Quick Start

```bash
# 1. Install OakVar and the MCP server
pip install oakvar oakvar-mcp

# 2. Setup OakVar (first time only)
ov system setup

# 3. Configure your MCP client (see SETUP.md)
```

📖 **Full setup instructions**: See [SETUP.md](SETUP.md)

## What is This?

This MCP server lets you control OakVar through AI assistants like Claude or ChatGPT. Instead of running command-line tools, you can simply ask:

- *"What OakVar modules are installed?"*
- *"Install the ClinVar annotator"*
- *"Run OakVar on my VCF file with gnomAD annotation"*
- *"Show me pathogenic variants from the results"*

## Features

| Category | Capabilities |
|----------|--------------|
| **Pipeline** | Run annotations, generate reports (VCF, Excel, CSV) |
| **Modules** | Install, update, list, search 200+ annotator modules |
| **Data** | Query result databases, filter variants, export data |
| **Development** | Create module templates, pack for distribution |

## Architecture

```
┌─────────────────┐     MCP Protocol     ┌──────────────────┐
│   Claude /      │◄───────────────────►│  OakVar MCP      │
│   ChatGPT       │    (stdin/stdout)    │     Server       │
└─────────────────┘                      └────────┬─────────┘
                                                  │
                                                  │ Python API
                                                  ▼
                                         ┌──────────────────┐
                                         │     OakVar      │
                                         │ Variant Analysis │
                                         └──────────────────┘
```

## Installation

Note: OakVar and this MCP server must be installed in the same Python environment. If you use a virtual environment, configure your MCP client to use the full path to that environment's `oakvar-mcp` executable.

<!--
### From PyPI

```bash
pip install oakvar-mcp
```
-->

### From Source

```bash
git clone https://github.com/zaroganos/oakvar-mcp.git
cd oakvar-mcp
pip install -e .
```

## Configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "oakvar": {
      "command": "oakvar-mcp"
    }
  }
}
```

### ChatGPT Desktop

Add to `chatgpt_mcp_config.json`:

```json
{
  "mcpServers": {
    "oakvar": {
      "command": "oakvar-mcp"
    }
  }
}
```

📖 **Config file locations and troubleshooting**: See [SETUP.md](SETUP.md)

## Available Tools (19)

| Tool | Description |
|------|-------------|
| `oakvar_version` | Get OakVar version |
| `oakvar_system_check` | Verify installation |
| `oakvar_system_setup` | Configure OakVar |
| `oakvar_modules_dir` | Get/set modules directory |
| `oakvar_module_list` | List modules |
| `oakvar_module_info` | Get module details |
| `oakvar_module_install` | Install modules |
| `oakvar_module_uninstall` | Remove modules |
| `oakvar_module_update` | Update modules |
| `oakvar_run` | Run annotation pipeline |
| `oakvar_report` | Generate reports |
| `oakvar_sqliteinfo` | Get database info |
| `oakvar_filtersqlite` | Filter databases |
| `oakvar_query` | Execute SQL queries |
| `oakvar_new_module` | Create module templates |
| `oakvar_new_exampleinput` | Create test inputs |
| `oakvar_module_pack` | Pack for distribution |
| `oakvar_store_fetch` | Refresh store cache |
| `oakvar_store_register` | Register modules |

## Development

```bash
# Clone and install in dev mode
git clone https://github.com/zaroganos/oakvar-mcp.git
cd oakvar-mcp
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## Project Structure

```
oakvar-mcp/
├── oakvar_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   └── server.py
├── tests/
│   └── test_server.py
├── pyproject.toml
├── README.md
├── SETUP.md
├── claude_desktop_config.example.json
└── chatgpt_mcp_config.example.json
```

## License

MIT License

## Links

- [OakVar Documentation](https://oakvar.readthedocs.io/)
- [OakVar GitHub](https://github.com/zaroganos/oakvar)
- [Model Context Protocol](https://modelcontextprotocol.io/)
