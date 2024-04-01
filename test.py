import gradio as gr
import json
import os


psd1 = {
    "group1": ["layer1", "layer2", "layer3"],
    "group2": ["layer4", "layer5", "layer6"],
    "group3": ["layer7", "layer8"]
}

psd2 = {
    "line": ["layer1", "layer2"],
    "color": ["layer3", "layer4"],
    "background": ["layer5", "layer6"]
}


def create_blocks(path):
    with open(path, "r") as f:
        data = json.load(f)
    with gr.Accordion("fake check boxes") as check_boxes:
        for item in data.items():
            if isinstance(item, tuple):
                with gr.Accordion(label=item[0], open=False):
                    for subitem in item[1]:
                        gr.Checkbox(label=f"{subitem}")
    return check_boxes

fake_path = "./temp.json"


with gr.Blocks(title="PSD Converter") as demo:
    gr.Markdown(
    """
    # PSD Pipeline
    """
    )
    path_box = gr.Textbox(label="enter path", value="./psd1.psd")
    def create_json(path):
        global flag
        if path == "./psd1.psd":
            data = psd1
        elif path == "./psd2.psd":
            data = psd2
        with open(fake_path, "w") as f:
            json.dump(data, f)
        #add something to this code, then delete it
        os.system("sed -i '.bak' '1s/^/import time \\n/' test.py")
        os.system("sed -i '.bak' '1d' test.py")
    button = gr.Button("Load PSD") 
    button.click(create_json, inputs=path_box)
    create_blocks(fake_path)

if __name__ == "__main__":
    demo.launch(server_port=7860)