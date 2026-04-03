import asyncio
from services.openai_service import OpenAIService

async def test():
    service = OpenAIService()
    try:
        qs = await service.generate_questions("Frontend Developer", ["tr"], "Entry Level", "Test", "test@test.com", "Resume text: React, Node, Python")
        print("GENERATED:", qs)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(test())
