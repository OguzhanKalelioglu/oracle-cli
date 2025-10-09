import sys

if __name__ == "__main__":
    # Eğer 'mcp' argümanı varsa MCP server'ı başlat
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        from .mcp_server import main as mcp_main
        mcp_main()
    else:
        # Normal CLI modunda çalıştır
        from .cli import main
        main()
