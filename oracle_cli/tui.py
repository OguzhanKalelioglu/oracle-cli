from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from rich.syntax import Syntax
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import (
    Checkbox,
    ContentSwitcher,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Select,
    Static,
    TabPane,
    TabbedContent,
    TextArea,
)

from . import db
from .db import ConnectionConfig


def debug_log(message: str, debug_mode: bool = False):
    """Helper function to write debug logs to a file when in debug mode."""
    if debug_mode:
        from pathlib import Path
        import datetime
        log_file = Path.home() / ".oracle_cli" / "logs" / "tui_debug.log"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
            f.flush()


FILTER_OPTIONS: Sequence[Tuple[str, str, bool]] = (
    ("TABLE", "Tablolar", True),
    ("PACKAGE", "Packages", False),
    ("PACKAGE BODY", "Package Body", False),
    ("PROCEDURE", "Procedurler", False),
    ("FUNCTION", "Fonksiyonlar", False),
)


OBJECT_LABELS: Dict[str, str] = {
    "TABLE": "Tablo",
    "PACKAGE": "Package",
    "PACKAGE BODY": "Package Body",
    "PROCEDURE": "Prosedür",
    "FUNCTION": "Fonksiyon",
}


def sanitize_object_type_id(object_type: str) -> str:
    """Return a safe identifier suffix for use in widget ids."""

    return object_type.lower().replace(" ", "-")


@dataclass
class ExplorerItem:
    name: str
    object_type: str


class ExplorerListItem(ListItem):
    """List item that keeps a reference to the underlying database object."""

    def __init__(self, entry: ExplorerItem):
        label = f"[bold]{entry.name}[/] [dim]{OBJECT_LABELS.get(entry.object_type, entry.object_type)}[/]"
        super().__init__(Label(label, markup=True))
        self.entry = entry


class MessageListItem(ListItem):
    """Non-selectable message item."""

    can_focus = False

    def __init__(self, message: str):
        super().__init__(Label(message, markup=True))


class TableDetail(Widget):
    """Widget rendering table column metadata and data preview."""

    DEFAULT_CSS = """
    TableDetail {
        width: 1fr;
        height: 1fr;
    }
    
    TableDetail TabbedContent {
        height: 1fr;
    }
    
    TableDetail DataTable {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        with TabbedContent(id="table-tabs"):
            with TabPane("Kolonlar", id="columns-pane"):
                yield DataTable(id="columns-table")
            with TabPane("Veri", id="rows-pane"):
                yield DataTable(id="rows-table")

    def on_mount(self) -> None:
        columns_table = self.query_one("#columns-table", DataTable)
        columns_table.cursor_type = "row"
        columns_table.zebra_stripes = True
        rows_table = self.query_one("#rows-table", DataTable)
        rows_table.cursor_type = "row"
        rows_table.zebra_stripes = True

    def clear(self) -> None:
        columns_table = self.query_one("#columns-table", DataTable)
        rows_table = self.query_one("#rows-table", DataTable)
        columns_table.clear(columns=True)
        rows_table.clear(columns=True)

    def update_detail(
        self,
        columns: Sequence[Tuple],
        rows: Sequence[Sequence],
        column_names: Sequence[str],
        debug_mode: bool = False,
    ) -> None:
        columns_table = self.query_one("#columns-table", DataTable)
        rows_table = self.query_one("#rows-table", DataTable)

        debug_log(f"update_detail called: {len(columns)} columns, {len(rows)} rows", debug_mode)

        columns_table.clear(columns=True)
        columns_table.add_columns(
            "Kolon",
            "Tip",
            "Uzunluk",
            "Precision",
            "Scale",
            "Nullable",
            "Varsayılan",
        )
        debug_log(f"Columns table headers added", debug_mode)
        
        for (
            _,
            column_name,
            data_type,
            data_length,
            data_precision,
            data_scale,
            nullable,
            data_default,
        ) in columns:
            columns_table.add_row(
                column_name,
                data_type,
                str(data_length or ""),
                str(data_precision or ""),
                str(data_scale or ""),
                nullable,
                (data_default or "").strip(),
            )
        
        debug_log(f"Columns table populated with {columns_table.row_count} rows", debug_mode)

        rows_table.clear(columns=True)
        if column_names:
            debug_log(f"Adding {len(column_names)} column headers to rows table", debug_mode)
            rows_table.add_columns(*column_names)
            debug_log(f"Row table columns added", debug_mode)
            
            row_count = 0
            for row in rows:
                def format_value(value):
                    if value is None:
                        return "NULL"
                    elif isinstance(value, bytes):
                        # CLOB/BLOB değerlerini decode et
                        try:
                            return value.decode('utf-8')
                        except UnicodeDecodeError:
                            return f"<binary data: {len(value)} bytes>"
                    else:
                        return str(value)
                
                rows_table.add_row(*(format_value(value) for value in row))
                row_count += 1
            
            debug_log(f"Rows table populated with {row_count} rows (table.row_count={rows_table.row_count})", debug_mode)
        else:
            debug_log("No column names provided, skipping rows", debug_mode)


class CodeDetail(Static):
    """Widget rendering PL/SQL source code."""

    def show_source(self, name: str, object_type: str, source: str) -> None:
        language = "plsql"
        title = f"-- {object_type} {name}"
        code = f"{title}\n\n{source.strip()}"
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.update(syntax)


class AboutScreen(Static):
    """About/Status screen with ASCII art and version info."""

    DEFAULT_CSS = """
    AboutScreen {
        width: 100%;
        height: 100%;
        content-align: center middle;
        background: $surface;
        border: solid $primary;
    }
    """

    def __init__(self):
        ascii_art = """
