import json
from typing import Dict, Any, List, Callable

# Import core tools functions
from tools.role_database import get_role_requirements, list_available_roles
from tools.matching_tools import normalize_skills, match_skills_to_role, find_missing_skills, rank_skill_gaps
from tools.scoring_tools import calculate_readiness_score, calculate_category_scores
from tools.roadmap_tools import create_30_day_plan
from tools.readme_tools import generate_project_readme
from tools.safety_tools import detect_fake_claim_request, honesty_check, redact_sensitive_info, validate_no_api_keys
from tools.export_tools import export_markdown_report, export_json_report

class MCPToolRegistry:
    """
    A local Model Context Protocol (MCP) style registry class.
    Exposes tool names, descriptions, schemas, and dynamic execution endpoints.
    Allows agent orchestration layers to query and call python tools deterministically.
    """
    def __init__(self) -> None:
        self.registry: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register_tool(self, name: str, description: str, func: Callable, schema: Dict[str, Any]) -> None:
        """
        Registers a tool function with validation schema and documentation metadata.
        """
        self.registry[name] = {
            "name": name,
            "description": description,
            "func": func,
            "schema": schema
        }

    def execute_tool(self, name: str, **kwargs: Any) -> Any:
        """
        Dynamic tool invocation interface. Call a tool by its registered name.
        """
        if name not in self.registry:
            raise KeyError(f"Tool '{name}' is not registered in the MCP Tool Registry.")
        return self.registry[name]["func"](**kwargs)

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Returns documentation metadata for all registered tools.
        """
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "schema": t["schema"]
            }
            for t in self.registry.values()
        ]

    def _register_default_tools(self) -> None:
        # 1. Role Database Tools
        self.register_tool(
            name="get_role_requirements",
            description="Loads the requirements schema for a specific target internship track.",
            func=get_role_requirements,
            schema={
                "type": "object",
                "properties": {
                    "role_name": {"type": "string", "description": "Name of the internship track."}
                },
                "required": ["role_name"]
            }
        )
        self.register_tool(
            name="list_available_roles",
            description="Lists all support career tracks in the database.",
            func=list_available_roles,
            schema={"type": "object", "properties": {}}
        )

        # 2. Matching Tools
        self.register_tool(
            name="normalize_skills",
            description="Sanitizes, strips, and deduplicates a list of candidate skills.",
            func=normalize_skills,
            schema={
                "type": "object",
                "properties": {
                    "skills": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["skills"]
            }
        )
        self.register_tool(
            name="match_skills_to_role",
            description="Compares student profile skills against required career track skills.",
            func=match_skills_to_role,
            schema={
                "type": "object",
                "properties": {
                    "current_skills": {"type": "array", "items": {"type": "string"}},
                    "required_skills": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["current_skills", "required_skills"]
            }
        )

        # 3. Scoring Tools
        self.register_tool(
            name="calculate_readiness_score",
            description="Computes general percentage score matching candidate profile against track.",
            func=calculate_readiness_score,
            schema={
                "type": "object",
                "properties": {
                    "current_skills": {"type": "array", "items": {"type": "string"}},
                    "required_skills": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["current_skills", "required_skills"]
            }
        )
        self.register_tool(
            name="calculate_category_scores",
            description="Evaluates subcategory scores out of 100.",
            func=calculate_category_scores,
            schema={
                "type": "object",
                "properties": {
                    "current_skills": {"type": "array", "items": {"type": "string"}},
                    "role_name": {"type": "string"},
                    "projects": {"type": "array", "items": {"type": "object"}, "default": None}
                },
                "required": ["current_skills", "role_name"]
            }
        )

        # 4. Roadmap Tools
        self.register_tool(
            name="create_30_day_plan",
            description="Constructs weekly and daily preparation task schedules.",
            func=create_30_day_plan,
            schema={
                "type": "object",
                "properties": {
                    "missing_skills": {"type": "array", "items": {"type": "string"}},
                    "target_role": {"type": "string"},
                    "hours_per_day": {"type": "number", "default": 2.0}
                },
                "required": ["missing_skills", "target_role"]
            }
        )

        # 5. Readme Tools
        self.register_tool(
            name="generate_project_readme",
            description="Assembles standard Markdown repository README templates.",
            func=generate_project_readme,
            schema={
                "type": "object",
                "properties": {
                    "project_details": {"type": "object"}
                },
                "required": ["project_details"]
            }
        )

        # 6. Safety & Audits
        self.register_tool(
            name="honesty_check",
            description="Scans profile strings to look for illogical years of experience contradictions.",
            func=honesty_check,
            schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        )
        self.register_tool(
            name="redact_sensitive_info",
            description="Masks emails and phone numbers to safeguard PII.",
            func=redact_sensitive_info,
            schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        )
        self.register_tool(
            name="validate_no_api_keys",
            description="Verifies the text does not contain sensitive high-entropy credentials.",
            func=validate_no_api_keys,
            schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        )

# Attempt to integrate with external FastMCP SDK wrapper if active
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("SkillBridgeAI")
    
    # FastMCP decorator functions
    @mcp.tool()
    def get_role_reqs(role_name: str) -> str:
        """Get requirement details for a specific internship role."""
        return json.dumps(get_role_requirements(role_name), indent=2)

    @mcp.tool()
    def check_safety(text: str) -> str:
        """Scan candidate profile text for honesty warnings and redact sensitive PII."""
        clean = redact_sensitive_info(text)
        audit = honesty_check(clean)
        return json.dumps({
            "cleaned_text": clean,
            "integrity_report": audit
        }, indent=2)

except ImportError:
    # No-op fallback
    mcp = None

if __name__ == "__main__":
    registry = MCPToolRegistry()
    print("SkillBridge AI MCP Tool Registry local registration status:")
    for tool in registry.list_tools():
        print(f" - [Registered] '{tool['name']}': {tool['description']}")
