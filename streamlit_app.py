# Import the necessary libraries
import streamlit as st  # For creating the web app interface
from google import genai  # For interacting with the Google Gemini API
from google.genai import types
import re
import re as _re

# === Model Routing Constants ===
MAX_CHAT_HISTORY = 20            # Number of messages to keep in context
MODEL_MEDIUM_TIER_THRESHOLD = 5  # Threshold for gemini-2.5-flash
MODEL_TOP_TIER_THRESHOLD = 10    # Threshold for gemini-2.5-pro
TOKEN_THRESHOLD_PRO = 3000       # Token threshold for using pro model
WEIGHT_SMALL = 2
WEIGHT_MEDIUM = 3
WEIGHT_HARD = 5

# Temperature settings for different models
TEMPERATURE_PRO = 0.2            # Low temperature for consistent, accurate responses
TEMPERATURE_FLASH = 0.7          # Balanced temperature for medium creativity
TEMPERATURE_LITE = 1.0           # High temperature for creative, varied responses

# Top-p (nucleus sampling) settings for different models
TOP_P_PRO = 0.8                  # More focused sampling for consistency
TOP_P_FLASH = 0.9                # Balanced sampling
TOP_P_LITE = 0.95                # Broader sampling for creativity

# Top-k settings for different models
TOP_K_PRO = 20                   # Smaller vocabulary for more focused responses
TOP_K_FLASH = 40                 # Balanced vocabulary size
TOP_K_LITE = 64                  # Larger vocabulary for more varied responses

# Model routing keywords
HARD_KEYWORDS = [
    r"derivative", r"integral",  r"big-?o", r"complexity", r"algorithm", r"algoritma",r"mathematical",
    r"dynamic programming", r"regex", r"sql",  r"stack trace", r"panic", r"traceback",  r"recursion", r"algorithm", r"theorem", r"bukti", r"turunan", r"integral", r"induksi",
    r"np[-\s]?sulit", r"kompleksitas", r"pemrograman dinamis", r"jejak tumpukan", r"jejak kesalahan", r"jejak error", r"jejak",
    r"algoritma", r"teorema", r"persamaan", r"matematika", r"logika", r"berpikir keras", r"pikir keras", r"buktikan", r"soal sulit",
    r"tantangan", r"uji", r"uji coba", r"uji hipotesis", r"prima", r"prime"
]
MEDIUM_KEYWORDS = [
    r"apa itu", r"jelaskan", r"analisa", r"penjelasan", r"mengapa", r"kenapa", r"sulit", r"tantangan", r"perbaiki", r"kesalahan",
    r"masalah", r"solusi", r"langkah", r"cara", r"bagaimana", r"penyebab", r"penyelesaian" 
]
HARD_PATTERN = re.compile("|".join(HARD_KEYWORDS), re.IGNORECASE)
MEDIUM_PATTERN = re.compile("|".join(MEDIUM_KEYWORDS), re.IGNORECASE)

# === Helper Functions ===
def select_model(content: str, conversation_history: list) -> str:
    """Select Gemini model based on weighted content complexity and token count."""
    score = 1  # Start with a base score of 1
    
    # Calculate complexity score
    # Hard keywords: +5 each
    score += WEIGHT_HARD * len(HARD_PATTERN.findall(content))
    # Medium keywords: +3 each
    score += WEIGHT_MEDIUM * len(MEDIUM_PATTERN.findall(content))
    # Question marks: +2 each
    score += WEIGHT_SMALL * content.count('?')
    
    # Estimate token count for conversation context
    token_count = 0
    try:
        if conversation_history and len(conversation_history) > 0:
            # Build conversation prompt for token estimation
            prompt = ""
            # Use recent history for token counting (limit to avoid huge contexts)
            recent_history = conversation_history[-MAX_CHAT_HISTORY:]
            for msg in recent_history:
                prompt += f"{msg['role']}: {msg['content']}\n"
            
            # Add current message to the prompt for accurate estimation
            prompt += f"user: {content}\n"
            
            # Use the client from session state to count tokens
            if hasattr(st.session_state, 'genai_client') and st.session_state.genai_client:
                try:
                    estimated_token = st.session_state.genai_client.models.count_tokens(
                        model="gemini-2.5-flash-lite", 
                        contents=prompt
                    )
                    token_count = estimated_token.total_tokens if hasattr(estimated_token, 'total_tokens') else int(estimated_token)
                except Exception as e:
                    # Fallback: rough estimation if API call fails
                    # Approximate: 1 token ≈ 4 characters for English text
                    token_count = len(prompt) // 4
                    st.warning(f"Token estimation failed, using approximation: {token_count} tokens")
            else:
                # Fallback estimation when client not available
                token_count = len(prompt) // 4
        else:
            # For first message, just estimate current content
            token_count = len(content) // 4
            
    except Exception as e:
        # Fallback to character-based estimation
        total_text = content
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages for safety
                total_text += msg.get('content', '')
        token_count = len(total_text) // 4
    
    # Enhanced model selection with token consideration:
    # 1. gemini-2.5-pro: For really hard problems OR long conversations
    # 2. gemini-2.5-flash: For medium complexity
    # 3. gemini-2.5-flash-lite: For simple queries and short conversations
    
    if score >= MODEL_TOP_TIER_THRESHOLD or token_count > TOKEN_THRESHOLD_PRO:
        return "gemini-2.5-pro"        # Most capable model for complex/long contexts
    elif score >= MODEL_MEDIUM_TIER_THRESHOLD:
        return "gemini-2.5-flash"      # Balanced model for medium complexity
    else:
        return "gemini-2.5-flash-lite"  # Fastest model for simple queries

