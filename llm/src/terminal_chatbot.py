"""
Terminal-based chatbot interface for NPU-accelerated AnythingLLM
"""
import sys
import os
from chat_client import NPUChatClient

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🤖 NPU-Accelerated Chatbot (Llama 3.2 2B 8K)")
    print("Powered by AnythingLLM with NPU acceleration")
    print("=" * 60)
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("Type 'help' for more commands")
    print("=" * 60)

def print_help():
    """Print help information"""
    print("\n📖 Available Commands:")
    print("  quit, exit, bye  - End the conversation")
    print("  clear           - Clear conversation history")
    print("  help            - Show this help message")
    print("  history         - Show conversation history")
    print("\n💡 Tips:")
    print("  - The chatbot uses NPU acceleration for faster responses")
    print("  - Responses are streamed in real-time")
    print("  - The model has 8K context length")
    print()

def show_history(chat_client):
    """Show conversation history"""
    history = chat_client.get_history()
    if not history:
        print("No conversation history.")
        return
    
    print("\n📜 Conversation History:")
    print("-" * 40)
    for i, message in enumerate(history, 1):
        role = "👤 You" if message["role"] == "user" else "🤖 Assistant"
        content = message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"]
        print(f"{i}. {role}: {content}")
    print("-" * 40)

def main():
    """Main chatbot loop"""
    print_banner()
    
    # Initialize chat client
    try:
        chat_client = NPUChatClient()
        print("✅ Connected to AnythingLLM API")
    except Exception as e:
        print(f"❌ Failed to initialize chat client: {e}")
        print("Make sure AnythingLLM is running and config.yaml is properly configured.")
        return
    
    print("\n🚀 Ready to chat! Ask me anything...\n")
    
    while True:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye! Thanks for chatting!")
                break
            elif user_input.lower() == 'clear':
                chat_client.clear_history()
                print("🧹 Conversation history cleared.")
                continue
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'history':
                show_history(chat_client)
                continue
            elif not user_input:
                continue
            
            # Send message and get response
            print("\n🤖 Assistant: ", end="", flush=True)
            
            response_stream = chat_client.send_message(user_input)
            if response_stream:
                for chunk in response_stream:
                    print(chunk, end="", flush=True)
                print("\n")  # New line after response
            else:
                print("Sorry, I couldn't process your message. Please try again.")
                print()
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for chatting!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()
