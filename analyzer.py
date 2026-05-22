from database import SessionLocal
from experiment import Experiment, ExperimentResult
from openai import OpenAI
from dotenv import load_dotenv
import os
import statistics

load_dotenv()

def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_ai_quality_score(input_text: str, output_text: str) -> float:
    client = get_client()
    """Ask AI to score the quality of a response (1-5) with strict criteria"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a STRICT quality evaluator for customer support responses.
Score the response from 1.0 to 5.0 in increments of 0.5 using these exact criteria:

5.0 - EXCELLENT: Acknowledges feeling AND solves the problem clearly AND is concise (under 4 sentences)
4.5 - GREAT: Nearly excellent, minor room for improvement in tone or brevity
4.0 - GOOD: Solves the problem clearly but lacks empathy OR is slightly too long
3.5 - ABOVE AVERAGE: Helpful but noticeably robotic or a bit wordy
3.0 - AVERAGE: Addresses the issue but vague, too long, or robotic tone
2.5 - BELOW AVERAGE: Partially helpful but missing key info or feels cold
2.0 - POOR: Partially addresses the issue, dismissive or confusing
1.5 - BAD: Barely relevant, mostly unhelpful
1.0 - TERRIBLE: Does not solve the problem at all or completely off-topic

Be strict. Most responses should score between 3.0 and 4.0.
Only truly exceptional responses earn 4.5 or 5.0.
A helpful but cold and robotic response should score 3.0 to 3.5, not 5.0.
A warm response that doesn't solve the problem should score 2.0 to 2.5.

Return ONLY a number like 3.5 or 4.0. Nothing else."""
            },
            {
                "role": "user",
                "content": f"Customer question: {input_text}\n\nAI response: {output_text}"
            }
        ]
    )

    score = float(response.choices[0].message.content.strip())
    return score


def analyze_experiment(experiment_id: int):
    """Compare variant A vs B and declare a winner"""
    db = SessionLocal()

    results = db.query(ExperimentResult).filter(
        ExperimentResult.experiment_id == experiment_id
    ).all()

    if not results:
        print("❌ No results found for this experiment")
        db.close()
        return

    variant_a_scores = [r.quality_score for r in results if r.variant == "A"]
    variant_b_scores = [r.quality_score for r in results if r.variant == "B"]

    if not variant_a_scores or not variant_b_scores:
        print("❌ Not enough data for both variants yet")
        db.close()
        return

    avg_a = statistics.mean(variant_a_scores)
    avg_b = statistics.mean(variant_b_scores)

    print(f"\n📊 Experiment #{experiment_id} Results")
    print(f"{'='*40}")
    print(f"Variant A → {len(variant_a_scores)} results | Average score: {avg_a:.2f}/5")
    print(f"Variant B → {len(variant_b_scores)} results | Average score: {avg_b:.2f}/5")
    print(f"{'='*40}")

    difference = abs(avg_a - avg_b)

    if difference < 0.2:
        print("🤝 No clear winner yet — need more data!")
    elif avg_a > avg_b:
        print(f"🏆 Winner: Variant A (v{results[0].prompt_version})")
        print(f"   It scored {difference:.2f} points higher than Variant B")
    else:
        print(f"🏆 Winner: Variant B")
        print(f"   It scored {difference:.2f} points higher than Variant A")

    db.close()


def run_live_test(experiment_id: int, user_id: str, input_text: str, prompt_text: str, variant: str, prompt_version: int):
    """Run a real AI response and score it automatically"""
    import time
    from experiment import log_result
    client = get_client()

    start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": input_text}
        ]
    )
    latency_ms = (time.time() - start) * 1000
    output_text = response.choices[0].message.content

    quality_score = get_ai_quality_score(input_text, output_text)

    log_result(experiment_id, user_id, variant, prompt_version, input_text, output_text, quality_score, latency_ms)

    print(f"\n💬 Input: {input_text}")
    print(f"🤖 Response: {output_text}")
    print(f"⭐ Auto-score: {quality_score}/5")
    print(f"⏱️ Latency: {latency_ms:.0f}ms")