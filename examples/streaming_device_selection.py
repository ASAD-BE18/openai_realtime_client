import asyncio
import os

from pynput import keyboard
from openai_realtime_client import RealtimeClient, AudioHandler, InputHandler, TurnDetectionMode
from llama_index.core.tools import FunctionTool


async def main():
    audio_handler = AudioHandler()
    input_handler = InputHandler()
    input_handler.loop = asyncio.get_running_loop()
    
    client = RealtimeClient(
        api_key=os.environ.get("OPENAI_API_KEY"),
        on_text_delta=lambda text: print(f"\nAssistant: {text}", end="", flush=True),
        on_audio_delta=lambda audio: audio_handler.play_audio(audio),
        on_interrupt=lambda: audio_handler.stop_playback_immediately(),
        turn_detection_mode=TurnDetectionMode.SERVER_VAD,
        tools=tools,
    )

    # List available input and output devices
    print("Available audio devices:")
    audio_handler.list_devices()
    
    # Select input and output devices by index
    input_device_index = 2
    output_device_index = 0
    
    audio_handler.select_input_device(input_device_index)
    audio_handler.select_output_device(output_device_index)

    # Start keyboard listener in a separate thread
    listener = keyboard.Listener(on_press=input_handler.on_press)
    listener.start()
    
    try:
        await client.connect()
        message_handler = asyncio.create_task(client.handle_messages())
        
        print("Connected to OpenAI Realtime API!")
        print("Audio streaming will start automatically.")
        print("Press 'q' to quit")
        print("")
        
        # Start continuous audio streaming
        streaming_task = asyncio.create_task(audio_handler.start_streaming(client))
        
        # Simple input loop for quit command
        while True:
            command, _ = await input_handler.command_queue.get()
            
            if command == 'q':
                break
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        audio_handler.stop_streaming()
        audio_handler.cleanup()
        await client.close()

if __name__ == "__main__":
    print("Starting Realtime API CLI with Server VAD...")
    asyncio.run(main())
