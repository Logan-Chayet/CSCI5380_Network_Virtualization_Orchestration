def ask2():
    answer = ""
    if request.method == "POST":
        user_question = request.form["question"]
        print(user_question)
        try:
            df = pd.read_csv("cisco_snmp_health_test.csv")

            # Keep last 50 entries for faster response
            recent_data = df.tail(50).to_dict(orient="records")

            # Create the prompt
            prompt = f"""You are a network assistant.
Here is recent SNMP health data from routers:
{recent_data}

Answer the following question based on the data:
{user_question}
"""

            # Call local Ollama model
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "tinyllama",  # or "llama3", etc.
                    "prompt": prompt,
                    "stream": False
                }
            )
            print(answer)
            if response.status_code == 200:
                result = response.json()
                answer = result["response"]
            else:
                answer = f"Error from LLM API: {response.text}"

        except Exception as e:
            answer = f"Error processing your question: {e}"
    print(answer)
    return render_template("ask2.html", answer=answer)

