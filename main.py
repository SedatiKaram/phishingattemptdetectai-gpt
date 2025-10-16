import asyncio, json, sys
from rich import print as rprint
from app.llm_client import get_llm_client
from app.pipeline import run_pipeline

async def main():
    if len(sys.argv) != 2:
        rprint("[bold red]Usage:[/bold red] python main.py path/to/email.json")
        sys.exit(1)

    email_path = sys.argv[1]
    email = json.loads(open(email_path, "r", encoding="utf-8").read())

    llm = get_llm_client()
    result = await run_pipeline(llm, email)
    rprint(result.model_dump())

if __name__ == "__main__":
    asyncio.run(main())