def wrap_code_blocks(text):
    """Process code blocks for Streamlit display - keep markdown formatting intact."""
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    
    # Keep markdown code blocks intact for Streamlit's native rendering
    # Streamlit automatically handles ```language and ``` code blocks
    # We just need to ensure proper formatting
    
    # Clean up any malformed code blocks and ensure proper spacing
    text = _re.sub(r"```(\w*)\s*\n", r"```\1\n", text)  # Clean language specifier
    text = _re.sub(r"```\s*$", "```", text, flags=_re.MULTILINE)  # Clean closing tags
    
    return text

def add_citations(response):
    """Add citations from grounding metadata."""
    text = ""
    grounding_metadata = getattr(response.candidates[0], "grounding_metadata", None)
    if not grounding_metadata:
        return text
    supports = getattr(grounding_metadata, "grounding_supports", None)
    chunks = getattr(grounding_metadata, "grounding_chunks", None)
    if not supports or not chunks:
        return text

    # Collect all unique citations (index, url)
    citation_map = {}
    for i, chunk in enumerate(chunks):
        if getattr(chunk, "web", None) and getattr(chunk.web, "uri", None):
            citation_map[i + 1] = chunk.web.uri

    # Build bibliography at the end
    if citation_map:
        bib = "\n\n Referensi:\n"
        for idx, url in sorted(citation_map.items()):
            bib += f"[{idx}] {url}\n"
        return bib.strip()
    else:
        return ""

# --- 1. Page Configuration and Title ---

# Set the title and a caption for the web page
st.title("💬 Smart Gemini Chatbot")
st.caption("Intelligent chat with dynamic model routing using Google's Gemini models")

# --- 2. Sidebar for Settings ---

# Create a sidebar section for app settings using 'with st.sidebar:'
with st.sidebar:
    # Add a subheader to organize the settings
    st.subheader("Settings")
    
    # Create a text input field for the Google AI API Key.
    # 'type="password"' hides the key as the user types it.
    google_api_key = st.text_input("Google AI API Key", type="password")
    
    # Create a button to reset the conversation.
    # 'help' provides a tooltip that appears when hovering over the button.
    reset_button = st.button("Reset Conversation", help="Clear all messages and start fresh")
    
    # Add toggle for showing model thinking process
    show_thinking = st.toggle("Show Model Thinking Process", value=True, help="Display model selection and reasoning steps")
    
    if show_thinking:
        st.info("💭 **Thinking Mode**: You'll see the model's decision-making process including complexity analysis, token counting, and parameter selection.", icon="🧠")
    
    # Show model routing information
    st.subheader("🤖 Smart Model Routing")
    st.markdown("""
    **Gemini-2.5-Pro** is used for:
    - Very complex mathematical problems
    - Advanced algorithms and data structures
    - Research-level technical analysis
    - Long conversations (>3000 tokens)
    - *Temperature: 0.2, Top-p: 0.8, Top-k: 20 (focused & consistent)*
    
    **Gemini-2.5-Flash** is used for:
    - Programming and code analysis
    - Technical explanations
    - Medium complexity problems
    - *Temperature: 0.7, Top-p: 0.9, Top-k: 40 (balanced)*
    
    **Gemini-2.5-Flash-Lite** is used for:
    - Simple questions
    - General conversations
    - Basic information requests
    - Short conversations
    - *Temperature: 1.0, Top-p: 0.95, Top-k: 64 (creative & varied)*
    
    *Routing considers both content complexity and conversation length*
    """)
    
    # Show current conversation stats
    if "messages" in st.session_state and st.session_state.messages:
        st.subheader("📊 Conversation Stats")
        total_messages = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.metric("Total Messages", total_messages)
        st.metric("Your Messages", user_messages)

