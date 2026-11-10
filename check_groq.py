from groq import Groq 

client = Groq(
    timeout=20.0,
    max_retries=0,
)

response = client.chat.completions.create(
    model = "openai/gpt-oss-20b",
    messages = [
        {
        "role": "user",
        "content": "AI là gì ?",
        }
    ],
    max_completion_tokens=250,
)
print(response.choices[0].message.content)
