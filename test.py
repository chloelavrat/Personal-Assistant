import sys
import llamacpp


def progress_callback(progress):
    print("Progress: {:.2f}%".format(progress * 100))
    sys.stdout.flush()


params = llamacpp.InferenceParams.default_with_callback(progress_callback)
params.path_model = './src/models/7B/ggml-model-q4_1.bin'
model = llamacpp.LlamaInference(params)

prompt = "A llama is a"
prompt_tokens = model.tokenize(prompt, True)
model.update_input(prompt_tokens)

model.ingest_all_pending_input()

#model.print_system_info()
for i in range(20):
    model.eval()
    token = model.sample()
    text = model.token_to_str(token)
    print(text, end="")
    
# Flush stdout
sys.stdout.flush()

#model.print_timings()
