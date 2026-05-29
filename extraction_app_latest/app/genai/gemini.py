import google.generativeai as genai

def generate_invoice_response(json_data: dict, text_file_path: str) -> str:
    # Read invoice text from the provided file path
    with open(text_file_path, 'r') as file:
        text_data = file.read()
    
    # Extract required inputs from JSON data
    component_data = json_data['components'][1]['userInputs']
    api_key = component_data['apiKey']
    model_name = component_data['modelName']
    system_message = component_data['systemMessage']
    user_input = component_data['input']

    # Configure and initialize the generative model
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    # Build the prompt
    prompt = f"{system_message}\n{user_input}\nInvoice '''\n{text_data}\n'''"

    # Generate the AI response
    response = model.generate_content(prompt)
    
    # Save response to a file
    with open(output_file_path, 'w') as out_file:
        out_file.write(response.text)
    
    return response.text