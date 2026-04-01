import os
import json
from typing import Dict, Any, Union
from pathlib import Path


class FileSystemTool:
    """File system tool for storing and reading files scoped by tenant_id."""

    name = "filesystem_tool"
    description = "Store and read files under storage/ directory scoped by tenant_id"

    input_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["store_file", "read_file", "store_json", "read_json"],
                "description": "Action to perform"
            },
            "tenant_id": {
                "type": "integer",
                "description": "Tenant ID for scoping"
            },
            "file_path": {
                "type": "string",
                "description": "Path to the file relative to tenant directory"
            },
            "content": {
                "type": "string",
                "description": "Content to store (for store_file)"
            },
            "data": {
                "type": "object",
                "description": "JSON data to store (for store_json)"
            }
        },
        "required": ["action", "tenant_id", "file_path"]
    }

    @staticmethod
    def _get_tenant_path(tenant_id: int) -> Path:
        """Get the tenant-specific directory path."""
        return Path(f"storage/{tenant_id}")

    @staticmethod
    def _ensure_tenant_directory(tenant_id: int) -> Path:
        """Ensure tenant directory exists and return its path."""
        tenant_path = FileSystemTool._get_tenant_path(tenant_id)
        tenant_path.mkdir(parents=True, exist_ok=True)
        return tenant_path

    @staticmethod
    def _get_full_path(tenant_id: int, file_path: str) -> Path:
        """Get full path to file."""
        tenant_path = FileSystemTool._ensure_tenant_directory(tenant_id)
        return tenant_path / file_path

    @staticmethod
    def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute file system operation.

        Args:
            input_data: Dictionary with action, tenant_id, file_path, and optional content/data

        Returns:
            Result of the operation
        """
        action = input_data.get("action")
        tenant_id = input_data.get("tenant_id")
        file_path = input_data.get("file_path")

        if not all([action, tenant_id, file_path]):
            raise ValueError("action, tenant_id, and file_path are required")

        full_path = FileSystemTool._get_full_path(tenant_id, file_path)

        try:
            if action == "store_file":
                content = input_data.get("content")
                if content is None:
                    raise ValueError("content is required for store_file action")

                # Ensure parent directory exists
                full_path.parent.mkdir(parents=True, exist_ok=True)

                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                return {
                    "success": True,
                    "message": f"File stored at {full_path}",
                    "file_path": str(full_path)
                }

            elif action == "read_file":
                if not full_path.exists():
                    raise FileNotFoundError(f"File not found: {full_path}")

                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                return {
                    "success": True,
                    "content": content,
                    "file_path": str(full_path)
                }

            elif action == "store_json":
                data = input_data.get("data")
                if data is None:
                    raise ValueError("data is required for store_json action")

                # Ensure parent directory exists
                full_path.parent.mkdir(parents=True, exist_ok=True)

                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                return {
                    "success": True,
                    "message": f"JSON stored at {full_path}",
                    "file_path": str(full_path)
                }

            elif action == "read_json":
                if not full_path.exists():
                    raise FileNotFoundError(f"File not found: {full_path}")

                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                return {
                    "success": True,
                    "data": data,
                    "file_path": str(full_path)
                }

            else:
                raise ValueError(f"Invalid action: {action}")

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def store_file(tenant_id: int, file_path: str, content: str) -> Dict[str, Any]:
        """Helper method to store a file."""
        return FileSystemTool.run({
            "action": "store_file",
            "tenant_id": tenant_id,
            "file_path": file_path,
            "content": content
        })

    @staticmethod
    def read_file(tenant_id: int, file_path: str) -> Dict[str, Any]:
        """Helper method to read a file."""
        return FileSystemTool.run({
            "action": "read_file",
            "tenant_id": tenant_id,
            "file_path": file_path
        })

    @staticmethod
    def store_json(tenant_id: int, file_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to store JSON data."""
        return FileSystemTool.run({
            "action": "store_json",
            "tenant_id": tenant_id,
            "file_path": file_path,
            "data": data
        })

    @staticmethod
    def read_json(tenant_id: int, file_path: str) -> Dict[str, Any]:
        """Helper method to read JSON data."""
        return FileSystemTool.run({
            "action": "read_json",
            "tenant_id": tenant_id,
            "file_path": file_path
        })
