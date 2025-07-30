from app.core.rag_pipeline import run_rag_query

print("🚀 Testing all personas...")
print("=" * 50)

personas = ['budget_student', 'power_user', 'general']
question = 'Is this worth buying?'
product = 'Gaming Laptop'

for persona in personas:
    print(f"\n--- {persona.upper()} PERSONA ---")
    try:
        result = run_rag_query(product, question, persona)
        answer_length = len(result["answer"])
        word_count = len(result["answer"].split())
        
        print(f'✅ Success!')
        print(f'📏 Length: {answer_length} chars, {word_count} words')
        print(f'⏱️ Time: {result["execution_time"]:.2f}s')
        print(f'📚 Sources: {len(result["sources"])}')
        print(f'🎭 Persona used: {result["persona_used"]}')
        print(f'💬 Preview: {result["answer"][:100]}...')
        
    except Exception as e:
        print(f'❌ Error: {e}')

print("\n" + "=" * 50)
print("✅ All persona tests completed!")
