from typing import Dict,List
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
        
        
        
    def generate_analysis(
    self,
    brand: str,
    category: str,
    competitors: list,
    questions_and_responses: list
) -> dict:
        """
        Generate a brand visibility analysis based on ChatGPT's responses.

        Args:
            brand (str): Brand name
            category (str): Industry or domain
            competitors (list): List of competitors
            questions_and_responses (list): List of dicts with 'question' and 'answer' keys

        Returns:
            dict: {
                "analysis": str,
                "total_tokens": int,
                "total_cost": float
            }
        """

        def format_qa_pairs(pairs):
            return "\n\n".join([
                f"Q: {item['question']}\nA: {item['answer']}" for item in pairs
            ])

        prompt = f"""
    You are analyzing ChatGPT responses about **{brand}** (a **{category}** company).

    The user asked {len(questions_and_responses)} questions to understand how their brand appears in AI-generated answers.

    **Key competitors:** {', '.join(competitors)}

    ---

    **ChatGPT Responses to Analyze:**

    {format_qa_pairs(questions_and_responses)}

    ---

    **Your task**:
    Please analyze these responses and provide insights about:
    1. How often and in what context **{brand}** was mentioned.
    2. How **{brand}** was positioned relative to competitors.
    3. Any patterns in how ChatGPT talks about **{brand}**.
    4. Notable gaps where **{brand}** wasn't mentioned but might be expected.
    5. Overall tone and sentiment when **{brand}** is discussed.

    Keep the analysis factual and helpful for a marketing team.
    """

        messages = [{"role": "user", "content": prompt.strip()}]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )

            completion_text = response.choices[0].message.content

            prompt_cost = calculate_prompt_cost(messages, model=self.model)
            completion_cost = calculate_completion_cost(completion_text, model=self.model)
            prompt_tokens = count_message_tokens(messages, model=self.model)
            completion_tokens = count_string_tokens(completion_text, model=self.model)

            return {
                "analysis": completion_text.strip(),
                "total_tokens": prompt_tokens + completion_tokens,
                "total_cost": prompt_cost + completion_cost
            }

        except Exception as e:
            raise RuntimeError(f"OpenAI API failed to generate analysis: {str(e)}")
        
    def generate_answers_batch(self, questions: List[str]) -> Dict:
        prompt = "Provide answers (150–200 words for each question) to the following questions. Ensure the each answer is informative, well-written, and structured in a professional tone.\n\n"

        for idx, q in enumerate(questions, start=1):
            prompt += f"{idx}. {q}\n"

        prompt += "\nRespond in the same numbered format."

        messages = [{"role": "user", "content": prompt}]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )

            completion_text = response.choices[0].message.content.strip()

            # Token and cost analysis
            prompt_cost = calculate_prompt_cost(messages, model=self.model)
            completion_cost = calculate_completion_cost(completion_text, model=self.model)
            prompt_tokens = count_message_tokens(messages, model=self.model)
            completion_tokens = count_string_tokens(completion_text, model=self.model)

            # Split answers back
            raw_answers = completion_text.split("\n")
            numbered_answers = [ans for ans in raw_answers if ans.strip()]

            # Map answers to original questions
            parsed_answers = []
            for i, answer in enumerate(numbered_answers):
                parsed_answers.append({
                    "question": questions[i],
                    "answer": answer.strip()
                })

            return {
                "answers": parsed_answers,
                "total_tokens": prompt_tokens + completion_tokens,
                "total_cost": round(prompt_cost + completion_cost, 6)
            }

        except Exception as e:
            raise RuntimeError(f"OpenAI batch API failed: {str(e)}")
