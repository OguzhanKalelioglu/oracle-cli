# Changelog

All notable changes to Oracle-CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

