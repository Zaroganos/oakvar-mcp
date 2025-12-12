# OakVar MCP Server - Setup Guide

This guide explains how to set up and use the OakVar MCP Server with ChatGPT or Claude Desktop as your MCP client.

---

## Prerequisites

1. **Python 3.9+** installed on your system
2. **pip** package manager

---

## Installation

### Step 1: Install OakVar

Install OakVar and the MCP server into the same Python environment. If you use a virtual environment, make sure your MCP client is configured to run the `oakvar-mcp` executable from that environment.

```bash
pip install oakvar
```

### Step 2: Setup OakVar

Run the OakVar system setup (first time only):

```bash
ov system setup
```

This will:
- Create configuration directories
- Download the OakVar store cache
- Install required base modules
- Optionally create/login to an OakVar store account

### Step 3: Install the MCP Server

<!--
**Option A: From PyPI (when published)**
```bash
pip install oakvar-mcp
```
-->

**Option B: From source (this repo)**
```bash
git clone https://github.com/zaroganos/oakvar-mcp.git
cd oakvar-mcp
pip install -e .
```

### Step 4: Verify Installation

```bash
oakvar-mcp --help
# Or test it works:
python -c "from oakvar_mcp.server import list_tools; import asyncio; print(f'Loaded {len(asyncio.run(list_tools()))} tools')"
```

---

## Configuring MCP Clients

### Claude Desktop

1. **Locate your Claude Desktop config file:**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Edit the config file** (create if it doesn't exist):

```json
{
  "mcpServers": {
    "oakvar": {
      "command": "oakvar-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Verify**: You should see "oakvar" listed in Claude's MCP tools. Ask Claude: *"What OakVar tools do you have available?"*

---

### ChatGPT (Desktop App with MCP Support)

1. **Locate your ChatGPT config file:**
   - **macOS**: `~/Library/Application Support/ChatGPT/chatgpt_mcp_config.json`
   - **Windows**: `%APPDATA%\ChatGPT\chatgpt_mcp_config.json`
   - **Linux**: `~/.config/ChatGPT/chatgpt_mcp_config.json`

2. **Edit the config file** (create if it doesn't exist):

```json
{
  "mcpServers": {
    "oakvar": {
      "command": "oakvar-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

3. **Restart ChatGPT Desktop**

4. **Verify**: Ask ChatGPT: *"What OakVar tools do you have available?"*

---

## Using a Virtual Environment (Recommended)

If you installed OakVar and oakvar-mcp in a virtual environment, update the config to use the full path to that environment's `oakvar-mcp` executable:

**macOS/Linux:**
```json
{
  "mcpServers": {
    "oakvar": {
      "command": "/path/to/your/venv/bin/oakvar-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "oakvar": {
      "command": "C:\\path\\to\\your\\venv\\Scripts\\oakvar-mcp.exe",
      "args": [],
      "env": {}
    }
  }
}
```

---

## Troubleshooting

### "OakVar is not installed"
Install OakVar and ensure it's in the same Python environment as oakvar-mcp (for example `pip install oakvar`).

### "Modules directory is not set"
Run `ov system setup` to configure OakVar.

### MCP server not appearing in client
1. Check the config file path is correct for your OS
2. Ensure the JSON syntax is valid
3. Restart the MCP client application
4. Check client logs for error messages

### Testing the server manually
```bash
# Start the server (it will wait for MCP protocol input)
oakvar-mcp

# Or run the test suite
pip install pytest pytest-asyncio
pytest tests/ -v
```

---

## Example Prompts

Once configured, try these prompts with your AI assistant:

- *"List all installed OakVar modules"*
- *"Get information about the ClinVar module"*
- *"Install the gnomad annotator module"*
- *"Run OakVar on my VCF file at /path/to/sample.vcf"*
- *"Query the results database to find pathogenic variants"*
- *"Create a new annotator module template called my-annotator"*

---

## Available Tools

| Tool | Description |
|------|-------------|
| `oakvar_version` | Get OakVar version |
| `oakvar_system_check` | Verify installation |
| `oakvar_system_setup` | Configure OakVar |
| `oakvar_modules_dir` | Get/set modules directory |
| `oakvar_module_list` | List installed/available modules |
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

---

## Support

- **OakVar Documentation**: https://oakvar.readthedocs.io/
- **OakVar GitHub**: https://github.com/rkimoakbioinformatics/oakvar
- **MCP Protocol**: https://modelcontextprotocol.io/
