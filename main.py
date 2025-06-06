import os
import openai
import time

class AIAgent:
    def __init__(self, model_name="gpt-4"):
        """
        Inicjalizacja agenta AI.
        - model_name: nazwa modelu OpenAI do generowania odpowiedzi.
        - pamięć: lista ostatnich interakcji (maxymalnie ostatnie 10 wpisów).
        """
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = model_name
        self.memory = []

    def analyze_input(self, user_input: str) -> dict:
        """
        1. Analizuje tekst użytkownika.
        2. Rozpoznaje intencję (np. czy to pytanie informacyjne, prośba o kod, wywołanie API itp.).
        3. Zwraca słownik z wynikami analizy: { "intent": str, "entities": [...] }.
        (Dla uproszczenia użyjemy modelu GPT do analizy naturalnego języka.)
        """
        prompt = (
            "Napisz JSON z kluczem 'intent' opisującym intencję użytkownika "
            "oraz 'entities' jako listę istotnych elementów. Tekst: " + user_input
        )
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Jesteś analizatorem intencji."},
                    {"role": "user", "content": prompt}
                ]
            )
            analysis = response.choices[0].message.content.strip()
            # Zakładamy, że zwrócony string to poprawny JSON.
            intent_data = None
            import json
            intent_data = json.loads(analysis)
            return intent_data
        except Exception as e:
            print(f"[Błąd analizy]: {e}")
            return {"intent": "unknown", "entities": []}

    def plan_action(self, analysis: dict) -> dict:
        """
        1. Na podstawie analizy intencji wybiera strategię działania.
        2. Zwraca plan w formie słownika, np.:
           { "action": "generate_response", "parameters": { ... } }
        3. Jeśli intencja nieznana, zwraca plan fallbackowy.
        """
        intent = analysis.get("intent", "unknown")
        if intent == "generate_info":
            return {"action": "generate_response", "parameters": {"topic": analysis["entities"]}}
        elif intent == "code_request":
            return {"action": "generate_code", "parameters": {"requirements": analysis["entities"]}}
        else:
            return {"action": "fallback", "parameters": {}}

    def execute_action(self, plan: dict, user_input: str) -> str:
        """
        Wykonuje zaplanowane działanie:
        - generate_response: wywołuje OpenAI do wygenerowania odpowiedzi informacyjnej.
        - generate_code: wywołuje OpenAI do wygenerowania fragmentu kodu.
        - fallback: zwraca komunikat o niezrozumieniu.
        """
        action = plan.get("action", "fallback")
        if action == "generate_response":
            prompt = (
                "Użytkownik pyta o: " + user_input +
                "\nProszę wygeneruj jasną, wyczerpującą odpowiedź."
            )
            try:
                resp = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "Jesteś pomocnym asystentem."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                return f"[Błąd generowania odpowiedzi]: {e}"

        elif action == "generate_code":
            prompt = (
                "Użytkownik chciałby następujący kod: " + user_input +
                "\nProszę wygeneruj poprawny, skomentowany kod w Pythonie."
            )
            try:
                resp = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "Jesteś doświadczonym programistą Python."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                return f"[Błąd generowania kodu]: {e}"

        else:
            return "Przepraszam, nie rozumiem Twojej prośby. Spróbuj sformułować pytanie inaczej."

    def update_memory(self, user_input: str, agent_output: str):
        """
        Dodaje nowe interakcje do pamięci (ostatnie 10 wpisów).
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        entry = {"time": timestamp, "user": user_input, "agent": agent_output}
        self.memory.append(entry)
        if len(self.memory) > 10:
            self.memory.pop(0)

    def run(self):
        """
        Główna pętla działania agenta:
        1. Wczytuje tekst od użytkownika.
        2. Analizuje intencję.
        3. Planowanie i wykonanie.
        4. Wyświetlenie wyniku i zapis do pamięci.
        5. Powtarza do momentu wpisania 'exit' lub 'quit'.
        """
        print("=== Witamy w prostym agencie AI. Wpisz 'exit' aby zakończyć. ===")
        while True:
            user_input = input("\nTy: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Agent: Do zobaczenia!")
                break

            analysis = self.analyze_input(user_input)
            plan = self.plan_action(analysis)
            agent_output = self.execute_action(plan, user_input)
            print(f"\nAgent: {agent_output}")

            self.update_memory(user_input, agent_output)


if __name__ == "__main__":
    agent = AIAgent(model_name="gpt-4")
    agent.run()