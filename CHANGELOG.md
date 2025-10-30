# Changelog

All notable changes to Oracle-CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.4] - 2025-01-XX

### 🐛 Bug Fixes
- **PL/SQL Syntax Highlighting Fixed**: Package body and PL/SQL code now displays with proper syntax highlighting
  - Fixed: Changed from non-existent 'plsql' lexer to 'sql' lexer
  - SQL keywords (SELECT, CREATE, BEGIN, END, etc.) now colored
  - Strings, comments, and identifiers now properly highlighted
  - Dynamic theme selection: monokai for dark mode, github-dark for light mode
  - Improved code readability with proper color contrast

## [1.2.3] - 2025-01-XX

### ✨ New Features
- **Package Body Scroll Navigation**: Package body source code can now be scrolled with arrow keys
  - Changed from `ScrollableContainer` to `VerticalScroll` for better scroll support
  - Package body view is now focusable - automatically focuses when selected
  - Arrow keys (↑/↓) scroll by 3 lines at a time
  - Page Up/Down for larger scroll increments
  - Home/End keys jump to top/bottom of code
  - Mouse wheel scrolling also works
  - After selecting a package body with Enter, arrow keys immediately work for navigation

### 🐛 Bug Fixes
- Fixed scroll functionality for long package body source code
  - Previously couldn't scroll through package body content
  - Now uses proper Textual `VerticalScroll` container for native scroll support

## [1.2.2] - 2025-10-09

### 🐛 Critical Bug Fix
- **Windows MCP Server Fix**: Fixed `__main__.py` to properly handle MCP server mode
  - **Issue 1**: Previous version was ignoring the `mcp` argument and starting the normal CLI instead
  - **Issue 2**: Fixed async function handling - now correctly uses `run_mcp_server()` instead of calling `main()` directly
  - `python -m oracle_cli mcp` now correctly starts the MCP server
  - This was the root cause of Windows MCP server not working in Cursor

## [1.2.1] - 2025-10-09

### 🐛 Bug Fixes
- **Auto-save Configuration**: Connection details are now automatically saved when entered interactively
  - No need to run `oracle-cli configure` separately anymore
  - First run will prompt for connection details and save them automatically
  - Shows confirmation message with config file location

### 🪟 Windows Improvements
- **Windows MCP Support**: Added Windows-specific MCP configuration instructions
  - Recommended: Use `python -m oracle_cli mcp` for Windows
  - Alternative: Use full path to `oracle-cli.exe`
  - Detailed setup guide in README for both options

### 📝 Documentation
- Updated README with Windows-specific MCP setup instructions
- Added clear configuration path examples for Windows users
- Improved first-time setup experience documentation

## [1.2.0] - 2025-10-09

### 🎯 Advanced MCP Tools (NEW!)
- **6 New MCP Tools** for advanced database analysis and schema discovery:
  - `get_table_relationships` - View foreign key relationships (parent & child tables)
  - `get_table_indexes` - List all indexes with performance insights
  - `get_table_constraints` - Display all constraints (PK, FK, UK, CHECK)
  - `get_related_tables` - Find all related tables through FK relationships
  - `search_tables` - Search tables and columns by keyword
  - `get_table_triggers` - List table triggers with event details

### 🔍 Enhanced Schema Discovery
- **Relationship Analysis**: Automatically discover table dependencies
- **Performance Insights**: Index analysis for optimization recommendations
- **Smart Search**: Find tables and columns across entire schema
- **Constraint Mapping**: Complete view of data integrity rules

### 🤖 AI Model Benefits
- **Better Context**: AI can now understand table relationships
- **Smarter Queries**: AI suggests optimal joins based on FK relationships
- **Performance Tips**: AI can recommend missing indexes
- **Schema Navigation**: AI helps discover related data across tables

### 🛠️ Technical Improvements
- Schema normalization for all new tools
- Fallback queries for different privilege levels
- Comprehensive error handling
- Markdown-formatted output for better readability

### 📊 Total MCP Tools: 13
- 4 Basic Info Tools (tables, describe, query, stats)
- 4 Relationship Tools (relationships, constraints, related, indexes)
- 1 Search Tool (search_tables)
- 3 Advanced Tools (SQL, triggers, PL/SQL objects)
- 1 Source Code Tool (get_source)

