import os
import asyncio
import threading
import traceback
from datetime import datetime
from dotenv import load_dotenv
from autogen import AssistantAgent
from flask import Flask, render_template, request, jsonify

# Initialize Flask app
# ... existing code ...
# Add this near the top of the file after imports
from flask import Flask
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Load environment variables
load_dotenv()

# ---------- Helper: Gemini config ----------
def get_llm_config():
    if os.getenv("GEMINI_API_KEY"):
        return {
            "config_list": [{
                "model": "gemini-2.0-flash",
                "api_key": os.getenv("GEMINI_API_KEY"),
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "api_type": "google"
            }],
            "temperature": 0.7
        }
    else:
        return None

# ---------- Async helpers ----------
def _run_coro_in_new_loop(coro, timeout=None):
    def _loop_runner(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=_loop_runner, args=(new_loop,), daemon=True)
    t.start()

    future = asyncio.run_coroutine_threadsafe(coro, new_loop)
    try:
        res = future.result(timeout=timeout)
    finally:
        try:
            new_loop.call_soon_threadsafe(new_loop.stop)
            t.join(timeout=2)
        except Exception:
            pass
    return res

def run_qa_once(assistant, question, timeout: float = 60.0):
    """Ask one question and get one reply."""
    try:
        coro = assistant.a_generate_reply([{"role": "user", "content": question}])
        try:
            result = asyncio.run(coro)
        except RuntimeError:
            result = _run_coro_in_new_loop(coro, timeout=timeout)

        if isinstance(result, dict) and "content" in result:
            return result["content"]
        elif hasattr(result, "content"):
            return result.content
        else:
            return str(result)
    except Exception as e:
        tb = traceback.format_exc()
        return f"❌ Error: {str(e)[:200]}\nTraceback:\n{tb}"

# ---------- Global state ----------
qa_history = []
stats = {
    "total_questions": 0,
    "session_start": datetime.now().isoformat(),
    "last_question": None,
    "last_answer": None
}

# ---------- Main ----------
def main():
    print("🤖 AI Q&A Bot(Powered by Radicals)")
    print("Ask any question, get AI-powered answers!\n")

    llm_config = get_llm_config()
    if not llm_config:
        print("⚠️ No GEMINI_API_KEY found. Please set it in your environment.")
        return

    assistant = AssistantAgent(
        name="qa_assistant",
        llm_config=llm_config,
        system_message="You are a helpful AI assistant. Answer user questions clearly and concisely.",
        code_execution_config={"use_docker": False}
    )

    while True:
        question = input("\n Qn.>  Ask a question (or type 'exit' to quit): ").strip()
        if question.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        print("\nThinking...")
        answer = run_qa_once(assistant, question)

        print("\n💡 Answer:", answer)

        # Save history
        qa_history.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        stats["total_questions"] += 1
        stats["last_question"] = question
        stats["last_answer"] = answer

    # End of session summary
    print("\n--- SESSION SUMMARY ---")
    print(f"📝 Total Questions: {stats['total_questions']}")
    print(f"📅 Session started: {stats['session_start']}")
    for item in qa_history:
        print(f"\nQ: {item['question']}\nA: {item['answer']}")

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    llm_config = get_llm_config()
    if not llm_config:
        return jsonify({'error': 'GEMINI_API_KEY not found'}), 500

    assistant = AssistantAgent(
        name="qa_assistant",
        llm_config=llm_config,
        system_message="You are a helpful AI assistant. Answer user questions clearly and concisely.",
        code_execution_config={"use_docker": False}
    )

    answer = run_qa_once(assistant, question)
    
    # Save to history
    qa_history.append({
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    })
    stats["total_questions"] += 1
    stats["last_question"] = question
    stats["last_answer"] = answer

    return jsonify({
        'answer': answer,
        'history': qa_history,
        'stats': stats
    })

if __name__ == "__main__":
    # Use environment variable for port, defaulting to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
