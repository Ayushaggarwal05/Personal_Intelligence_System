from fastapi import APIRouter
from app.services.prompt_loader import prompt_loader

router = APIRouter(prefix="/prompts", tags=["Prompt Templates"])

@router.get("/list")
def list_prompt_templates():
    """Lists registered prompt templates categories and their required placeholders."""
    return {
        "prompts_root": prompt_loader.prompts_dir,
        "registered_templates": [
            {
                "key": key,
                "category": key.split("/")[0],
                "filename": key.split("/")[1],
                "expected_variables": vars_list
            } for key, vars_list in prompt_loader._registry.items()
        ]
    }
