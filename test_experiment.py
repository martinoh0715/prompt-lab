from experiment import create_experiment, assign_variant, log_result

# Create an experiment (v1 vs v2, 50/50 split)
experiment_id = create_experiment(
    name="Friendliness Test",
    prompt_name="EmailBot",
    variant_a=1,
    variant_b=2,
    traffic_split=0.5
)

# Simulate 10 users coming in
users = ["user_001", "user_002", "user_003", "user_004", "user_005",
         "user_006", "user_007", "user_008", "user_009", "user_010"]

print("\n--- Assigning variants to users ---")
for user_id in users:
    variant = assign_variant(experiment_id, user_id)
    print(f"{user_id} → Variant {variant}")

# Simulate logging some results
print("\n--- Logging results ---")
log_result(experiment_id, "user_001", "A", 1, "Where is my order?", "Your order is on its way!", 4.2, 823)
log_result(experiment_id, "user_002", "B", 2, "I need a refund", "I completely understand...", 4.8, 651)
log_result(experiment_id, "user_003", "A", 1, "My package is late", "I apologize for the delay...", 3.9, 910)
log_result(experiment_id, "user_004", "B", 2, "Wrong item received", "I'm so sorry to hear that...", 4.7, 720)