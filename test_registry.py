from prompt_registry import create_prompt, get_active_prompt, list_versions, rollback

# Create first version
create_prompt(
    name="EmailBot",
    system_prompt="You are a helpful customer support assistant. Be professional and concise.",
    commit_message="Initial version"
)

# Create second version
create_prompt(
    name="EmailBot",
    system_prompt="You are a friendly customer support assistant. Be warm, empathetic, and concise.",
    commit_message="Made it friendlier"
)

# Create third version
create_prompt(
    name="EmailBot",
    system_prompt="You are a customer support assistant. Keep responses under 3 sentences.",
    commit_message="Tried shorter responses"
)

# Show all versions
list_versions("EmailBot")

# Roll back to version 1
rollback("EmailBot", 1)

# Show versions again to confirm rollback
list_versions("EmailBot")