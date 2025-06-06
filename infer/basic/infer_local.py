from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import os
import torch

device = "cuda:0"  # the device to load the model onto
# os.environ["CUDA_VISIBLE_DEVICES"] = "4,5,6,7"
model_name_or_path = "./all_models/Qwen2.5-7B-Instruct_1111"

# Load the model and tokenizer
model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)


def load_json_files_from_directory(directory_path):
    json_data = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                json_data[filename] = data  
    return json_data


def process_rules(rules):
    processed_results = []
    
    for rule in rules:
        need_regeneration = True
        num = 0
        output_str = ""

        while need_regeneration:
            # Reset flag and output string
            need_regeneration = False
            
            # Prepare model inputs
            messages = [
                {"role": "user", "content": rule}
            ]
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = tokenizer([text], return_tensors="pt").to(device)

            # Generate the output
            generated_ids = model.generate(
                model_inputs.input_ids,
                max_new_tokens=512
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            output_str += response
            num += 1
            
            # if "&" not in output_str and "|" not in output_str:
            #     need_regeneration = True

            # Stop regenerating if too many attempts (avoid infinite loop)
            if num > 10:
                need_regeneration = False

        processed_results.append(output_str)
    return processed_results


input_directory = './prompt/basic_prompt/cn' 
output_directory = './result/2.5_7b_ori/ori'  


json_files = load_json_files_from_directory(input_directory)


for filename, rules in json_files.items():
    if isinstance(rules, list):  
        processed_results = process_rules(rules)
        
     
        base_name = os.path.splitext(filename)[0]  
        output_filepath = os.path.join(output_directory, f"{base_name}.json")
        
       
        with open(output_filepath, 'w', encoding='utf-8') as json_file:
            json.dump(processed_results, json_file, ensure_ascii=False, indent=4)

        print(f"Processed results for '{filename}' have been saved to '{output_filepath}'.")

