"""
Gradio web interface for NPU-accelerated AnythingLLM chatbot
"""
import gradio as gr
import sys
import os
from chat_client import NPUChatClient

class GradioChatInterface:
    def __init__(self):
        """Initialize the Gradio chat interface"""
        self.chat_client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize the chat client"""
        try:
            self.chat_client = NPUChatClient()
            print("✅ Connected to AnythingLLM API")
        except Exception as e:
            print(f"❌ Failed to initialize chat client: {e}")
            print("Make sure AnythingLLM is running and config.yaml is properly configured.")
            self.chat_client = None
    
    def chat_response(self, message, history):
        """Handle chat response for Gradio interface"""
        if not self.chat_client:
            return "Error: Chat client not initialized. Please check your configuration."
        
        if not message.strip():
            return history
        
        # Add user message to history
        history.append([message, ""])
        
        # Get response from chat client
        response_stream = self.chat_client.send_message(message)
        
        if response_stream:
            # Collect the full response
            full_response = ""
            for chunk in response_stream:
                full_response += chunk
            
            # Update the last message in history
            history[-1][1] = full_response
        else:
            history[-1][1] = "Sorry, I couldn't process your message. Please try again."
        
        return history
    
    def clear_chat(self):
        """Clear the chat history"""
        if self.chat_client:
            self.chat_client.clear_history()
        return []
    
    def create_interface(self):
        """Create the Gradio interface"""
        if not self.chat_client:
            return gr.Interface(
                fn=lambda x: "Error: Chat client not initialized",
                inputs="text",
                outputs="text",
                title="❌ NPU Chatbot - Configuration Error",
                description="Please check your config.yaml and ensure AnythingLLM is running."
            )
        
        with gr.Blocks(
            title="NPU-Accelerated Chatbot",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 800px !important;
                margin: auto !important;
            }
            .chat-message {
                padding: 10px;
                margin: 5px 0;
                border-radius: 10px;
            }
            """
        ) as interface:
            gr.Markdown(
                """
                # 🤖 NPU-Accelerated Chatbot
                **Powered by AnythingLLM with Llama 3.2 2B 8K on NPU**
                
                This chatbot runs locally on your NPU for fast, private conversations.
                """
            )
            
            chatbot = gr.Chatbot(
                label="Chat History",
                height=500,
                show_label=True,
                container=True,
                bubble_full_width=False
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your Message",
                    placeholder="Ask me anything...",
                    lines=2,
                    scale=4
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("Clear Chat", variant="secondary")
                gr.Markdown(
                    """
                    **Commands:**
                    - Type your message and press Enter or click Send
                    - Click "Clear Chat" to start a new conversation
                    - The chatbot uses NPU acceleration for faster responses
                    """
                )
            
            # Event handlers
            msg.submit(
                self.chat_response,
                inputs=[msg, chatbot],
                outputs=[chatbot],
                show_progress=True
            ).then(
                lambda: "",  # Clear input
                outputs=[msg]
            )
            
            send_btn.click(
                self.chat_response,
                inputs=[msg, chatbot],
                outputs=[chatbot],
                show_progress=True
            ).then(
                lambda: "",  # Clear input
                outputs=[msg]
            )
            
            clear_btn.click(
                self.clear_chat,
                outputs=[chatbot]
            )
        
        return interface

def main():
    """Main function to launch the Gradio interface"""
    print("🚀 Starting NPU-Accelerated Chatbot...")
    
    # Create and launch the interface
    interface = GradioChatInterface()
    gradio_interface = interface.create_interface()
    
    # Launch the interface
    gradio_interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,       # Default Gradio port
        share=False,            # Set to True if you want a public link
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()
