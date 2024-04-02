import gradio as gr
import json
import os
from psd_tools import PSDImage

#check layers 
def get_layer_tree(psd: PSDImage) -> list:
    #reverse the order of layers
    psd._layers.reverse()
    layer_tree = []
    for layer in psd._layers:
        if layer.kind == "group":
            layer_tree.append((layer.name, get_layer_tree(layer)))
        else:
            layer_tree.append(layer.name)
    return layer_tree

checkbox_list = []

def create_blocks(layer_list):
    for layer in layer_list:
        if isinstance(layer, str):
            checkbox_list.append(gr.Checkbox(label=layer))
        elif isinstance(layer[1], list):
            with gr.Accordion(label=layer[0], open=False):
                create_blocks(layer[1])
        else:
            checkbox_list.append(gr.Checkbox(label=layer[0]))
    return checkbox_list

def create_blocks_path(path):
    with open(path, "r", encoding="UTF-8-sig") as f:
        dict = json.load(f)
    layer_list = [list(item) for item in dict.items()]
    with gr.Accordion("layer check boxes", open=False) as check_boxes:
        check_box_list = create_blocks(layer_list)
    return check_boxes, check_box_list

def get_pixel_layers_path(psd_path):
    psd = PSDImage.open(psd_path)
    return get_pixel_layers(psd)
    
def get_pixel_layers(psd):
    pixel_layers = []
    for layer in psd._layers:
        if layer.is_group():
            pixel_layers.extend(get_pixel_layers(layer))
        else:
            pixel_layers.append(layer)
    return pixel_layers

temp_path = "./temp/temp.json"

with gr.Blocks(title="PSD Converter") as demo:
    gr.Markdown(
    """
    # PSD Pipeline
    """
    )
    path_box = gr.Textbox(label="enter path of a psd file or a folder with psd files only", value="/home/paneah/auto_clipimage_conversion/test_data/test_folder/")
    def create_json(path):
        #get the path
        global psd_path, psd_bbox
        if path.endswith(".psd"):
            psd_path = path
            psd = PSDImage.open(path)
        else:
            psd_path = [path + item for item in os.listdir(path)]
            psd = PSDImage.open(psd_path[0])
        psd_bbox = psd.bbox
        layer_tree = get_layer_tree(psd)
        layer_dict = {}
        for layer in layer_tree:
            if isinstance(layer, tuple):
                layer_dict[layer[0]] = layer[1] 
            else:
                layer_dict[layer] = None
        with open(temp_path, "w", encoding="UTF-8-sig") as f:
            f.write(json.dumps(layer_dict, ensure_ascii=False, indent=4))
        #add something to this code then delete it to reload the demo
        #if os is mac os
        #os.system("sed -i '.bak' '1s/^/import time \\n/' test.py")
        #os.system("sed -i '.bak' '1d' test.py")
        #for linux 
        os.system("sed -i '1s/^/import time \\n/' main.py")
        os.system("sed -i '1d' main.py")
    button = gr.Button("Load PSD")
    button.click(create_json, inputs=path_box)
    checkboxes, checkbox_list = create_blocks_path(temp_path)
    button2 = gr.Button("Convert")
    status = gr.Textbox(label="status of convert")

    def composite_images(psd_path, checkbox_list, idx):
        pixel_layers = get_pixel_layers_path(psd_path)
        pixel_layers = pixel_layers[::-1]
        selected_layers = [layer for layer, selected in zip(pixel_layers, checkbox_list) if selected]
        composite_images_list = []
        for layer in selected_layers:
            image = layer.compose(psd_bbox)
            composite_images_list.append(image)
        for image in composite_images_list[1:]:
            composite_images_list[0].paste(image, (0, 0), image)
        composite_images_list[0].save(f"./temp/output{idx}.png")

    def extract_layers(*checkbox_list):
        if isinstance(psd_path, list):
            for idx, psd in enumerate(psd_path):
                composite_images(psd, checkbox_list, idx)
        elif isinstance(psd_path, str):
            composite_images(psd_path, checkbox_list, 0)
        return "convert done"
    button2.click(extract_layers, inputs=checkbox_list, outputs=status, concurrency_limit=1, show_progress=True)

if __name__ == "__main__":
    demo.launch()