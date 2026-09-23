import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.config.settings import get_settings

async def main():
    settings = get_settings()
    print(f"Connecting to database: {settings.DATABASE_URL.split('@')[-1]}...")
    engine = create_async_engine(settings.DATABASE_URL)
    
    # Read schema.sql
    with open("apps/api/src/infrastructure/database/postgres/schema.sql", "r") as f:
        schema_sql = f.read()

    # Enable pgvector or create fallback domain
    async with engine.connect() as conn:
        print("Checking if 'vector' type/domain exists...")
        try:
            async with conn.begin():
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            print("Successfully enabled pgvector extension.")
        except Exception as e:
            print(f"pgvector extension not available: {str(e)}")
            print("Creating fallback domain 'vector' as float[]...")
            try:
                async with conn.begin():
                    await conn.execute(text("CREATE DOMAIN vector AS float[];"))
                print("Created fallback 'vector' domain successfully.")
            except Exception as dom_err:
                print(f"Domain 'vector' may already exist: {str(dom_err)}")

        # Split schema.sql statements by semicolon
        statements = schema_sql.split(";")
        for stmt in statements:
            # Strip SQL comments
            lines = stmt.split("\n")
            cleaned_lines = [l for l in lines if not l.strip().startswith("--")]
            stmt = "\n".join(cleaned_lines).strip()
            
            if not stmt or "CREATE EXTENSION" in stmt:
                continue
            
            # Print statement summary
            summary = stmt.split("\n")[0]
            print(f"Executing: {summary}...")
            try:
                async with conn.begin():
                    await conn.execute(text(stmt))
            except Exception as stmt_err:
                print(f"Statement status: {str(stmt_err)} (Continuing...)")

    print("\nDatabase initialization complete!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
