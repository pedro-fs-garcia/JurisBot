from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import PeftModel

MODEL_DIR = "zephyr-juridico-lora"

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
base_model = AutoModelForCausalLM.from_pretrained("HuggingFaceH4/zephyr-7b-beta", device_map="auto", load_in_4bit=True)
model = PeftModel.from_pretrained(base_model, MODEL_DIR)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")

prompt = "<|user|> Quais são os requisitos para cassação de mandato por infidelidade partidária?\n<|assistant|>"
output = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7)[0]["generated_text"]

print(output)
