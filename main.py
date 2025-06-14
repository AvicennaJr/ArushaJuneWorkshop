import os
import json
import groq

client = groq.Groq(api_key="your-api-key")

conversation = [
    {"role": "system", "content": "You are a helpful AI assisstant. You will always do what you are told and inform the user what you have done."}
]

def calculator(operation: str, x: int, y: int):
    if operation.lower() == "add":
        return x + y
    elif operation.lower() == "multiply":
        return x * y
    elif operation.lower() == "subtract":
        return x - y
    elif operation.lower() == "divide":
        return x / y
    else:
        return "operation not supported"

def read_file(filename: str):
    try:
        full_path = os.path.join("./", filename)
        with open(full_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Failed to read from file: {str(e)}"

def create_folder(foldername: str):
    try:
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        return "folder created successfully"
    except Exception:
        return "failed to create folder"

def create_file(filename: str, content: str = ""):
    try:
        full_path = os.path.join("./", filename)
        with open(full_path, 'a') as file:
            file.write(content)
        return f"File '{filename}' created successfully"
    except Exception as e:
        return f"Failed to create file: {str(e)}"

tools = [
    {
      "type": "function",
      "function": {
        "name": "calculator",
        "description": "Calculate the values of two numbers",
        "parameters": {
          "type": "object",
          "properties": {
            "operation": {
              "type": "string",
              "description": "The type of operation to perform. Supported operations are add, multiply, divide and subtract"
            },
            "x": {
              "type": "integer",
              "description": "The value of the first number"
            },
            "y": {
              "type": "integer",
              "description": "The value of the second number"
            }
          },
          "required": ["operation", "x", "y"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "read_file",
        "description": "A function to read files. The files it reads will always be in the current directory.",
        "parameters": {
          "type": "object",
          "properties": {
            "filename": {
              "type": "string",
              "description": "The name of the file to read from"
            },
          },
          "required": ["filename"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "create_folder",
        "description": "A function to create folders.",
        "parameters": {
          "type": "object",
          "properties": {
            "foldername": {
              "type": "string",
              "description": "The name of the folder to create"
            },
          },
          "required": ["foldername"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "create_file",
        "description": "A function to create files with its contents.",
        "parameters": {
          "type": "object",
          "properties": {
            "filename": {
              "type": "string",
              "description": "The name of the file to create"
            },
            "content": {
              "type": "string",
              "description": "The contents of the file"
            },
          },
          "required": ["filename", "content"]
        }
      }
    }
]

# message = input("Your message: ")
#
# conversation.append({"role": "user", "content": message})
#
# first_ai_response = client.chat.completions.create(messages=conversation, model="llama-3.3-70b-versatile", tools=tools, tool_choice="auto")
#
# should_we_use_tools = first_ai_response.choices[0].message.tool_calls

while True:
    message = input("Your message: ")

    conversation.append({"role": "user", "content": message})

    first_ai_response = client.chat.completions.create(messages=conversation, model="llama-3.3-70b-versatile", tools=tools, tool_choice="auto")

    should_we_use_tools = first_ai_response.choices[0].message.tool_calls
    if should_we_use_tools:
        available_functions = {
            "calculator": calculator,
            "read_file": read_file,
            "create_folder": create_folder,
            "create_file": create_file,
        }
        conversation.append(first_ai_response.choices[0].message)
        for tool_call in should_we_use_tools:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            conversation.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response),
                }
            )
        second_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation
        )
        print(second_response.choices[0].message.content)

    else:
        print(first_ai_response.choices[0].message.content)