# --- 3. API Key and Client Initialization ---

# Check if the user has provided an API key.
# If not, display an informational message and stop the app from running further.
if not google_api_key:
    st.info("Please add your Google AI API key in the sidebar to start chatting.", icon="🗝️")
    st.stop()

# This block of code handles the creation of the Gemini API client.
# It's designed to be efficient: it only creates a new client if one doesn't exist
# or if the user has changed the API key in the sidebar.

# We use `st.session_state` which is Streamlit's way of "remembering" variables
# between user interactions (like sending a message or clicking a button).

# Condition 1: "genai_client" not in st.session_state
# Checks if we have *never* created the client before.
#
# Condition 2: getattr(st.session_state, "_last_key", None) != google_api_key
# This is a safe way to check if the current API key is different from the last one we used.
# `getattr(object, 'attribute_name', default_value)` tries to get an attribute from an object.
# If the attribute doesn't exist, it returns the default value (in this case, `None`).
# So, it checks: "Is the key stored in memory different from the one in the input box?"
if ("genai_client" not in st.session_state) or (getattr(st.session_state, "_last_key", None) != google_api_key):
    try:
        # If the conditions are met, create a new client.
        st.session_state.genai_client = genai.Client(api_key=google_api_key)
        # Store the new key in session state to compare against later.
        st.session_state._last_key = google_api_key
        # Since the key changed, we must clear the chat session and message history.
        # .pop() safely removes an item from session_state.
        st.session_state.pop("chat", None)
        st.session_state.pop("current_model", None)
        st.session_state.pop("messages", None)
    except Exception as e:
        # If the key is invalid, show an error and stop.
        st.error(f"Invalid API Key: {e}")
        st.stop()


# --- 4. Chat History Management ---

# Initialize single chat session that we'll use with model switching
if "chat" not in st.session_state:
    st.session_state.chat = None
if "current_model" not in st.session_state:
    st.session_state.current_model = None

# Initialize the message history (shared across all models)
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_or_create_chat_session(model_name: str):
    """Get or create a chat session, recreating if model changes to maintain context."""
    # Different models support different tools
    tools = []
    
    # Code execution and search tools support varies by model
    if model_name in ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"]:
        tools = [
            types.Tool(code_execution=types.ToolCodeExecution),
            types.Tool(google_search=types.GoogleSearch())
        ]
    # For experimental models or others, use no tools or adjust as needed
    
    # Set generation parameters based on model for different creativity/consistency levels
    if model_name == "gemini-2.5-pro":
        temperature = TEMPERATURE_PRO      # 0.2 - More consistent, accurate responses
        top_p = TOP_P_PRO                  # 0.8 - More focused sampling
        top_k = TOP_K_PRO                  # 20 - Smaller vocabulary for consistency
    elif model_name == "gemini-2.5-flash":
        temperature = TEMPERATURE_FLASH    # 0.7 - Balanced creativity
        top_p = TOP_P_FLASH                # 0.9 - Balanced sampling
        top_k = TOP_K_FLASH                # 40 - Balanced vocabulary
    else:  # gemini-2.5-flash-lite
        temperature = TEMPERATURE_LITE     # 1.0 - More creative, varied responses
        top_p = TOP_P_LITE                 # 0.95 - Broader sampling for creativity
        top_k = TOP_K_LITE                 # 64 - Larger vocabulary for variety
    
    config = types.GenerateContentConfig(
        tools=tools,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        system_instruction="You are a helpful assistant. Use Google Search if needed to ground your answers and cite sources with [number] where relevant. Use Code execution tool only for code-related queries and complex math, do not show internal tool in response if it being used"
    )
    
    # If model changed or no chat exists, create new session with the new model
    if (st.session_state.chat is None or 
        st.session_state.current_model != model_name):
        
        st.session_state.chat = st.session_state.genai_client.chats.create(
            model=model_name,
            config=config
        )
        st.session_state.current_model = model_name
    
    return st.session_state.chat