## [1.1.0] - 2025-10-09

### 🤖 MCP Integration (NEW!)
- **MCP Server Support**: Oracle-CLI can now run as a Model Context Protocol server
- **AI Tool Integration**: Direct integration with Cursor, VS Code, Claude Desktop, and other AI tools
- **7+ MCP Tools**: 
  - `list_tables` - List all tables in schema
  - `describe_table` - View table structure
  - `query_table` - Query table data
  - `execute_sql` - Execute custom SQL queries (SELECT only)
  - `list_objects` - List PL/SQL objects
  - `get_source` - View source code
  - `get_table_stats` - Get table statistics
- **Security**: SELECT-only queries, local stdio access
- **Documentation**: Detailed MCP setup guide (MCP_SETUP.md)

### ✨ Added
- `oracle-cli mcp` command - Starts the MCP server
- MCP configuration example (mcp-config-example.json)
- Comprehensive MCP documentation
- Cursor, VS Code, Claude Desktop integration examples

### 📦 Dependencies
- Added `mcp>=0.9.0` package

### 📝 Documentation
- Added MCP section to README
- MCP_SETUP.md detailed installation guide
- Usage examples and troubleshooting

## [1.0.1] - 2025-01-10

### 🚀 Performance Improvements
- **Smart Cache System**: Implemented intelligent caching with 5-minute TTL
- **Background Prefetching**: Next 2-3 items are loaded in background
- **4-10x Faster**: Navigation speed improved dramatically for large databases
- **Auto-clear Cache**: Cache automatically cleared on schema change
- **Cache Statistics**: View cache stats in About screen (F1)

### ✨ Added
- `--version` flag to display current version
- Update instructions in README
- Performance documentation section
- Cache hit/miss logging in debug mode

### 🔧 Changed
- First table load: ~200-500ms
- Cached table load: <50ms (4-10x faster!)
- Prefetched table: Instant (already loaded)
- Memory efficient with TTL-based expiration

### 📝 Documentation
- Added "Updating" section to README
- Performance benchmarks and tips
- Cache behavior documentation

## [1.0.0] - 2025-01-09

### 🎉 Initial Release

### ✨ Features
- **Interactive TUI**: Modern terminal interface powered by Textual
- **Full Keyboard Navigation**: Navigate everything with arrow keys and shortcuts
- **Copy to Clipboard**: Export table structure & data in markdown format (Ctrl+Y)
- **AI-Ready**: Perfect for pasting into ChatGPT, Claude, Cursor
- **Schema Explorer**: Browse tables, packages, procedures, functions
- **SQL Editor**: Execute custom SQL queries with syntax highlighting
- **Search**: Instant filtering and object search
- **PL/SQL Viewer**: Syntax-highlighted source code viewer
- **No Oracle Client Required**: Uses python-oracledb thin mode

### ⌨️ Keyboard Shortcuts
- **↑/↓**: Navigate objects
- **Tab**: Switch focus
- **Ctrl+Y**: Copy to clipboard
- **Ctrl+S**: Search
- **Ctrl+P**: Show procedures
- **Ctrl+K**: Show packages
- **Ctrl+E**: SQL editor
- **F1**: About screen
- **R**: Refresh
- **Q**: Quit

### 📦 Installation
```bash
pipx install git+https://github.com/OguzhanKalelioglu/oracle-cli.git
```

### 🔧 Requirements
- Python 3.10+
- Oracle Database 11g or higher
- Dependencies: oracledb, click, rich, textual, pyperclip

---

## Release Links

- **v1.0.1**: https://github.com/OguzhanKalelioglu/oracle-cli/releases/tag/v1.0.1
- **v1.0.0**: https://github.com/OguzhanKalelioglu/oracle-cli/releases/tag/v1.0.0

## Upgrade Instructions

### From any version:
```bash
pipx upgrade oracle-cli
```

Or reinstall:
```bash
pipx uninstall oracle-cli
pipx install git+https://github.com/OguzhanKalelioglu/oracle-cli.git
```

---

[1.0.1]: https://github.com/OguzhanKalelioglu/oracle-cli/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/OguzhanKalelioglu/oracle-cli/releases/tag/v1.0.0

