from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("modelo_juridico")
model = AutoModelForCausalLM.from_pretrained("modelo_juridico")

inputs = tokenizer("Explique o que é habeas corpus", return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