def send_message_with_context(chat_session, current_message, message_history):
    """Send message with full conversation context for model switches."""
    # If this is the first message or we just switched models,
    # we need to provide context from the conversation history
    if len(message_history) > 1:  # More than just the current user message
        # Build context from conversation history
        context_messages = message_history[:-1]  # All except current message
        context = "Previous conversation:\n"
        for msg in context_messages[-MAX_CHAT_HISTORY:]:  # Limit context
            context += f"{msg['role']}: {msg['content']}\n"
        context += f"\nCurrent message: {current_message}"
        
        # Send the context + current message
        return chat_session.send_message(context)
    else:
        # First message, send directly
        return chat_session.send_message(current_message)

# Handle the reset button click.
if reset_button:
    # If the reset button is clicked, clear chat and message history from memory.
    st.session_state.pop("chat", None)
    st.session_state.pop("current_model", None)
    st.session_state.pop("messages", None)
    # st.rerun() tells Streamlit to refresh the page from the top.
    st.rerun()

# --- 5. Display Past Messages ---

# Loop through every message currently stored in the session state.
for msg in st.session_state.messages:
    # For each message, create a chat message bubble with the appropriate role ("user" or "assistant").
    with st.chat_message(msg["role"]):
        # Display the content of the message using Markdown for nice formatting.
        st.markdown(msg["content"])

# --- 6. Handle User Input and API Communication ---

# Create a chat input box at the bottom of the page.
# The user's typed message will be stored in the 'prompt' variable.
prompt = st.chat_input("Type your message here...")

