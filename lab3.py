import streamlit as st
import tiktoken
from openai import OpenAI

st.title("Lab 3: Streaming Chatbot")

# 1. Set up the OpenAI client (key lives in .streamlit/secrets.toml)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
SYSTEM_PROMPT = (
    "You are a professional assistant. Give concise, direct answers. "
    "No filler, no preamble, no repeating the question. "
    "Use a formal, neutral tone. If a short answer is enough, give a short answer."
)

# Price in US dollars per 1 million tokens (input, output).
# Check https://openai.com/api/pricing if these change.
PRICES = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},  # "mini" model
    "gpt-4o": {"input": 2.50, "output": 10.00},  # "flagship" model
}

# 2. Sidebar settings
st.sidebar.header("Chat settings")
model = st.sidebar.selectbox("Model", ["gpt-4o-mini", "gpt-4o"])
buffer_size = st.sidebar.slider(
    "Buffer: keep the last N questions", min_value=1, max_value=10, value=3
)
max_tokens = st.sidebar.slider(
    "Buffer: send at most this many tokens",
    min_value=100,
    max_value=4000,
    value=1000,
    step=100,
)

# A tokenizer turns text into tokens so we can count them
encoding = tiktoken.get_encoding("o200k_base")


def count_tokens(messages):
    """Count the tokens in a list of messages."""
    total = 0
    for message in messages:
        total += len(encoding.encode(message["content"]))
    return total


def text_only(stream, usage_box):
    """Pass along just the reply text from the stream.
    OpenAI sends the token counts in the last chunk; save them in usage_box."""
    for chunk in stream:
        if chunk.usage:
            usage_box["usage"] = chunk.usage
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# 3. Create the memory the first time the page loads
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Re-draw the whole conversation on every rerun
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Handle a new user message
if prompt := st.chat_input("Ask me anything"):
    # Save and show the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Build the conversation buffer ---
    # Step A: keep only the last N user messages (and the replies to them).
    # Find where the N-th most recent user message starts, and keep from there.
    user_positions = []
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            user_positions.append(i)
    start = user_positions[-buffer_size] if len(user_positions) >= buffer_size else 0
    buffer = st.session_state.messages[start:]

    # Step B: drop the oldest messages until the buffer fits in max_tokens.
    # The system prompt counts too. We always keep the newest question.
    system_message = {"role": "system", "content": SYSTEM_PROMPT}
    while len(buffer) > 1 and count_tokens([system_message] + buffer) > max_tokens:
        buffer = buffer[1:]

    messages_to_send = [system_message] + buffer
    tokens_sent = count_tokens(messages_to_send)

    # Stream the assistant's reply
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=model,
            messages=messages_to_send,
            stream=True,
            stream_options={"include_usage": True},  # ask OpenAI for token counts
        )

        # Show the text as it arrives, and grab the token usage at the end
        usage_box = {}
        response = st.write_stream(text_only(stream, usage_box))
        usage = usage_box["usage"]

    # Save the finished reply so it persists on the next rerun
    st.session_state.messages.append({"role": "assistant", "content": response})

    # --- Tokens and cost for this request ---
    price = PRICES[model]
    cost = (
        usage.prompt_tokens * price["input"]
        + usage.completion_tokens * price["output"]
    ) / 1_000_000

    st.session_state.last_request = {
        "model": model,
        "messages_sent": len(messages_to_send),
        "tokens_sent": tokens_sent,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "cost": cost,
    }

# 6. Show the stats for the most recent request in the sidebar
if "last_request" in st.session_state:
    stats = st.session_state.last_request
    st.sidebar.divider()
    st.sidebar.subheader("Last request")
    st.sidebar.write(f"Model: {stats['model']}")
    st.sidebar.write(f"Messages sent (incl. system prompt): {stats['messages_sent']}")
    st.sidebar.write(f"Tokens we counted: {stats['tokens_sent']}")
    st.sidebar.write(f"Input tokens (from OpenAI): {stats['input_tokens']}")
    st.sidebar.write(f"Output tokens (from OpenAI): {stats['output_tokens']}")
    st.sidebar.write(f"Cost: ${stats['cost']:.6f}")
