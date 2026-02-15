import csv
import sys
import requests

def extract_exercises(file_path):
    """
    Reads the CSV and returns a list of dictionaries.
    Each dictionary contains: 'Number', 'Title', and 'Description'.
    """
    exercise_list = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            # DictReader automatically uses the first row as keys
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Cleaning up data and appending to our list
                exercise_list.append({
                    "Number": row['Problem Number'],
                    "Title": row['Problem Title'],
                    "Description": row['Problem Description']
                })
        return exercise_list

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    except KeyError as e:
        print(f"Error: Check your CSV headers. Missing column: {e}")
        return []

def prepare_prompt(problem):

    prefix = "Write Python code for:"

    postfix = "Provide raw code only. No explanations, no preamble, and no markdown backticks. Please use short statements. Please do not use f-strings."

    prompt = f"{prefix} {problem}. {postfix}"

    return prompt

def generate(prompt):
    '''
    For sending one prompt
    '''
    global temperature

    # logger = jvox_logging("general", log_to_stderr=False)
    # logger.debug(f"Sending prompt: {prompt}, with temperature {temperature}.")

    # use llama.cpp's OAI compatible interface
    llama_server_url = "http://localhost:4590" 
    url  = llama_server_url + "/v1/chat/completions"

    # send request
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [{"role": "user",
                      "content": prompt} ],
        "temperature": 0,
    }
    
    response = requests.post(url, headers=headers, json=data)
    # logger.debug(f"LLama full response:\n{response.json()}")

    choices = response.json().get("choices", [])
    response = choices[0]
    response_text = response["message"]["content"]
    # logger.debug(f"LLama response text:\n{response_text}")

    response_reasoning = None
    if "reasoning_content" in response["message"]:
        response_reasoning = response["message"]["reasoning_content"]
        # logger.debug(f"LLama response thinking output:\n{response_reasoning}")
    
    return response_text

if __name__ == "__main__":
    # Check if the user provided a filename argument
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <your_file.csv>")
    else:
        filename = sys.argv[1]
        data = extract_exercises(filename)

        max_rounds = 1 #3
        
        # Demonstrating how to use the returned list
        print(f"Successfully extracted {len(data)} exercises.\n")
        for item in data:
            print(f"[{item['Number']}] {item['Title']}")

            # generate prompt
            prompt = prepare_prompt(item["Description"])
            print(f"Prompt is: {prompt}")
            print()
            for i in range(max_rounds):
                # connect to server to generate results
                response_text = generate(prompt)
                print(f"Round {i+1} #################:\n {response_text}")
                ## print(f"{response_text}")

            #break
