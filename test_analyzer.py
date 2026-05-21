from analyzer import analyze_experiment, run_live_test
from prompt_registry import get_active_prompt, rollback
from experiment import create_experiment, assign_variant

# Step 1: Create a new experiment (v1 vs v2)
experiment_id = create_experiment(
    name="Quality Test",
    prompt_name="EmailBot",
    variant_a=1,
    variant_b=2,
    traffic_split=0.5
)

# Step 2: Get the actual prompts from our registry
rollback("EmailBot", 1)
prompt_v1 = get_active_prompt("EmailBot")

rollback("EmailBot", 2)
prompt_v2 = get_active_prompt("EmailBot")

# Step 3: Run real AI tests with real scoring
print("\n🧪 Running live AI tests...\n")

# Test v1 with 3 customer questions
run_live_test(experiment_id, "user_101", "Where is my order?", prompt_v1.system_prompt, "A", 1)
run_live_test(experiment_id, "user_102", "I want a refund please.", prompt_v1.system_prompt, "A", 1)
run_live_test(experiment_id, "user_103", "My package arrived damaged.", prompt_v1.system_prompt, "A", 1)

# Test v2 with same questions
run_live_test(experiment_id, "user_104", "Where is my order?", prompt_v2.system_prompt, "B", 2)
run_live_test(experiment_id, "user_105", "I want a refund please.", prompt_v2.system_prompt, "B", 2)
run_live_test(experiment_id, "user_106", "My package arrived damaged.", prompt_v2.system_prompt, "B", 2)

# Step 4: Analyze and declare winner!
print("\n🏆 Analyzing results...")
analyze_experiment(experiment_id)