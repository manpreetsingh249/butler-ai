import google.generativeai as genai
from groq import Groq
import config

def ask_gemini(prompt: str, system: str = "") -> str:
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        model    = genai.GenerativeModel("gemini-1.5-flash",
                       system_instruction=system or "You are a helpful expert assistant.")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Gemini error: {str(e)[:80]}]"

def ask_groq(prompt: str, system: str = "") -> str:
    try:
        groq_client = Groq(api_key=config.GROQ_API_KEY)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages, max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Groq error: {str(e)[:80]}]"

def get_best_answer(question: str, context: str = "") -> dict:
    system = f"You are an expert assistant. Be accurate, detailed, and helpful.{chr(10) + 'Context: ' + context if context else ''}"
    gemini_ans = ask_gemini(question, system)
    groq_ans   = ask_groq(question, system)
    judge_prompt = f"""You are the Judge. Two AIs answered this question. Combine the best parts into ONE perfect answer.

QUESTION: {question}

AI-A (Gemini): {gemini_ans}

AI-B (Llama): {groq_ans}

Output only the final best answer, nothing else:"""
    master = ask_groq(judge_prompt)
    return {"master": master, "gemini": gemini_ans, "groq": groq_ans}
