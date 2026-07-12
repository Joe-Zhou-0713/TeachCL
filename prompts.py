from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent # 找到当前 prompts.py 所在的文件夹
PROMPT_DIR = BASE_DIR / "prompts" # 指定 prompt 文件夹


def load_prompt(file_name):
    prompt_path = PROMPT_DIR / file_name

    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()


CHATBOT_PROMPT = load_prompt("System_Prompt.txt") # 读取协同机器人生成引擎 prompt
PATTERN_DETECTION_PROMPT = load_prompt("Pattern_Detection_Prompt.txt") # 读取 interaction pattern 识别 prompt
