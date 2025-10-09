# Oracle-CLI

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Release](https://img.shields.io/github/v/release/oguzhankalelioglu/oracle-cli)](https://github.com/oguzhankalelioglu/oracle-cli/releases)
[![MCP Server](https://img.shields.io/badge/MCP-Server-blue?logo=cursor)](https://modelcontextprotocol.io)

**🚀 Interactive Oracle Database Explorer with AI-powered MCP Integration**

<div align="center">

[![Install with pipx](https://img.shields.io/badge/Install%20with-pipx-brightgreen?style=for-the-badge&logo=python)](https://github.com/oguzhankalelioglu/oracle-cli#install-with-pipx-recommended)
[![Add to Cursor](https://img.shields.io/badge/Add%20to-Cursor-blue?style=for-the-badge&logo=cursor)](https://cursor.com/en-US/install-mcp?name=oracle-cli&config=eyJjb21tYW5kIjoib3JhY2xlLWNsaSIsImFyZ3MiOlsibWNwIl19)
[![View on GitHub](https://img.shields.io/badge/View%20on-GitHub-black?style=for-the-badge&logo=github)](https://github.com/oguzhankalelioglu/oracle-cli)

</div>

                                                          
## Features

✨ **Interactive TUI** - Modern terminal interface with full keyboard navigation  
🔍 **Schema Explorer** - Browse tables, packages, procedures, and functions  
📊 **Data Preview** - View table structures and sample data  
💾 **SQL Editor** - Execute custom SQL queries  
⚡ **Lightning Fast** - Intelligent caching & prefetching for instant navigation  
🚀 **Smart Performance** - Background loading & 5-minute cache for large databases  
📋 **Copy to Clipboard** - Export table structure & data in markdown format with **Ctrl+Y**  
🤖 **AI-Ready** - Perfect for pasting into ChatGPT, Claude, Cursor, or any AI assistant  
🎨 **Syntax Highlighting** - Color-coded PL/SQL source code viewer  
⌨️ **Keyboard First** - Navigate everything with arrow keys, no mouse needed  
🔌 **No Client Required** - Uses `python-oracledb` thin mode by default  
🔗 **MCP Server** - Integrates with AI tools (Cursor, VS Code, Claude) via Model Context Protocol  
🔎 **Relationship Discovery** - Automatically find foreign key relationships between tables  
📈 **Performance Analysis** - Index analysis and optimization recommendations  
🔒 **Constraint Mapping** - Complete view of primary keys, foreign keys, unique constraints  
🔍 **Smart Search** - Search tables and columns across entire schema  

---

## 🤖 Quick Start: Add to Cursor (MCP Integration)

**Oracle-CLI now works as an MCP server!** Let AI assistants directly access your Oracle database.

### 📦 Step 1: Install Oracle-CLI

```bash
pipx install git+https://github.com/oguzhankalelioglu/oracle-cli.git
```

### ⚙️ Step 2: Configure Database Connection

```bash
oracle-cli configure
```

### 🔌 Step 3: Add to Cursor

**Option 1: One-Click Install (Easiest!)**

[![Add to Cursor](https://img.shields.io/badge/🚀_Click_to_Install_in_Cursor-blue?style=for-the-badge)](https://cursor.com/en-US/install-mcp?name=oracle-cli&config=eyJjb21tYW5kIjoib3JhY2xlLWNsaSIsImFyZ3MiOlsibWNwIl19)

Click the button above → Cursor will automatically add the configuration!

**Option 2: Manual Configuration**

Open Cursor Settings → **Features** → **Model Context Protocol** → Add this JSON:

```json
{
  "mcpServers": {
    "oracle-cli": {
      "command": "oracle-cli",
      "args": ["mcp"]
    }
  }
}
```

### ✅ Step 4: Restart Cursor & Test

Ask your AI assistant:
- *"List all tables in my database"*
- *"Show me the structure of EMPLOYEES table"*
- *"Find all customers from California"*
- *"What tables are related to EMPLOYEES?"* 🆕
- *"Show me the indexes on EMPLOYEES table"* 🆕
- *"Search for all tables containing 'customer'"* 🆕

**That's it!** 🎉 AI can now:
- ✅ Query your Oracle database automatically
- ✅ Discover table relationships and foreign keys
- ✅ Analyze indexes and constraints
- ✅ Search across your entire schema
- ✅ Provide performance optimization tips

> 💡 **Works with:** Cursor, VS Code, Claude Desktop, and any MCP-compatible AI tool

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Oracle Database (tested with 11g, 12c, 18c, 19c, 21c, 23c)

### Install with pipx (Recommended)

```bash
pipx install git+https://github.com/oguzhankalelioglu/oracle-cli.git
```

### Install with pip

```bash
pip install git+https://github.com/oguzhankalelioglu/oracle-cli.git
```

### Install from source

```bash
git clone https://github.com/oguzhankalelioglu/oracle-cli.git
cd oracle-cli
pip install -e .
```

## Updating

### Update with pipx (Recommended)

```bash
pipx upgrade oracle-cli
```

Or reinstall from GitHub for the latest version:

```bash
pipx uninstall oracle-cli
pipx install git+https://github.com/oguzhankalelioglu/oracle-cli.git
```

### Update with pip

```bash
pip install --upgrade git+https://github.com/oguzhankalelioglu/oracle-cli.git
```

### Update from source

```bash
cd oracle-cli
git pull
pip install -e . --upgrade
```

**After updating:**
- Configuration file (`~/.oracle_cli/config.json`) is preserved
- Cache is automatically cleared on first run
- Press `R` in TUI to clear cache and see new features

## Quick Start

### 1. Configure Connection

Save your Oracle connection details:

```bash
oracle-cli configure
```

You'll be prompted for:
- **Username**: Your Oracle database username
- **Password**: Your database password
- **DSN**: Connection string (e.g., `localhost:1521/XEPDB1` or `hostname:1521/ORCL`)
- **Schema**: Default schema to explore (defaults to username)

### 2. Launch TUI

```bash
oracle-cli
```

That's it! The interactive TUI will open.

## Usage

### Interactive TUI (Default)

Launch the full-featured terminal interface:

```bash
oracle-cli
# or explicitly
oracle-cli tui
```

#### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **↑/↓ Arrows** | Navigate through objects |
| **Tab** | Switch focus between panels |
| **Ctrl+Y** | 📋 Copy selected object to clipboard (markdown format) |
| **Ctrl+S** | Toggle search |
| **Ctrl+P** | Show procedures only |
| **Ctrl+K** | Show packages only |
| **Ctrl+E** | Open SQL editor |
| **F1** | Show About/Help screen |
| **R** | Refresh object list |
| **ESC** | Close panels/Cancel |
| **Q** | Quit application |

#### 🤖 AI Assistant Integration

Press **Ctrl+Y** on any selected object to copy:
- **Tables**: Complete structure + sample data in markdown tables
- **PL/SQL Objects**: Full source code in code blocks

Perfect for:
- Asking AI to explain table structures
- Getting AI help with PL/SQL code
- Generating queries based on table schema
- Database documentation

Example workflow:
1. Open `oracle-cli` in your terminal
2. Navigate to a table using ↑/↓ arrows
3. Press **Ctrl+Y** to copy
4. Paste into ChatGPT/Claude/Cursor and ask: "Explain this table structure"

### Command Line Interface

You can also use oracle-cli as a traditional CLI tool:

```bash
# List all tables
oracle-cli list-tables

# Describe table structure
oracle-cli describe-table EMPLOYEES

# Preview table data
oracle-cli preview-table EMPLOYEES --limit 10

# List packages
oracle-cli list-packages --with-body

# List procedures
oracle-cli list-programs --type procedure

# Show PL/SQL source code
oracle-cli show-source MY_PACKAGE --type package

# Show package body
oracle-cli show-source MY_PACKAGE --type package --body

# Switch schema
oracle-cli use-schema HR
```

### Connection Options

#### Using Environment Variables

```bash
export ORACLE_USER=hr
export ORACLE_PASSWORD='your_password'
export ORACLE_DSN='localhost:1521/XEPDB1'
export ORACLE_SCHEMA='HR'  # Optional

oracle-cli
```

#### Using Command Line Options

```bash
oracle-cli --user hr --password secret --dsn localhost:1521/XEPDB1 --schema HR
```

## Configuration

Connection details are stored in `~/.oracle_cli/config.json`. You can:

- Update configuration: `oracle-cli configure`
- Use custom path: `oracle-cli configure --path /custom/path/config.json`

**Note**: Configuration file may contain sensitive information. Never commit it to version control.

## Performance

Oracle-CLI is optimized for large databases with thousands of tables:

### 🚀 Smart Caching System
- **Intelligent Cache**: Table structures and data are cached for 5 minutes
- **Instant Navigation**: Second visit to a table is instant (from cache)
- **Auto-Refresh**: Press **R** to clear cache and reload
- **Schema-Aware**: Changing schemas automatically clears cache

### ⚡ Background Prefetching
- **Predictive Loading**: Next 2-3 tables are loaded in background
- **Seamless Experience**: By the time you navigate, data is ready
- **Smart Queue**: Only prefetches items you're likely to visit

### 📊 Performance Tips
```bash
# For very large databases (10,000+ tables)
oracle-cli tui --limit 20  # Reduce data preview rows

# Enable debug mode to see cache hits
oracle-cli tui --debug

# Check cache statistics
# Open TUI, press F1 (About) - shows cache count
```

**Performance Improvements:**
- ✅ First table load: ~200-500ms
- ✅ Cached table load: **<50ms** (4-10x faster!)
- ✅ Prefetched table: **Instant** (already loaded)

## Oracle Client

By default, `python-oracledb` runs in **thin mode** (no Oracle Client required).

If your organization requires Oracle Instant Client:

1. Install Oracle Instant Client
2. Set the `ORACLE_CLIENT_LIB_DIR` environment variable
3. The tool will automatically use thick mode

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/oguzhankalelioglu/oracle-cli.git
cd oracle-cli

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Project Structure

```
oracle-cli/
├── oracle_cli/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py          # CLI commands
│   ├── config.py       # Configuration management
│   ├── db.py           # Database operations
│   └── tui.py          # Text User Interface
├── pyproject.toml      # Project metadata
├── README.md
├── LICENSE
└── INSTALL.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Oğuzhan Kalelioğlu**
- GitHub: [@oguzhankalelioglu](https://github.com/oguzhankalelioglu)

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) - An amazing TUI framework
- Uses [python-oracledb](https://oracle.github.io/python-oracledb/) - Oracle's official Python driver
- CLI powered by [Click](https://click.palletsprojects.com/)
- Pretty output by [Rich](https://rich.readthedocs.io/)

## 🔧 Advanced MCP Configuration

### Available MCP Tools

- ✅ **13 Powerful Tools**: List tables, describe structures, query data, analyze relationships
- 🔒 **Secure**: SELECT-only queries, local stdio access
- ⚡ **Fast**: Uses existing caching system
- 🎯 **Smart**: AI automatically selects the right tools
- 🔗 **Relational**: Discover table relationships and dependencies
- 📊 **Analytical**: Index analysis, constraint mapping, performance insights

### MCP Tools Reference

#### 📊 Basic Information (4 tools)
| Tool | Description |
|------|-------------|
| `list_tables` | List all tables in the schema |
| `describe_table` | View detailed table structure (columns, types, constraints) |
| `query_table` | Get sample data from a table |
| `get_table_stats` | Get table statistics (row count, size, segments) |

#### 🔗 Relationship Analysis (4 tools)
| Tool | Description |
|------|-------------|
| `get_table_relationships` | View foreign key relationships (parent & child tables) |
| `get_table_constraints` | Show all constraints (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK) |
| `get_related_tables` | Find all related tables through foreign key relationships |
| `get_table_indexes` | List all indexes with performance insights |

#### 🔍 Search & Discovery (1 tool)
| Tool | Description |
|------|-------------|
| `search_tables` | Search tables and columns by keyword across schema |

#### 🛠️ Advanced Tools (4 tools)
| Tool | Description |
|------|-------------|
| `execute_sql` | Run custom SELECT queries (read-only) |
| `get_table_triggers` | List table triggers with event details |
| `list_objects` | List PL/SQL packages, procedures, functions |
| `get_source` | View PL/SQL source code |

**For detailed setup and troubleshooting:** [MCP_SETUP.md](MCP_SETUP.md)

## Roadmap

- [x] Copy to clipboard (markdown format) ✅
- [x] Full keyboard navigation ✅
- [x] **MCP Server Integration** ✅
- [x] **Table relationships viewer** ✅ **NEW in v1.2.0!**
- [x] **Index and constraint viewer** ✅ **NEW in v1.2.0!**
- [x] **Advanced schema analysis** ✅ **NEW in v1.2.0!**
- [ ] Export data to CSV/JSON
- [ ] Save and load SQL queries
- [ ] Support for database diagrams
- [ ] Multi-connection management
- [ ] Query history
- [ ] Custom themes
- [ ] Plugin system
- [ ] ER diagram visualization
- [ ] Performance monitoring dashboard

## Support

If you encounter any issues or have questions:

- 📫 Open an [issue](https://github.com/oguzhankalelioglu/oracle-cli/issues)
- 💬 Start a [discussion](https://github.com/oguzhankalelioglu/oracle-cli/discussions)

---

**Note**: This tool is designed for development and database exploration. Always follow your organization's security policies when connecting to production databases.