# Check if the user has entered a message.
if prompt:
    # 1. Add the user's message to our message history list.
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 2. Display the user's message on the screen immediately for a responsive feel.
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Get the assistant's response using dynamic model routing with context preservation.
    try:
        # Select the appropriate model based on content complexity
        selected_model = select_model(prompt, st.session_state.messages)
        
        # Get or create the appropriate chat session (recreates if model changed)
        chat_session = get_or_create_chat_session(selected_model)
        
        # Display which model is being used and if it switched
        model_switched = st.session_state.current_model != selected_model
        
        with st.chat_message("assistant"):
            # Create a status container to show model thinking process (if enabled)
            if show_thinking:
                status_container = st.status("🤔 Model is thinking...", expanded=True)
                response_placeholder = st.empty()
                
                with status_container:
                    # Show model selection process
                    st.write(f"🎯 **Model Selection**: Analyzing complexity...")
                    complexity_score = 1 + WEIGHT_HARD * len(HARD_PATTERN.findall(prompt)) + WEIGHT_MEDIUM * len(MEDIUM_PATTERN.findall(prompt)) + WEIGHT_SMALL * prompt.count('?')
                    st.write(f"📊 **Complexity Score**: {complexity_score}")
                    
                    # Show token estimation
                    try:
                        if st.session_state.messages:
                            conversation_prompt = ""
                            recent_history = st.session_state.messages[-MAX_CHAT_HISTORY:]
                            for msg in recent_history:
                                conversation_prompt += f"{msg['role']}: {msg['content']}\n"
                            conversation_prompt += f"user: {prompt}\n"
                            
                            estimated_token = st.session_state.genai_client.models.count_tokens(
                                model="gemini-2.5-flash-lite", 
                                contents=conversation_prompt
                            )
                            token_count = estimated_token.total_tokens if hasattr(estimated_token, 'total_tokens') else int(estimated_token)
                        else:
                            token_count = len(prompt) // 4
                        st.write(f"🔢 **Token Count**: ~{token_count}")
                    except:
                        token_count = len(prompt) // 4
                        st.write(f"🔢 **Token Count**: ~{token_count} (estimated)")
                    
                    st.write(f"🤖 **Selected Model**: {selected_model}")
                    
                    # Show context preservation info if model switched
                    if model_switched and len(st.session_state.messages) > 1:
                        st.write(f"⚡ **Context Preservation**: Switching from {st.session_state.current_model} to {selected_model}")
                        st.write("📝 **Status**: Injecting conversation history for seamless transition...")
                    
                    # Show model parameters
                    if selected_model == "gemini-2.5-pro":
                        st.write(f"⚙️ **Parameters**: Temperature=0.2, Top-p=0.8, Top-k=20 (focused & consistent)")
                    elif selected_model == "gemini-2.5-flash":
                        st.write(f"⚙️ **Parameters**: Temperature=0.7, Top-p=0.9, Top-k=40 (balanced)")
                    else:
                        st.write(f"⚙️ **Parameters**: Temperature=1.0, Top-p=0.95, Top-k=64 (creative & varied)")
                    
                    st.write("🧠 **Generating response**...")
            else:
                # Simple spinner when thinking display is disabled
                response_placeholder = st.empty()
                complexity_score = 1 + WEIGHT_HARD * len(HARD_PATTERN.findall(prompt)) + WEIGHT_MEDIUM * len(MEDIUM_PATTERN.findall(prompt)) + WEIGHT_SMALL * prompt.count('?')
                
                # Calculate token count
                try:
                    if st.session_state.messages:
                        conversation_prompt = ""
                        recent_history = st.session_state.messages[-MAX_CHAT_HISTORY:]
                        for msg in recent_history:
                            conversation_prompt += f"{msg['role']}: {msg['content']}\n"
                        conversation_prompt += f"user: {prompt}\n"
                        
                        estimated_token = st.session_state.genai_client.models.count_tokens(
                            model="gemini-2.5-flash-lite", 
                            contents=conversation_prompt
                        )
                        token_count = estimated_token.total_tokens if hasattr(estimated_token, 'total_tokens') else int(estimated_token)
                    else:
                        token_count = len(prompt) // 4
                except:
                    token_count = len(prompt) // 4
                
                with st.spinner(f"Thinking... (using {selected_model})"):
                    pass  # Just show the spinner
            
            # Generate the actual response
            if model_switched and len(st.session_state.messages) > 1:
                # Send message with conversation context for model switches
                response = send_message_with_context(chat_session, prompt, st.session_state.messages)
            else:
                # Normal send_message for same model or first message
                response = chat_session.send_message(prompt)
            # Extract and process the response with better handling for different response types
            if hasattr(response, "text"):
                assistant_reply = response.text
            else:
                # Handle responses with multiple parts (text, code, etc.)
                assistant_reply = ""
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            content_parts = []
                            for part in candidate.content.parts:
                                # Always include text parts
                                if hasattr(part, 'text') and part.text:
                                    content_parts.append(part.text)
                                
                                # Include executable code if present and relevant
                                if hasattr(part, 'executable_code') and part.executable_code:
                                    if hasattr(candidate, 'finish_reason') and candidate.finish_reason == "STOP":
                                        content_parts.append(f"\n```\n{part.executable_code.code}\n```\n")
                                
                                # Include code execution results if present
                                if hasattr(part, 'code_execution_result') and part.code_execution_result:
                                    if hasattr(part.code_execution_result, 'output') and part.code_execution_result.output:
                                        if hasattr(candidate, 'finish_reason') and candidate.finish_reason == "STOP":
                                            content_parts.append(f"\n**Output:**\n```\n{part.code_execution_result.output}\n```\n")
                            
                            assistant_reply = "".join(content_parts)
                        else:
                            # Fallback to string conversion
                            assistant_reply = str(candidate.content)
                    else:
                        assistant_reply = str(candidate)
                else:
                    # Final fallback
                    assistant_reply = str(response)
            
            if not assistant_reply or assistant_reply.strip() == "":
                assistant_reply = "I apologize, but I couldn't generate a proper response. Please try again."

            # Process code blocks (keeping the enhanced processing from main.py)
            assistant_reply = wrap_code_blocks(assistant_reply)
            
            # Add citations if available
            try:
                citations = add_citations(response)
                if citations:
                    assistant_reply += citations
            except:
                # Skip citations if there's an error processing them
                pass
            
            # Update status to show completion (if thinking display is enabled)
            if show_thinking:
                status_container.update(label="✅ Response generated!", state="complete")
            
            # Display the final response
            with response_placeholder.container():
                st.markdown(assistant_reply)
                
                # Show final model info
                model_info = f"Model: {selected_model} | Complexity Score: {complexity_score} | Tokens: ~{token_count}"
                if model_switched:
                    model_info += " | ⚡ Model switched with context preserved"
                st.caption(model_info)

    except Exception as e:
        # If any error occurs, create an error message to display to the user.
        assistant_reply = f"An error occurred: {e}"
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)

    # 4. Add the assistant's response to the message history list.
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})