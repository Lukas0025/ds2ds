from datasets import load_dataset
from ollama import chat, ChatResponse, Client
import argparse
from tqdm import tqdm

def parseCliArgs():

    parser = argparse.ArgumentParser(
        description="Convert datasets using advance LLMs from ollama hosts."
    )

    parser.add_argument(
        "--ollama_host",
        type=str,
        required=True,
        help="Host address of the Ollama server."
    )

    parser.add_argument(
        "--hf_token",
        type=str,
        required=True,
        help="Hugging Face token for authentication."
    )

    parser.add_argument(
        "--hf_source",
        type=str,
        required=True,
        help="Format of the input dataset."
    )

    parser.add_argument(
        "--hf_output",
        type=str,
        required=True,
        help="Format of the output dataset."
    )

    parser.add_argument(
        "--out_transfer_fields",
        type=str,
        nargs='+',
        required=False,
        help="names of the fields transferd from the input dataset to the output dataset."
    )

    parser.add_argument(
        "--stages",
        type=int,
        default=1,
        help="Number of stages in the conversion process."
    )

    parser.add_argument(
        "--to_lang",
        type=str,
        default="English",
        help="Target language for translation."
    )

    parser.add_argument(
        "--prompts",
        type=str,
        nargs='+',
        required=False,
        help="Prompts for each stage (space-separated). Example: --prompts 'prompt1' 'prompt2' 'prompt3'"
    )

    parser.add_argument(
        "--models",
        type=str,
        nargs='+',
        required=False,
        help="Models for each stage (space-separated). Example: --models 'model1' 'model2' 'model3'"
    )

    parser.add_argument(
        "--start_index",
        type=int,
        default=0,
        help="Start processing from this index (default: 0)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of items to process (default: all)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output."
    )

    args = parser.parse_args()
    
    # Validate that prompts and models match the number of stages
    if args.prompts and len(args.prompts) != args.stages:
        parser.error(f"Number of prompts ({len(args.prompts)}) must match number of stages ({args.stages})")
    
    if args.models and len(args.models) != args.stages:
        parser.error(f"Number of models ({len(args.models)}) must match number of stages ({args.stages})")

    if args.out_transfer_fields and len(args.out_transfer_fields) != args.stages:
        parser.error(f"Number of out_transfer_fields ({len(args.out_transfer_fields)}) must match number of stages ({args.stages})")

    return args

def parse_errors(text):
    try:
        # Odstraníme všechny znaky kromě číslic a čárek
        filtered = "".join(c if c.isdigit() or c == "," else "" for c in text)
        parts = filtered.split(",")
        # Pokud máme méně než 3 čísla, doplníme nuly
        while len(parts) < 3:
            parts.append("0")
        # Převedeme na integer
        return tuple(int(p) for p in parts[:3])
    except Exception:
        # Pokud se cokoli pokazí, vrátíme 1
        return 1, 1, 1

def extract_clean_output(content):
    """Extracts clean output from model response, removing thinking blocks."""
    import re
    
    # Odstranění thinking bloků (DeepSeek, o1, atd.)
    # Vzor: <think>...</think> nebo <thinking>...</thinking>
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    content = re.sub(r'<thinking>.*?</thinking>', '', content, flags=re.DOTALL)
    
    # Odstranění prázdných řádků na začátku a konci
    content = content.strip()
    
    return content

