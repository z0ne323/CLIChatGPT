"""import of modules"""
import json
import openai
import Helpers
from pathlib import Path


def load_json_response(res_parse_json):
    """Function used to load/parse the json response OpenAI sent us"""
    res_dic = json.loads(res_parse_json)
    return res_dic


def get_user_input_and_parse_filename(exclusion, excluded_character):
    """Function used to get a filename as input and parse it until we got a proper one"""
    filename_parsed = ""
    while filename_parsed.isalnum() is False:
        try:
            filename = input(
                "Please provide a filename for your report (without an extension / _ is accepted between chars): ")
            filename_parsed = filename
            if exclusion is True:
                if filename != '':
                    if filename[0] != excluded_character and filename[-1] != excluded_character and (excluded_character * 2 in filename) is not True:
                        filename_parsed = filename.replace(excluded_character, '')
        except (KeyboardInterrupt, EOFError) as k_err:
            Helpers.exception_handler(True, k_err)
            return None
    filename_txt = Path(filename + ".txt")
    if filename_txt.is_file():
        choice = ""
        while choice not in ["overwrite", "change"]:
            choice = input("[-] This file already exists on the system, do you want to overwrite or change the filename (overwrite/change): ")
            if choice == "overwrite":
                return filename
            else:
                return None
    else:
        return filename


def write_log_to_report(filename, data):
    """Function used to write logs of the conversation to a report"""
    try:
        with open(filename, "w", encoding="UTF-8") as file:
            file.write(data + "\n")
    except (IOError, KeyboardInterrupt, EOFError) as io_err:
        Helpers.exception_handler(True, io_err)
        exit(1)
    return True


def formatting_data(conversation_logs, conversation_logs_detailed):
    """Function used to format two piece of data, our filename by calling the get_user_input_and_parse_filename function and formatting our dictionnary containing the logs"""
    print("[*] Formatting data...")
    filename = None
    while filename is None:
        filename = get_user_input_and_parse_filename(True, '_')
    logs = ""
    for c in conversation_logs:
        logs += c + '\n'
    logs_detailed = ""
    for c in conversation_logs_detailed:
        logs_detailed += c + '\n'
    if write_log_to_report(filename + ".txt", logs) and write_log_to_report(filename + "_detailed.txt", logs_detailed):
        print(f"[+] The file report of the conversation logs can be found as {filename}.txt in {Path.cwd()}")
        print(f"[+] The file report of the conversation logs detailed can be found as {filename }_detailed.txt in {Path.cwd()}")
        return True


if __name__ == '__main__':
    asking_for_api_file_path = Helpers.get_path_from_user("[*] Please input the path to your API Key file: ")
    if asking_for_api_file_path is None:
        exit(1)

    openai.api_key = Helpers.read_api_key(asking_for_api_file_path)

    question_response_logs = []
    question_response_logs_detailed = []
    print("[*] Welcome to CLIChatGPT the CLI version of ChatGPT! Ask any questions to the bot! If you need help, type help")
    question_response_logs.append("[*] Welcome to CLIChatGPT the CLI version of ChatGPT! Ask any questions to the bot! If you need help, type help")
    question_response_logs_detailed.append("[*] Welcome to CLIChatGPT the CLI version of ChatGPT! Ask any questions to the bot! If you need help, type help")
    question = ""
    total_usage = 0
    try:
        while question != "exit":
            question = input(r"X:\> ")
            question_response_logs.append(rf"X:\> {question}")
            question_response_logs_detailed.append(rf"X:\> {question}")
            if question == "help":
                print("[*] Welcome to the Help Center!\n[*] You have two choices as of now, ask a question to CLIChatGPT, or type exit to quit this interactive prompt!")
                question_response_logs.append("[*] Welcome to the Help Center!\n[*] You have two choices as of now, ask a question to CLIChatGPT, or type exit to quit this interactive prompt!")
                question_response_logs_detailed.append("[*] Welcome to the Help Center!\n[*] You have two choices as of now, ask a question to CLIChatGPT, or type exit to quit this interactive prompt!")
            elif question == "exit":
                print("[+] Quitting the program...")
                question_response_logs.append("[+] Quitting the program...")
                question_response_logs_detailed.append("[+] Quitting the program...")
                safe_exit = formatting_data(question_response_logs, question_response_logs_detailed)
                if safe_exit is True:
                    exit(0)
            else:
                json_response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": question}], temperature=0)
                if json_response == "":
                    print("[-] OPENAI didn't send something back, try again please.")
                    question_response_logs.append("[-] OPENAI didn't send something back, try again please.")
                    question_response_logs_detailed.append("[-] OPENAI didn't send something back, try again please.")

                response = load_json_response(str(json_response))
                usage = response['usage']['total_tokens']
                response = response['choices'][0]['message']['content'].replace("\n", "")

                total_usage += int(usage)

                print(f"CLIChatGPT: {response}\n(Tokens usage for this interaction: {usage}, Total Tokens used since the beginning: {str(total_usage)})")
                question_response_logs.append(f"CLIChatGPT: {response}\n(Tokens usage for this interaction: {usage}, Total Tokens used since the beginning: {str(total_usage)})")
                question_response_logs_detailed.append(f"CLIChatGPT: {json_response}\n(Tokens usage for this interaction: {usage}, Total Tokens used since the beginning: {str(total_usage)})")
    except (KeyboardInterrupt, EOFError) as f_err:
        Helpers.exception_handler(True, f_err)
        print("\n[+] Quitting the program...")
        question_response_logs.append("[+] Quitting the program...")
        question_response_logs_detailed.append("[+] Quitting the program...")
        safe_exit = formatting_data(question_response_logs, question_response_logs_detailed)
        if safe_exit is True:
            exit(0)
