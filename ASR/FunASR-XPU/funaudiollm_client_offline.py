import argparse
from openai import OpenAI

def main():
    parser = argparse.ArgumentParser(description="SenseVoice ASR Client")
    parser.add_argument("--ip", required=True, help="Server IP, for example: 127.0.0.1")
    parser.add_argument("--audio", required=True, help="audio file path")
    parser.add_argument("--port", default="8005", help="Server Port, default 8005")
    parser.add_argument("--api_key", default="intel123", help="API Key")
    args = parser.parse_args()

    base_url = f"http://{args.ip}:{args.port}/v1"

    client = OpenAI(
        base_url=base_url,
        api_key=args.api_key
        )

    with open("long.wav", "rb") as f:
        result = client.audio.transcriptions.create(
            model="sensevoice",
            file=f,
            )

    print(result.text)


if __name__ == "__main__":
    main()
