from mcp.server.fastmcp import FastMCP
import json
import os
import sys

# Ensure backend root is in pythonpath
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.vector_store import get_vector_store

# Create the MCP Server
mcp = FastMCP("NYAYA-VAANI-MCP")

@mcp.tool()
def search_legal_codes(query: str, domain: str = "ipc") -> str:
    """
    Search Indian legal codes (IPC, BSA) for relevant statutes using dense vector embeddings.
    
    Args:
        query: The criminal act, offense, or legal topic to search for (e.g., "stole a bicycle").
        domain: Which code to search, "ipc" (Indian Penal Code) or "bsa" (BNS). Default is ipc.
    """
    try:
        store = get_vector_store()
        results = store.search(collection_name=domain.lower(), query=query, top_k=3)
        
        if not results:
            return f"No relevant legal codes found in {domain} for query '{query}'."
            
        formatted = f"Top Legal Matches from {domain.upper()}:\n"
        for r in results:
            formatted += f"- Section {r.get('Section')}: {r.get('Description')} (Score: {r.get('score', 0):.2f})\n"
        return formatted
    except Exception as e:
        return f"Error executing legal search: {str(e)}"

@mcp.tool()
def get_civic_updates() -> str:
    """
    Retrieves the latest government procedural updates and news related to civic services.
    Includes deadlines and changes.
    """
    try:
        updates_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "procedure_updates.json")
        if not os.path.exists(updates_path):
            return "No recent civic updates available in the system."
            
        with open(updates_path, "r") as f:
            data = json.load(f)
            
        updates = data.get("updates", [])
        if not updates:
            return "No recent updates found."
            
        text = f"Latest Civic Updates (As of {data.get('last_checked', 'Unknown')}):\n"
        for idx, u in enumerate(updates, start=1):
            text += f"{idx}. {u.get('title')} ({u.get('date')}): {u.get('details')}\n"
        return text
    except Exception as e:
        return f"Error fetching civic updates: {str(e)}"

@mcp.tool()
def get_required_documents(service_name: str) -> str:
    """
    Retrieves the list of exact identity and proof documents required to apply for a specific civic service.
    
    Args:
        service_name: E.g., "Aadhaar Registration", "Passport Renewal", "Income Certificate"
    """
    try:
        akshaya_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "akshaya_services.json")
        if not os.path.exists(akshaya_path):
            return "Central civic services database is unavailable."
            
        with open(akshaya_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        services = data.get("services", {})
        
        # Simple naive search for tool demonstration
        for s_id, s_info in services.items():
            if service_name.lower() in s_info.get("name", "").lower():
                docs = s_info.get("required_docs", s_info.get("required_info", []))
                return f"Required Documents for {s_info.get('name')}:\n- " + "\n- ".join(docs)
                
        return f"Could not find exact requirements for service '{service_name}'. Please be more specific."
    except Exception as e:
        return f"Error opening services database: {str(e)}"

if __name__ == "__main__":
    # Standard MCP initialization bridging this wrapper to transport
    mcp.run()
