"""
API wrapper for the NPU chatbot to be used by Electron app
"""
import sys
import argparse
import json
from chat_client import NPUChatClient

def main():
    parser = argparse.ArgumentParser(description='NPU Chatbot API Wrapper')
    parser.add_argument('--message', type=str, required=True, help='Message to send to the chatbot')
    parser.add_argument('--no-interactive', action='store_true', help='Run in non-interactive mode')
    parser.add_argument('--stream', action='store_true', help='Enable streaming response')
    
    args = parser.parse_args()
    
    try:
        # Initialize chat client with correct config path
        client = NPUChatClient('config.yaml')
        
        if args.stream:
            # Send message with streaming
            response_stream = client.send_message(args.message, True)
            if response_stream:
                for chunk in response_stream:
                    print(chunk, end='', flush=True)
            else:
                print("Error: Failed to get response from chatbot", file=sys.stderr)
                sys.exit(1)
        else:
            # Send message without streaming
            response = client.send_message(args.message, False)
            if response:
                print(response)
            else:
                print("Error: Failed to get response from chatbot", file=sys.stderr)
                sys.exit(1)
                
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