[bold red]
   ____                 _              _____ _      _____ 
  / __ \               | |            / ____| |    |_   _|
 | |  | |_ __ __ _  ___| | ___ ______| |    | |      | |  
 | |  | | '__/ _` |/ __| |/ _ \______| |    | |      | |  
 | |__| | | | (_| | (__| |  __/      | |____| |____ _| |_ 
  \____/|_|  \__,_|\___|_|\___|       \_____|______|_____|
                                                          
                                                          
                                                  
[/bold red][cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]

[bold white]Oracle-CLI TUI[/bold white]
[dim]Interactive Oracle Database Explorer[/dim]

[bold cyan]Version:[/bold cyan]     [yellow]1.0.0[/yellow]
[bold cyan]Developer:[/bold cyan]   [yellow]Oğuzhan Kalelioğlu[/yellow]
[bold cyan]GitHub:[/bold cyan]      [yellow]https://github.com/oguzhankalelioglu[/yellow]
[bold cyan]License:[/bold cyan]     [yellow]MIT[/yellow]
[bold cyan]Python:[/bold cyan]      [yellow]3.10+[/yellow]

[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]

[dim]Keyboard Shortcuts:[/dim]
  [bold]↑↓[/bold]      - Navigate       [bold]Ctrl+S[/bold] - Search
  [bold]Tab[/bold]     - Next focus     [bold]Ctrl+P[/bold] - Procedures
  [bold]Ctrl+K[/bold]  - Packages       [bold]Ctrl+E[/bold] - SQL Editor
  [bold]Ctrl+Y[/bold]  - Copy data      [bold]R[/bold]      - Refresh
  [bold]F1[/bold]      - About          [bold]Q[/bold]      - Quit
  [bold]ESC[/bold]     - Close/Cancel

[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]

[dim]✨ Press Ctrl+Y to copy table structure & data in markdown format[/dim]
[dim]   Perfect for pasting into AI chat tools like ChatGPT, Claude, Cursor![/dim]
[dim]Press ESC to close this screen[/dim]
"""
        super().__init__(ascii_art, markup=True)


class OracleExplorerApp(App[None]):
    """Interactive Oracle schema explorer built with Textual."""
    
    TITLE = "Oracle-CLI"

    CSS = """
    Screen {
        layout: vertical;
    }

    #controls {
        layout: horizontal;
        padding: 1 2;
        border-bottom: solid #3b3f45;
        height: 3;
    }

    #schema-select {
        width: 30%;
    }

    #filters {
        layout: horizontal;
        align-horizontal: left;
        padding-left: 2;
    }

    #filters > Checkbox {
        padding-right: 1;
    }

    #content {
        layout: horizontal;
        height: 1fr;
    }

    #object-list {
        width: 35%;
        border-right: solid #3b3f45;
    }

    #detail-switcher {
        width: 1fr;
        padding: 1;
    }

    #detail-switcher Static {
        padding: 1;
    }

    #error-panel {
        padding: 2;
        background: $error-darken-1;
        color: $text;
        border: solid red;
    }
    
    #search-container {
        height: 0;
        overflow: hidden;
        background: $boost;
        border-bottom: solid $primary;
    }
    
    #search-container.visible {
        height: auto;
        padding: 1 2;
    }
    
    #search-input {
        width: 100%;
    }
    
    #sql-container {
        height: 0;
        overflow: hidden;
        background: $panel;
        border: solid $primary;
    }
    
    #sql-container.visible {
        height: auto;
        padding: 1 2;
    }
    
    #sql-input {
        width: 100%;
        height: 5;
    }
    
    #sql-result {
        height: 1fr;
        margin-top: 1;
    }
    
    #about-container {
        display: none;
    }
    
    #about-container.visible {
        display: block;
        width: 100%;
        height: 100%;
        align: center middle;
        layer: overlay;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("ctrl+s", "toggle_search", "Search"),
        ("ctrl+p", "show_procedures", "Procedures"),
        ("ctrl+k", "show_packages", "Packages"),
        ("ctrl+e", "toggle_sql_editor", "SQL"),
        ("ctrl+y", "copy_to_clipboard", "Copy"),
        ("tab", "focus_next", "Next"),
        ("shift+tab", "focus_previous", "Previous"),
        ("f1", "toggle_about", "About"),
        ("escape", "cancel_action", "Close/Cancel"),
    ]

    is_loading = reactive(False)

    def __init__(self, config: ConnectionConfig, row_limit: int = 50, debug: bool = False):
        super().__init__()
        self.config = config
        self.row_limit = row_limit
        self.debug_mode = debug
        self.conn = None
        self.schemas: List[str] = []
        self.active_schema = db.normalize_identifier(config.schema)
        self.active_filters = {opt for opt, _, default in FILTER_OPTIONS if default}
        self.detail_task: Optional[asyncio.Task] = None
        self.error_panel = Static("", id="error-panel")
        self.filter_id_to_type: Dict[str, str] = {
            sanitize_object_type_id(object_type): object_type for object_type, _, _ in FILTER_OPTIONS
        }
        # Cache for fast filtering
        self.all_objects_cache: List[ExplorerItem] = []
        # Track selected item
        self.selected_item: Optional[ExplorerItem] = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="controls"):
            yield Select(options=[], id="schema-select", prompt="Select schema")
            with Horizontal(id="filters"):
                for object_type, label, is_default in FILTER_OPTIONS:
                    filter_id = f"filter-{sanitize_object_type_id(object_type)}"
                    yield Checkbox(
                        label,
                        value=is_default,
                        id=filter_id,
                    )
        with Container(id="search-container"):
            yield Input(placeholder="Search... (ESC to close)", id="search-input")
        with Container(id="sql-container"):
            yield Input(
                placeholder="Enter SQL query (SELECT * FROM table_name WHERE ...) and press Enter. ESC to close.",
                id="sql-input"
            )
            yield DataTable(id="sql-result", show_cursor=False)
        with Container(id="content"):
            yield ListView(id="object-list")
            with ContentSwitcher(id="detail-switcher"):
                yield Static("Select an object.\n\nUse ↑↓ arrow keys to navigate\nPress Ctrl+Y to copy data", id="placeholder")
                yield LoadingIndicator(id="loading")
                yield self.error_panel
                yield TableDetail(id="table-detail")
                yield CodeDetail(id="code-detail")
        with Container(id="about-container"):
            yield AboutScreen()
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#detail-switcher", ContentSwitcher).current = "loading"
        list_view = self.query_one("#object-list", ListView)
        
        try:
            # Bağlantı mesajı
            list_view.append(MessageListItem("[cyan]>> Connecting to database...[/]"))
            debug_log("Connecting to database...", self.debug_mode)
            
            await self._connect()
            debug_log("Connection established", self.debug_mode)
            
            # Şema yükleme mesajı
            list_view.clear()
            list_view.append(MessageListItem("[cyan]>> Loading schemas...[/]"))
            
            await self._populate_schemas()
            debug_log(f"Schemas loaded: {len(self.schemas)}", self.debug_mode)
            
            # Objeler yüklenecek (mesaj _refresh_object_list içinde)
            list_view.clear()
            await self._refresh_object_list()
            debug_log("Object list refreshed", self.debug_mode)
            
            # ListView'e focus ver - klavye navigasyonu için
            list_view.focus()
        except Exception as exc:  # pragma: no cover - interactive feedback
            import traceback
            error_details = traceback.format_exc()
            debug_log(f"Connection error: {exc}\n{error_details}", self.debug_mode)
            self._show_error(f"Connection failed: {exc}\n\nDetails:\n{error_details}")

    async def on_unmount(self) -> None:
        if self.conn is not None:
            try:
                await asyncio.get_running_loop().run_in_executor(None, self.conn.close)
            except Exception:
                pass

    async def _connect(self) -> None:
        loop = asyncio.get_running_loop()
        self.conn = await loop.run_in_executor(None, db.create_connection, self.config)

    def action_refresh(self) -> None:
        # Cache'i temizle ve yeniden yükle
        self.all_objects_cache = []
        asyncio.create_task(self._refresh_object_list())

    async def _populate_schemas(self) -> None:
        assert self.conn is not None
        loop = asyncio.get_running_loop()
        schemas = await loop.run_in_executor(None, db.list_schemas, self.conn)
        active = db.normalize_identifier(self.config.schema)
        if active not in schemas:
            schemas.insert(0, active)
        self.schemas = schemas
        select = self.query_one("#schema-select", Select)
        select.set_options([(schema, schema) for schema in schemas])
        select.value = active
        self.active_schema = active
        select.focus()

    async def _refresh_object_list(self, search_term: str = "") -> None:
        assert self.conn is not None
        list_view = self.query_one("#object-list", ListView)
        list_view.clear()
        self.query_one("#detail-switcher", ContentSwitcher).current = "loading"

        loop = asyncio.get_running_loop()
        
        # İlk kez yükleniyorsa veya cache boşsa, tüm objeleri çek
        if not self.all_objects_cache:
            # Loading mesajı göster
            list_view.append(MessageListItem("[yellow]>> Loading tables...[/]"))
            
            all_items: List[ExplorerItem] = []
            
            # Tüm tabloları al
            table_names = await loop.run_in_executor(
                None, db.list_tables, self.conn, self.active_schema
            )
            all_items.extend(ExplorerItem(name, "TABLE") for name in table_names)
            
            # Güncel mesaj göster
            list_view.clear()
            list_view.append(MessageListItem(f"[yellow]>> {len(table_names)} tables loaded. Loading other objects...[/]"))
            
            # Diğer tüm object tiplerini al
            all_types = [opt for opt, _, _ in FILTER_OPTIONS if opt != "TABLE"]
            if all_types:
                object_info = await loop.run_in_executor(
                    None, db.list_objects_info, self.conn, self.active_schema, all_types
                )
                all_items.extend(ExplorerItem(name, object_type) for name, object_type in object_info)
            
            self.all_objects_cache = sorted(all_items, key=lambda entry: entry.name)
            
            # Loading mesajını temizle
            list_view.clear()
        
        # Cache'den filtreleme yap
        items = [
            item for item in self.all_objects_cache
            if item.object_type in self.active_filters
            and (not search_term or search_term in item.name)
        ]
        
        if items:
            # İlk yüklemede toplam sayıyı göster
            if not search_term and len(self.all_objects_cache) > 0:
                total_tables = sum(1 for item in self.all_objects_cache if item.object_type == "TABLE")
                total_others = len(self.all_objects_cache) - total_tables
                list_view.append(MessageListItem(
                    f"[green]>> Completed: {total_tables} tables, {total_others} other objects loaded[/]"
                ))
                # Kısa bir süre göster
                await asyncio.sleep(0.5)
                list_view.clear()
            
            for entry in items:
                list_view.append(ExplorerListItem(entry))
            # select first item by default
            list_view.index = 0
            self.selected_item = items[0]
            await self._load_detail(items[0])
        else:
            msg = f"[dim]No results found for '{search_term}'.[/]" if search_term else "[dim]No objects found.[/]"
            list_view.append(MessageListItem(msg))
            self.query_one("#detail-switcher", ContentSwitcher).current = "placeholder"

    async def _load_detail(self, entry: ExplorerItem) -> None:
        if self.detail_task:
            self.detail_task.cancel()
        self.detail_task = asyncio.create_task(self._load_detail_task(entry))

    async def _load_detail_task(self, entry: ExplorerItem) -> None:
        assert self.conn is not None
        switcher = self.query_one("#detail-switcher", ContentSwitcher)
        switcher.current = "loading"
        loop = asyncio.get_running_loop()

        try:
            if entry.object_type == "TABLE":
                debug_log(f"Loading table: {entry.name}", self.debug_mode)
                columns = await loop.run_in_executor(
                    None, db.describe_table, self.conn, self.active_schema, entry.name
                )
                debug_log(f"Columns loaded: {len(columns)}", self.debug_mode)
                column_names, rows = await loop.run_in_executor(
                    None,
                    db.fetch_rows,
                    self.conn,
                    self.active_schema,
                    entry.name,
                    self.row_limit,
                )
                debug_log(f"Rows loaded: {len(rows)}, columns: {len(column_names)}", self.debug_mode)
                table_detail = self.query_one("#table-detail", TableDetail)
                debug_log(f"Updating table detail widget...", self.debug_mode)
                table_detail.update_detail(columns, rows, column_names, self.debug_mode)
                debug_log(f"Setting switcher to table-detail", self.debug_mode)
                switcher.current = "table-detail"
                debug_log(f"Table detail displayed successfully", self.debug_mode)
            else:
                debug_log(f"Loading source: {entry.name} ({entry.object_type})", self.debug_mode)
                source = await loop.run_in_executor(
                    None,
                    db.fetch_source,
                    self.conn,
                    self.active_schema,
                    entry.name,
                    entry.object_type,
                )
                code_detail = self.query_one("#code-detail", CodeDetail)
                code_detail.show_source(entry.name, entry.object_type, source)
                switcher.current = "code-detail"
                debug_log(f"Source code displayed successfully", self.debug_mode)
        except asyncio.CancelledError:
            debug_log(f"Load detail task was cancelled", self.debug_mode)
            raise
        except Exception as exc:  # pragma: no cover - interactive feedback
            import traceback
            error_details = traceback.format_exc()
            debug_log(f"ERROR: {exc}\n{error_details}", self.debug_mode)
            self._show_error(f"Hata: {exc}\n\nDetaylar:\n{error_details[:500]}")
        finally:
            self.detail_task = None

    def _show_error(self, message: str) -> None:
        self.error_panel.update(f"[red]{message}[/]")
        self.query_one("#detail-switcher", ContentSwitcher).current = "error-panel"

    async def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "schema-select":
            return
        if event.value is None:
            return
        new_schema = db.normalize_identifier(event.value)
        if new_schema == self.active_schema:
            return
        self.active_schema = new_schema
        # Şema değişti, cache'i temizle
        self.all_objects_cache = []
        await self._refresh_object_list()

    async def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        checkbox_id = event.checkbox.id or ""
        if not checkbox_id.startswith("filter-"):
            return
        sanitized = checkbox_id[len("filter-") :]
        object_type = self.filter_id_to_type.get(sanitized)
        if not object_type:
            return
        if event.value:
            self.active_filters.add(object_type)
        else:
            self.active_filters.discard(object_type)
        await self._refresh_object_list()

    async def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        if isinstance(item, ExplorerListItem):
            self.selected_item = item.entry
            await self._load_detail(item.entry)

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, ExplorerListItem):
            self.selected_item = item.entry
            await self._load_detail(item.entry)
    
    def action_toggle_search(self) -> None:
        """Toggle search input visibility."""
        search_container = self.query_one("#search-container", Container)
        search_input = self.query_one("#search-input", Input)
        
        if search_container.has_class("visible"):
            search_container.remove_class("visible")
        else:
            search_container.add_class("visible")
            search_input.focus()
            search_input.value = ""
    
    def action_cancel_action(self) -> None:
        """Hide search input, SQL editor, and about screen."""
        search_container = self.query_one("#search-container", Container)
        search_input = self.query_one("#search-input", Input)
        sql_container = self.query_one("#sql-container", Container)
        sql_input = self.query_one("#sql-input", Input)
        about_container = self.query_one("#about-container", Container)
        
        if about_container.has_class("visible"):
            about_container.remove_class("visible")
            return
        
        if search_container.has_class("visible"):
            search_container.remove_class("visible")
            search_input.value = ""
            asyncio.create_task(self._refresh_object_list())
        
        if sql_container.has_class("visible"):
            sql_container.remove_class("visible")
            sql_input.value = ""
    
    def action_toggle_about(self) -> None:
        """Toggle about screen visibility."""
        about_container = self.query_one("#about-container", Container)
        
        if about_container.has_class("visible"):
            about_container.remove_class("visible")
        else:
            # Diğer panelleri kapat
            search_container = self.query_one("#search-container", Container)
            sql_container = self.query_one("#sql-container", Container)
            
            if search_container.has_class("visible"):
                search_container.remove_class("visible")
            if sql_container.has_class("visible"):
                sql_container.remove_class("visible")
            
            # About ekranını aç
            about_container.add_class("visible")
    
    def action_copy_to_clipboard(self) -> None:
        """Copy selected object data to clipboard in markdown format."""
        if not self.selected_item:
            self.notify("No object selected", severity="warning", timeout=3)
            return
        
        # Async task olarak çalıştır
        asyncio.create_task(self._copy_selected_object())
    
    async def _copy_selected_object(self) -> None:
        """Copy the selected object's data to clipboard."""
        if not self.selected_item:
            return
        
        try:
            assert self.conn is not None
            loop = asyncio.get_running_loop()
            
            if self.selected_item.object_type == "TABLE":
                # Tablo için: yapı + veriler
                columns = await loop.run_in_executor(
                    None, db.describe_table, self.conn, self.active_schema, self.selected_item.name
                )
                column_names, rows = await loop.run_in_executor(
                    None, db.fetch_rows, self.conn, self.active_schema, self.selected_item.name, self.row_limit
                )
                
                # Markdown formatında oluştur
                output = []
                output.append(f"# Table: {self.active_schema}.{self.selected_item.name}")
                output.append("")
                output.append("## Structure")
                output.append("")
                output.append("| Column | Type | Length | Precision | Scale | Nullable | Default |")
                output.append("|--------|------|--------|-----------|-------|----------|---------|")
                
                for (_, col_name, data_type, data_length, data_precision, data_scale, nullable, data_default) in columns:
                    output.append(
                        f"| {col_name} | {data_type} | {data_length or ''} | "
                        f"{data_precision or ''} | {data_scale or ''} | {nullable} | {(data_default or '').strip()} |"
                    )
                
                output.append("")
                output.append(f"## Sample Data (first {min(len(rows), self.row_limit)} rows)")
                output.append("")
                
                if rows:
                    # Header
                    output.append("| " + " | ".join(column_names) + " |")
                    output.append("| " + " | ".join(["---"] * len(column_names)) + " |")
                    
                    # Rows
                    for row in rows:
                        formatted_row = []
                        for value in row:
                            if value is None:
                                formatted_row.append("NULL")
                            elif isinstance(value, bytes):
                                try:
                                    formatted_row.append(value.decode('utf-8')[:50])
                                except:
                                    formatted_row.append(f"<binary: {len(value)} bytes>")
                            else:
                                formatted_row.append(str(value).replace("|", "\\|").replace("\n", " ")[:100])
                        output.append("| " + " | ".join(formatted_row) + " |")
                else:
                    output.append("*No data*")
                
                markdown_text = "\n".join(output)
                
            else:
                # PL/SQL objesi için: kaynak kodu
                source = await loop.run_in_executor(
                    None, db.fetch_source, self.conn, self.active_schema, 
                    self.selected_item.name, self.selected_item.object_type
                )
                
                output = []
                output.append(f"# {self.selected_item.object_type}: {self.active_schema}.{self.selected_item.name}")
                output.append("")
                output.append("```sql")
                output.append(source.strip())
                output.append("```")
                
                markdown_text = "\n".join(output)
            
            # Clipboard'a kopyala - Textual'ın built-in özelliği
            import pyperclip
            pyperclip.copy(markdown_text)
            
            self.notify(
                f"✓ Copied {self.selected_item.name} to clipboard",
                severity="information",
                timeout=3
            )
            
        except ImportError:
            # pyperclip yoksa uyarı ver
            self.notify(
                "pyperclip not installed. Run: pip install pyperclip",
                severity="error",
                timeout=5
            )
        except Exception as exc:
            self.notify(f"Copy failed: {exc}", severity="error", timeout=5)
    
    def action_show_procedures(self) -> None:
        """Show only procedures."""
        # Tüm filtreleri kapat
        for object_type, _, _ in FILTER_OPTIONS:
            filter_id = f"filter-{sanitize_object_type_id(object_type)}"
            checkbox = self.query_one(f"#{filter_id}", Checkbox)
            checkbox.value = False
        
        # Sadece PROCEDURE'ü aç
        procedure_checkbox = self.query_one("#filter-procedure", Checkbox)
        procedure_checkbox.value = True
    
    def action_show_packages(self) -> None:
        """Show only packages."""
        # Tüm filtreleri kapat
        for object_type, _, _ in FILTER_OPTIONS:
            filter_id = f"filter-{sanitize_object_type_id(object_type)}"
            checkbox = self.query_one(f"#{filter_id}", Checkbox)
            checkbox.value = False
        
        # PACKAGE ve PACKAGE BODY'yi aç
        package_checkbox = self.query_one("#filter-package", Checkbox)
        package_checkbox.value = True
        package_body_checkbox = self.query_one("#filter-package-body", Checkbox)
        package_body_checkbox.value = True
    
    async def on_input_changed(self, event: Input.Changed) -> None:
        """Filter objects based on search input - using cache for instant filtering."""
        if event.input.id == "search-input":
            search_term = event.value.strip().upper()
            # Cache'den anında filtrele
            await self._refresh_object_list(search_term=search_term)
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Execute SQL query when Enter is pressed."""
        if event.input.id != "sql-input":
            return
        
        sql_query = event.value.strip()
        if not sql_query:
            return
        
        # SQL çalıştır
        await self._execute_sql(sql_query)
    
    def action_toggle_sql_editor(self) -> None:
        """Toggle SQL editor visibility."""
        sql_container = self.query_one("#sql-container", Container)
        sql_input = self.query_one("#sql-input", Input)
        sql_result = self.query_one("#sql-result", DataTable)
        
        if sql_container.has_class("visible"):
            sql_container.remove_class("visible")
            sql_input.value = ""
            sql_result.clear(columns=True)
        else:
            # Diğerlerini kapat
            search_container = self.query_one("#search-container", Container)
            if search_container.has_class("visible"):
                search_container.remove_class("visible")
            
            sql_container.add_class("visible")
            
            # Seçili item bir tablo ise otomatik SQL oluştur
            if self.selected_item and self.selected_item.object_type == "TABLE":
                sql_query = f"SELECT * FROM {self.active_schema}.{self.selected_item.name} WHERE ROWNUM <= 50"
                sql_input.value = sql_query
            else:
                sql_input.value = ""
            
            sql_input.focus()
            sql_result.clear(columns=True)
    
    async def _execute_sql(self, sql_query: str) -> None:
        """Execute SQL query and display results."""
        assert self.conn is not None
        sql_result = self.query_one("#sql-result", DataTable)
        sql_result.clear(columns=True)
        
        try:
            loop = asyncio.get_running_loop()
            
            # SQL'i arka planda çalıştır
            def run_query():
                with self.conn.cursor() as cursor:
                    cursor.execute(sql_query)
                    # Kolon adlarını al
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    # Sonuçları al (max 1000 satır)
                    rows = cursor.fetchmany(1000)
                    return columns, rows
            
            columns, rows = await loop.run_in_executor(None, run_query)
            
            if columns:
                # Kolonları ekle
                sql_result.add_columns(*columns)
                
                # Satırları ekle
                for row in rows:
                    def format_value(value):
                        if value is None:
                            return "NULL"
                        elif isinstance(value, bytes):
                            try:
                                return value.decode('utf-8')
                            except UnicodeDecodeError:
                                return f"<binary: {len(value)} bytes>"
                        else:
                            return str(value)
                    
                    sql_result.add_row(*(format_value(v) for v in row))
                
                # Cursor ve zebra stilini ayarla
                sql_result.cursor_type = "row"
                sql_result.zebra_stripes = True
            else:
                # DDL/DML komutları için
                sql_result.add_column("Sonuç")
                sql_result.add_row("Sorgu başarıyla çalıştırıldı")
                
        except Exception as exc:
            # Hata durumunda
            sql_result.clear(columns=True)
            sql_result.add_column("Hata")
            sql_result.add_row(str(exc))
