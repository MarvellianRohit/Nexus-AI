from langchain.tools import tool
import os

class AgentTools:
    @tool("Write File")
    def write_file(file_path: str, content: str):
        """Writes content to a file at the specified path. Use this to save code, tests, or reports."""
        try:
            # Ensure directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(file_path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    @tool("Read File")
    def read_file(file_path: str):
        """Reads the content of a file."""
        try:
            if not os.path.exists(file_path):
                return "File not found."
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    @tool("List Directory")
    def list_dir(path: str = "."):
        """Lists files in a directory."""
        try:
            return str(os.listdir(path))
        except Exception as e:
            return f"Error listing directory: {str(e)}"
