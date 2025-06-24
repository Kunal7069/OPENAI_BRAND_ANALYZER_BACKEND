from typing import Dict
from openai import OpenAI
from tokencost import (
    calculate_prompt_cost,
    calculate_completion_cost,
    count_message_tokens,
    count_string_tokens
)
import json
import os
from dotenv import load_dotenv

load_dotenv()  

class BrandQuestionGenerator:
    def __init__(self, model: str = "gpt-4"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def prepare_questions__prompt(self, paragraph: str) -> str:
        return f"""
You are a smart brand awareness assistant. Given the brand description below, generate **10 unique natural-language questions** whose answers would include the brand name.

Instructions:
- Do not mention the brand name directly in the questions.
- The questions should be general and meaningful where the brand name could be the answer.
- Format the output as JSON with a single key "questions", which is a list of 10 strings.

Brand description:
\"\"\"{paragraph}\"\"\"
"""

    def generate_questions(self, paragraph: str) -> Dict:
        prompt = self.prepare_questions__prompt(paragraph)
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )

            completion_text = response.choices[0].message.content

            # Token & cost analysis
            prompt_cost = calculate_prompt_cost(messages, model=self.model)
            completion_cost = calculate_completion_cost(completion_text, model=self.model)
            prompt_tokens = count_message_tokens(messages, model=self.model)
            completion_tokens = count_string_tokens(completion_text, model=self.model)

            parsed_output = json.loads(completion_text)
            questions = parsed_output.get("questions", [])

            return {
                "questions": questions,
                "total_tokens": prompt_tokens + completion_tokens,
                "total_cost": prompt_cost + completion_cost
            }

        except json.JSONDecodeError:
            raise ValueError("OpenAI did not return valid JSON:\n" + completion_text)
        except Exception as e:
            raise RuntimeError(f"OpenAI API failed: {str(e)}")
        
        
    def generate_answer(self, question: str) -> Dict:
        prompt = f"""
Answer the following question in 150 to 200 words:

"{question}"

Ensure the response is informative, well-written, and structured in a professional tone.
"""

        messages = [{"role": "user", "content": prompt}]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )

            completion_text = response.choices[0].message.content

            # Token & cost analysis
            prompt_cost = calculate_prompt_cost(messages, model=self.model)
            completion_cost = calculate_completion_cost(completion_text, model=self.model)
            prompt_tokens = count_message_tokens(messages, model=self.model)
            completion_tokens = count_string_tokens(completion_text, model=self.model)

            return {
                "answer": completion_text.strip(),
                "total_tokens": prompt_tokens + completion_tokens,
                "total_cost": prompt_cost + completion_cost
            }

        except Exception as e:
            raise RuntimeError(f"OpenAI API failed to generate answer: {str(e)}")