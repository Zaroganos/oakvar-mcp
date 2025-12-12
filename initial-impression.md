Here is a **concise, AI-legible, complete description** of how to implement a **Python-native OakVar MCP server**

---

# **Concise Implementation Description — OakVar MCP Server (Python Native)**

**1. Purpose**
A Python process acts as an MCP server and exposes OakVar’s functionality (pipeline execution, module management, data querying, module development) as structured MCP tools. The server requires a locally installed OakVar instance and uses OakVar’s Python API directly.

---

# **2. Server Role & Relationship to OakVar**

* The MCP server is a **wrapper around an existing OakVar installation**.
* OakVar remains installed via `pip install oakvar` and configured using `ov system setup`.
* The MCP server imports OakVar’s API at runtime and calls its functions directly.
* The MCP server is started as a **separate process** (e.g., `oakvar-mcp`) and communicates with any MCP client via stdin/stdout or socket depending on client requirements.

---

# **3. Core Functional Structure**

The server defines four namespaces of tools:

### **A. oakvar.pipeline**

Wraps OakVar’s core analysis features:

* Run annotation pipelines (`ov.api.run`)
* Generate reports (`ov.api.report`)
* Filter SQLite outputs (`filtersqlite`)
* Validate inputs

### **B. oakvar.modules**

Manages module discovery and installation:

* List installed / available modules
* Search modules by name, tags, keywords
* Get module metadata
* Install / uninstall modules

### **C. oakvar.data**

Provides structured access to OakVar result databases:

* Query variant, gene, or sample tables
* Run SQL queries safely
* Export tables in various formats

### **D. oakvar.dev**

Supports module development workflows:

* Create new module templates
* Package modules
* Register modules to the OakVar store

---

# **4. Server Lifecycle**

1. **Start**: Launch the MCP server process.
2. **Environment Check**:

   * Import OakVar
   * Validate system configuration
   * Verify modules directory
3. **Tool Registration**:

   * Register all OakVar MCP tools with schema metadata.
4. **Dispatch Loop**:

   * Wait for MCP client tool calls
   * Parse JSON payload
   * Execute corresponding OakVar API calls
   * Return structured JSON responses
5. **Optional**: Track long-running tasks using a minimal job registry.

---

# **5. Input/Output Contract**

* **Input**: MCP tool invocation containing a JSON payload describing the OakVar operation (e.g., file paths, annotators, report types).
* **Output**: Strict JSON containing either:

  * Operation result (e.g., SQLite file location, module metadata, query results), or
  * A structured error with classification (missing module, invalid input, OakVar error).

---

# **6. Packaging Options**

The MCP server can be provided in three forms:

* **pip package** (recommended): installs a command such as `oakvar-mcp`.
* **Docker image**: OakVar + the MCP server in a container.
* **Local script**: invoked directly for development environments.

---

# **7. Requirements & Assumptions**

* OakVar is installed locally and accessible to Python.
* The MCP server does not modify OakVar; it only calls its API.
* The server is client-agnostic; any MCP client can interact with it using the declared tools.

---

# **8. Implementation Summary**

A Python-native OakVar MCP server is a thin protocol adapter that:

* Loads OakVar’s Python API
* Exposes its functions as MCP tools grouped into four logical namespaces
* Runs as a standalone process communicating via the MCP transport mechanism
* Returns structured JSON responses suitable for AI agents and MCP clients
* Supports extensible deployment (local, pip, Docker)

---

# **9. Implementation Status**

**✅ IMPLEMENTED** - See `oakvar_mcp/` directory

The MCP server has been implemented with the following structure:

```
mcp-work/
├── oakvar_mcp/
│   ├── __init__.py      # Package initialization
│   ├── __main__.py      # Module entry point  
│   └── server.py        # Full MCP server implementation
├── tests/
│   ├── __init__.py
│   └── test_server.py   # Unit and integration tests
├── pyproject.toml       # Package configuration
├── README.md            # Documentation
└── claude_desktop_config.example.json
```

## **Implemented Tools (20 total)**

### System (4 tools)
- `oakvar_version` - Get OakVar version
- `oakvar_system_check` - Verify installation
- `oakvar_system_setup` - Configure OakVar
- `oakvar_modules_dir` - Get/set modules directory

### Modules (5 tools)
- `oakvar_module_list` - List modules (local/store)
- `oakvar_module_info` - Get module details
- `oakvar_module_install` - Install modules
- `oakvar_module_uninstall` - Remove modules
- `oakvar_module_update` - Update modules

### Pipeline (2 tools)
- `oakvar_run` - Execute annotation pipeline
- `oakvar_report` - Generate reports

### Data (3 tools)
- `oakvar_sqliteinfo` - Database metadata
- `oakvar_filtersqlite` - Filter databases
- `oakvar_query` - SQL queries (SELECT only)

### Development (3 tools)
- `oakvar_new_module` - Create module templates
- `oakvar_new_exampleinput` - Create test inputs
- `oakvar_module_pack` - Pack for distribution

### Store (2 tools)
- `oakvar_store_fetch` - Refresh store cache
- `oakvar_store_register` - Register modules

## **Installation**

```bash
cd mcp-work
pip install -e .
```

## **Usage**

```bash
oakvar-mcp
```

Or configure in Claude Desktop using `claude_desktop_config.example.json`
