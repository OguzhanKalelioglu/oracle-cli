#!/usr/bin/env python3
"""
Oracle-CLI MCP Server
MCP (Model Context Protocol) sunucusu - AI araçlarının Oracle veritabanına erişimini sağlar.
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any, Optional, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from . import db
from .config import load_config
from .db import ConnectionConfig


# Global connection - server başlatıldığında oluşturulur
_connection: Optional[Any] = None
_config: Optional[ConnectionConfig] = None


async def initialize_connection() -> None:
    """Veritabanı bağlantısını başlat."""
    global _connection, _config
    
    # Config dosyasından bilgileri yükle
    _config = load_config()
    if not _config:
        raise RuntimeError(
            "Oracle bağlantı bilgileri bulunamadı. "
            "Lütfen önce 'oracle-cli configure' komutunu çalıştırın."
        )
    
    # Bağlantıyı oluştur
    loop = asyncio.get_running_loop()
    _connection = await loop.run_in_executor(
        None, db.create_connection, _config
    )


async def close_connection() -> None:
    """Veritabanı bağlantısını kapat."""
    global _connection
    if _connection:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _connection.close)
        _connection = None


def get_connection() -> Any:
    """Mevcut bağlantıyı döndür."""
    if not _connection:
        raise RuntimeError("Veritabanı bağlantısı kurulmamış.")
    return _connection


def get_config() -> ConnectionConfig:
    """Mevcut konfigürasyonu döndür."""
    if not _config:
        raise RuntimeError("Konfigürasyon yüklenmemiş.")
    return _config


# MCP Server oluştur
app = Server("oracle-cli")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """MCP araçlarını listele."""
    return [
        Tool(
            name="list_tables",
            description="Oracle şemasındaki tüm tabloları listeler",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel, varsayılan configured schema)",
                    }
                },
            },
        ),
        Tool(
            name="describe_table",
            description="Tablonun yapısını (kolonlar, tipler, constraints) gösterir",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="query_table",
            description="Tablodan örnek veri getirir (ilk N satır)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maksimum satır sayısı (varsayılan: 10)",
                        "default": 10,
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="execute_sql",
            description="Özel SQL sorgusu çalıştırır (SELECT sorguları)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL sorgusu (sadece SELECT)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maksimum satır sayısı (varsayılan: 100)",
                        "default": 100,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="list_objects",
            description="Şemadaki PL/SQL objelerini listeler (packages, procedures, functions)",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_type": {
                        "type": "string",
                        "description": "Obje tipi: PACKAGE, PROCEDURE, FUNCTION, PACKAGE BODY",
                        "enum": ["PACKAGE", "PROCEDURE", "FUNCTION", "PACKAGE BODY"],
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["object_type"],
            },
        ),
        Tool(
            name="get_source",
            description="PL/SQL objesinin kaynak kodunu getirir",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Obje adı",
                    },
                    "object_type": {
                        "type": "string",
                        "description": "Obje tipi",
                        "enum": ["PACKAGE", "PROCEDURE", "FUNCTION", "PACKAGE BODY"],
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["object_name", "object_type"],
            },
        ),
        Tool(
            name="get_table_stats",
            description="Tablo istatistiklerini getirir (satır sayısı, boyut vb.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["table_name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """MCP aracını çalıştır."""
    
    conn = get_connection()
    config = get_config()
    loop = asyncio.get_running_loop()
    
    # Schema parametresini al veya varsayılanı kullan
    schema = arguments.get("schema", config.schema)
    schema = db.normalize_identifier(schema)
    
    try:
        if name == "list_tables":
            tables = await loop.run_in_executor(
                None, db.list_tables, conn, schema
            )
            result = {
                "schema": schema,
                "tables": tables,
                "count": len(tables),
            }
            return [
                TextContent(
                    type="text",
                    text=f"**Schema: {schema}**\n\nToplamda {len(tables)} tablo bulundu:\n\n" + 
                         "\n".join(f"- {table}" for table in tables)
                )
            ]
        
        elif name == "describe_table":
            table_name = arguments["table_name"]
            columns = await loop.run_in_executor(
                None, db.describe_table, conn, schema, table_name
            )
            
            if not columns:
                return [TextContent(type="text", text=f"Tablo bulunamadı: {table_name}")]
            
            # Markdown table formatında
            lines = [
                f"# Tablo: {schema}.{table_name.upper()}",
                "",
                "| Kolon | Tip | Uzunluk | Precision | Scale | Nullable | Varsayılan |",
                "|-------|-----|---------|-----------|-------|----------|------------|",
            ]
            
            for (
                _,
                col_name,
                data_type,
                data_length,
                data_precision,
                data_scale,
                nullable,
                data_default,
            ) in columns:
                lines.append(
                    f"| {col_name} | {data_type} | {data_length or ''} | "
                    f"{data_precision or ''} | {data_scale or ''} | {nullable} | "
                    f"{(data_default or '').strip()} |"
                )
            
            return [TextContent(type="text", text="\n".join(lines))]
        
        elif name == "query_table":
            table_name = arguments["table_name"]
            limit = arguments.get("limit", 10)
            
            column_names, rows = await loop.run_in_executor(
                None, db.fetch_rows, conn, schema, table_name, limit
            )
            
            if not rows:
                return [TextContent(type="text", text=f"Tabloda veri yok: {table_name}")]
            
            # Markdown table formatında
            lines = [
                f"# Tablo Verisi: {schema}.{table_name.upper()} (ilk {len(rows)} satır)",
                "",
                "| " + " | ".join(column_names) + " |",
                "| " + " | ".join(["---"] * len(column_names)) + " |",
            ]
            
            for row in rows:
                formatted_row = []
                for value in row:
                    if value is None:
                        formatted_row.append("NULL")
                    else:
                        # Uzun değerleri kısalt
                        str_val = str(value).replace("|", "\\|").replace("\n", " ")
                        formatted_row.append(str_val[:100])
                lines.append("| " + " | ".join(formatted_row) + " |")
            
            return [TextContent(type="text", text="\n".join(lines))]
        
        elif name == "execute_sql":
            query = arguments["query"]
            limit = arguments.get("limit", 100)
            
            # Güvenlik: Sadece SELECT sorgularına izin ver
            query_upper = query.strip().upper()
            if not query_upper.startswith("SELECT"):
                return [
                    TextContent(
                        type="text",
                        text="❌ Güvenlik: Sadece SELECT sorguları desteklenmektedir."
                    )
                ]
            
            # ROWNUM limiti ekle
            if "ROWNUM" not in query_upper:
                query = f"SELECT * FROM ({query}) WHERE ROWNUM <= {limit}"
            
            def run_query():
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()
                    return columns, rows
            
            columns, rows = await loop.run_in_executor(None, run_query)
            
            if not rows:
                return [TextContent(type="text", text="Sorgu sonuç döndürmedi.")]
            
            # Markdown table formatında
            lines = [
                f"# SQL Sorgu Sonucu ({len(rows)} satır)",
                "",
                f"```sql\n{query}\n```",
                "",
                "| " + " | ".join(columns) + " |",
                "| " + " | ".join(["---"] * len(columns)) + " |",
            ]
            
            for row in rows:
                formatted_row = []
                for value in row:
                    if value is None:
                        formatted_row.append("NULL")
                    else:
                        str_val = str(value).replace("|", "\\|").replace("\n", " ")
                        formatted_row.append(str_val[:100])
                lines.append("| " + " | ".join(formatted_row) + " |")
            
            return [TextContent(type="text", text="\n".join(lines))]
        
        elif name == "list_objects":
            object_type = arguments["object_type"]
            objects = await loop.run_in_executor(
                None, db.list_objects, conn, schema, [object_type]
            )
            
            result_text = f"**{object_type} objeleri (Schema: {schema})**\n\n"
            result_text += f"Toplam {len(objects)} adet bulundu:\n\n"
            result_text += "\n".join(f"- {obj}" for obj in objects)
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_source":
            object_name = arguments["object_name"]
            object_type = arguments["object_type"]
            
            source = await loop.run_in_executor(
                None, db.fetch_source, conn, schema, object_name, object_type
            )
            
            result_text = f"# {object_type}: {schema}.{object_name}\n\n```sql\n{source}\n```"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_table_stats":
            table_name = arguments["table_name"]
            
            # Tablo istatistiklerini al
            def get_stats():
                with conn.cursor() as cursor:
                    # Satır sayısı
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {db.qualified_identifier(schema, table_name)}"
                    )
                    row_count = cursor.fetchone()[0]
                    
                    # Normalize edilmiş şema ve tablo adı
                    normalized_schema = db.normalize_identifier(schema)
                    normalized_table = db.normalize_identifier(table_name)
                    
                    # Tablo boyutu (segment bilgisi) - önce user_segments dene, yoksa all_segments
                    try:
                        cursor.execute(
                            """
                            SELECT 
                                ROUND(SUM(bytes)/1024/1024, 2) as size_mb,
                                COUNT(*) as num_segments
                            FROM user_segments
                            WHERE segment_name = :table_name
                            """,
                            table_name=normalized_table
                        )
                        size_info = cursor.fetchone()
                    except:
                        # user_segments başarısız olursa all_segments dene
                        try:
                            cursor.execute(
                                """
                                SELECT 
                                    ROUND(SUM(bytes)/1024/1024, 2) as size_mb,
                                    COUNT(*) as num_segments
                                FROM all_segments
                                WHERE owner = :owner AND segment_name = :table_name
                                """,
                                owner=normalized_schema,
                                table_name=normalized_table
                            )
                            size_info = cursor.fetchone()
                        except:
                            # Segment bilgisi alınamazsa 0 döndür
                            size_info = (0, 0)
                    
                    size_mb = size_info[0] if size_info and size_info[0] else 0
                    num_segments = size_info[1] if size_info and size_info[1] else 0
                    
                    return row_count, size_mb, num_segments
            
            row_count, size_mb, num_segments = await loop.run_in_executor(None, get_stats)
            
            result_text = f"""# Tablo İstatistikleri: {schema}.{table_name.upper()}

**Satır Sayısı:** {row_count:,}
**Boyut:** {size_mb} MB
**Segment Sayısı:** {num_segments}
"""
            
            return [TextContent(type="text", text=result_text)]
        
        else:
            return [TextContent(type="text", text=f"Bilinmeyen araç: {name}")]
    
    except Exception as exc:
        import traceback
        error_detail = traceback.format_exc()
        return [
            TextContent(
                type="text",
                text=f"❌ Hata: {str(exc)}\n\nDetay:\n```\n{error_detail}\n```"
            )
        ]


async def main():
    """MCP sunucusunu başlat."""
    
    # Bağlantıyı başlat
    await initialize_connection()
    
    try:
        # stdio üzerinden MCP sunucusunu çalıştır
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        # Temizlik
        await close_connection()


def run_mcp_server():
    """MCP sunucusunu çalıştır (CLI entry point)."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMCP sunucusu durduruldu.", file=sys.stderr)
    except Exception as exc:
        print(f"MCP sunucu hatası: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_mcp_server()