def process_dataset_with_model(dataset, model, prompt, out_transfer_field, lang="English", client=None, verbose=False):

    rows_to_remove = []
    data_to_write = []
    verify_counter_good = 0
    verify_counter_bad  = 0

    for i in tqdm(range(len(dataset)), desc=f"Processing with {model}", unit="items"):

        input_text = prompt.format(**dataset[i])
        if prompt and prompt.startswith(">>VERIFY<<"):
            input_text = input_text.replace(">>VERIFY<<", "")
            input_text = f"Please verify the following text for correctness and completeness. Write only the number of grammar errors, logic errors, and spelling errors, separated by commas, with no additional text or explanation:\n\n{input_text}"

        if prompt and prompt.startswith(">>TRANSLATE<<"):
            input_text = input_text.replace(">>TRANSLATE<<", "")

            if len(input_text.strip()) == 0:
                if len(dataset[i][out_transfer_field].strip()) == 0: # nothing to translate
                    continue

                input_text = f"Translate the following text into {lang}. Do not add explanations or comments—write only the translated text:\n\n{dataset[i][out_transfer_field]}"
            else:
                if len(input_text.strip()) == 0: # nothing to translate
                    continue

                input_text = f"Translate the following text into {lang}. Do not add explanations or comments—write only the translated text:\n\n{input_text}"


        response: ChatResponse = client.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': input_text
                }
            ]
        )

        # Extract clean output (remove thinking blocks)
        clean_output = extract_clean_output(response.message.content)

        if verbose:
            print(f"\nItem {i} - Model: {model}")
            print("Input Prompt:")
            print(input_text)
            print("Model Response:")
            print(response.message.content)
            print("Clean Output:")
            print(clean_output)
            print("Out Transfer Field:")
            print(out_transfer_field.format(**dataset[i]))
            print("-" * 40)

        if out_transfer_field.startswith(">>NOT_EQ_DROP<<"):
            expected = out_transfer_field[15:]  # Remove ">>NOT_EQ_DROP<<"
            if clean_output.strip() != expected.format(**dataset[i]).strip():
                rows_to_remove.append(i)
                verify_counter_bad += 1
                continue

            verify_counter_good += 1

        elif out_transfer_field.startswith(">>VERIFY<<"):
            ge, le, se = parse_errors(clean_output)

            if ge > 0 or le > 0 or se > 0:
                rows_to_remove.append(i)
                verify_counter_bad += 1
                continue
            
            verify_counter_good += 1

        else:
            if out_transfer_field not in dataset.column_names:
                dataset = dataset.add_column(out_transfer_field, [None] * len(dataset))

            data_to_write.append(clean_output)

    # Remove rows by selecting indices to keep (Dataset has `select`, not `remove_rows`)
    if rows_to_remove:
        remove_set = set(rows_to_remove)
        keep_indices = [idx for idx in range(len(dataset)) if idx not in remove_set]
        dataset = dataset.select(keep_indices)

    if out_transfer_field.startswith(">>VERIFY<<") or out_transfer_field.startswith(">>NOT_EQ_DROP<<"):
        total = verify_counter_good + verify_counter_bad
        pct = (verify_counter_good / total * 100) if total > 0 else 0
        print(f"Verification results: {verify_counter_good} good, {verify_counter_bad} bad -> {pct}% good.")
    
    if len(data_to_write) > 0:
        dataset = dataset.remove_columns(out_transfer_field) if out_transfer_field in dataset.column_names else dataset
        dataset = dataset.add_column(out_transfer_field, data_to_write)

    return dataset

if __name__ == "__main__":
    args = parseCliArgs()
    
    print("Ollama Host:", args.ollama_host)
    print("Hugging Face Source:", args.hf_source)
    print("Hugging Face Output:", args.hf_output)
    print("Number of Stages:", args.stages)

    if args.prompts:
        for i, prompt in enumerate(args.prompts, 1):
            print(f"Stage {i} Prompt: {prompt}")

    if args.models:
        for i, model in enumerate(args.models, 1):
            print(f"Stage {i} Model: {model}")

    if args.out_transfer_fields:
        for i, field in enumerate(args.out_transfer_fields, 1):
            print(f"Stage {i} Out Transfer Field: {field}")

    print("Verbose:", args.verbose)
    if args.start_index > 0 or args.limit:
        print(f"Processing range: start_index={args.start_index}, limit={args.limit}")

    # load dataset from hf
    dataset_dict = load_dataset(args.hf_source, token=args.hf_token)
    if args.verbose:
        print("Loaded dataset:", dataset_dict)
    
    # Get the first split (usually 'train')
    split_name = list(dataset_dict.keys())[0] if isinstance(dataset_dict, dict) else 'train'
    dataset = dataset_dict[split_name] if isinstance(dataset_dict, dict) else dataset_dict

    # Slice dataset based on start_index and limit
    end_index = None
    if args.limit:
        end_index = args.start_index + args.limit
    else:
        end_index = len(dataset)
    
    # Select only the requested range
    dataset = dataset.select(range(args.start_index, min(end_index, len(dataset))))
    
    if args.verbose:
        print(f"Processing {len(dataset)} items from index {args.start_index} to {min(end_index, len(dataset)) - 1}")

    # Initialize Ollama client
    client = Client(
        host=args.ollama_host
    )

    # for each stage, process the dataset
    for stage in range(args.stages):
        prompt   = args.prompts[stage] if args.prompts else None
        model    = args.models[stage]  if args.models  else None
        outField = args.out_transfer_fields[stage] if args.out_transfer_fields else None

        if args.verbose:
            print(f"Processing Stage {stage + 1} with Model: {model}, Out Transfer Field: {outField} and Prompt: {prompt}")

        dataset = process_dataset_with_model(dataset, model, prompt, outField, lang=args.to_lang, client=client, verbose=args.verbose)

    #push dataset to hf
    dataset.push_to_hub(args.hf_output, token=args.hf_token)
    if args.verbose:
        print("Pushed dataset to Hugging Face Hub:", args.hf_output) 