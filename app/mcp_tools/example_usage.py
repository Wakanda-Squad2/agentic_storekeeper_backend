"""Example usage of MCP tools.

This demonstrates how to use the OCR, FileSystem, and Database tools.
"""

from app.mcp_tools import OCRTool, FileSystemTool, DatabaseQueryTool
from app.database import SessionLocal


def example_ocr_tool():
    """Example: Using OCR tool to extract text from an image or PDF."""
    print("=== OCR Tool Example ===")

    # Example 1: OCR on an image
    try:
        result = OCRTool.run({
            "file_path": "/path/to/receipt.jpg",
            "file_type": "jpg"
        })
        print(f"OCR Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: OCR on a PDF
    try:
        result = OCRTool.run({
            "file_path": "/path/to/document.pdf",
            "file_type": "pdf"
        })
        print(f"PDF OCR Result: {result}")
    except Exception as e:
        print(f"Error: {e}")


def example_filesystem_tool():
    """Example: Using FileSystem tool to store and read files."""
    print("\n=== FileSystem Tool Example ===")

    tenant_id = 1

    # Example 1: Store a text file
    result = FileSystemTool.run({
        "action": "store_file",
        "tenant_id": tenant_id,
        "file_path": "notes/document_analysis.txt",
        "content": "This document contains transaction details..."
    })
    print(f"Store file result: {result}")

    # Example 2: Read a file
    result = FileSystemTool.run({
        "action": "read_file",
        "tenant_id": tenant_id,
        "file_path": "notes/document_analysis.txt"
    })
    print(f"Read file result: {result}")

    # Example 3: Store JSON data
    json_data = {
        "extracted_data": {
            "total_amount": 1500.00,
            "vendor": "Office Supplies Inc.",
            "date": "2026-04-01",
            "items": ["Paper", "Pens", "Staples"]
        }
    }
    result = FileSystemTool.run({
        "action": "store_json",
        "tenant_id": tenant_id,
        "file_path": "data/extracted/invoice_001.json",
        "data": json_data
    })
    print(f"Store JSON result: {result}")

    # Example 4: Read JSON data
    result = FileSystemTool.run({
        "action": "read_json",
        "tenant_id": tenant_id,
        "file_path": "data/extracted/invoice_001.json"
    })
    print(f"Read JSON result: {result}")


def example_database_tool():
    """Example: Using DatabaseQuery tool to query financial data."""
    print("\n=== Database Query Tool Example ===")

    # Get a database session
    db = SessionLocal()

    try:
        # Example 1: List transactions
        result = DatabaseQueryTool.run({
            "query_type": "list_transactions",
            "filters": {
                "tenant_id": 1,
                "start_date": "2026-04-01",
                "end_date": "2026-04-30",
                "transaction_type": "expense"
            },
            "limit": 50,
            "offset": 0
        }, db)
        print(f"List transactions: {result}")

        # Example 2: Sum by category
        result = DatabaseQueryTool.run({
            "query_type": "sum_by_category",
            "filters": {
                "tenant_id": 1,
                "start_date": "2026-01-01",
                "end_date": "2026-12-31"
            }
        }, db)
        print(f"Sum by category: {result}")

        # Example 3: Monthly totals
        result = DatabaseQueryTool.run({
            "query_type": "monthly_totals",
            "filters": {
                "tenant_id": 1,
                "transaction_type": "income"
            }
        }, db)
        print(f"Monthly totals: {result}")

        # Example 4: Vendor breakdown
        result = DatabaseQueryTool.run({
            "query_type": "vendor_breakdown",
            "filters": {
                "tenant_id": 1,
                "start_date": "2026-04-01",
                "end_date": "2026-04-30"
            },
            "limit": 10
        }, db)
        print(f"Vendor breakdown: {result}")

        # Example 5: Pending invoices
        result = DatabaseQueryTool.run({
            "query_type": "pending_invoices",
            "filters": {
                "tenant_id": 1
            },
            "limit": 20
        }, db)
        print(f"Pending invoices: {result}")

    finally:
        db.close()


def helper_methods_example():
    """Example: Using helper methods for convenience."""
    print("\n=== Helper Methods Example ===")

    tenant_id = 1

    # Using helper methods instead of run()
    result = FileSystemTool.store_json(
        tenant_id=tenant_id,
        file_path="test/config.json",
        data={"theme": "dark", "language": "en"}
    )
    print(f"Store JSON via helper: {result}")

    result = FileSystemTool.read_json(
        tenant_id=tenant_id,
        file_path="test/config.json"
    )
    print(f"Read JSON via helper: {result}")


if __name__ == "__main__":
    print("MCP Tools Examples\n")

    # Run examples
    example_ocr_tool()
    example_filesystem_tool()
    example_database_tool()
    helper_methods_example()

    print("\n=== All examples completed ===")
