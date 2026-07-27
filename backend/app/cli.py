import asyncio
import sys
import argparse
from app.database import init_db, AsyncSessionLocal
from app.services.generator_service import GeneratorService
from app.sources.registry import source_registry

async def main():
    parser = argparse.ArgumentParser(description="Automated LinkedIn Tech Post Generator CLI")
    parser.add_argument("--tone", default="professional", choices=["professional", "founder", "developer", "investor"], help="Tone of the LinkedIn post")
    parser.add_argument("--source", default="hacker_news", help="Source name (default: hacker_news)")
    parser.add_argument("--story-id", default=None, help="Specific story ID to generate post for")
    
    args = parser.parse_args()

    print("Initializing Database...")
    await init_db()

    print(f"Fetching top story from source '{args.source}'...")
    async with AsyncSessionLocal() as db:
        try:
            res = await GeneratorService.generate_post_pipeline(
                db=db,
                story_id=args.story_id,
                source_name=args.source,
                tone=args.tone
            )
            print("\n=======================================================")
            print("LINKEDIN POST GENERATED SUCCESSFULLY!")
            print("=======================================================")
            print(f"Title: {res.title}")
            print(f"Tone: {res.tone}")
            print(f"Word Count: {res.word_count}")
            print(f"Output Directory: {res.output_folder}")
            print("\n--- CAPTION PREVIEW ---")
            print(res.linkedin_caption)
            print("\n--- HASHTAGS ---")
            print(" ".join(res.hashtags))
            print("=======================================================\n")
        except Exception as e:
            print(f"Error generating post: {e}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
