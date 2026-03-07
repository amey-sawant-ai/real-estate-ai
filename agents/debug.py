import os
from groq import Groq
import json

location = "Bandra West Mumbai"
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = f'''Extract the primary city name and country name from this location string: "{location}".
Return ONLY a valid JSON object in this exact format, nothing else:
{{"city": "...", "country": "..."}}'''
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )
    result = json.loads(completion.choices[0].message.content)
    print(result.get("city", "NOTFOUND"), result.get("country", "NOTFOUND"))
except Exception as e:
    print("ERROR:", e)
