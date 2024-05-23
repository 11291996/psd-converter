#testline

import time 
import gradio as gr
import json
import os
from psd_tools import PSDImage
from PIL import Image 
import natsort 

Image.MAX_IMAGE_PIXELS = None

#check layers 
def get_layer_tree(psd: PSDImage) -> list:
    #reverse the order of layers
    psd._layers.reverse()
    layer_tree = []
    for layer in psd._layers:
        if layer.kind == "group":
            layer_tree.append((layer.name + "(folder)", get_layer_tree(layer)))
        else:
            layer_tree.append(layer.name)
    return layer_tree

def create_blocks(layer_list, checkbox_list: list):
    for layer in layer_list:
        if isinstance(layer, str):
            checkbox_list.append(gr.Checkbox(label=layer))
        elif isinstance(layer[1], list):
            with gr.Accordion(label=layer[0], open=False):
                create_blocks(layer[1], checkbox_list)
        else:
            checkbox_list.append(gr.Checkbox(label=layer[0]))
    return checkbox_list

def create_blocks_path(path, block_title: str):
    checkbox_list = []
    with open(path, "r", encoding="UTF-8-sig") as f:
        dict = json.load(f)
    layer_list = [list(item) for item in dict.items()]
    with gr.Accordion(block_title, open=False) as check_boxes:
        check_box_list = create_blocks(layer_list, checkbox_list)
    return check_boxes, check_box_list

def get_pixel_layers_path(psd_path: str) -> list:
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

def get_all_psd_files(path):
    psd_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".psd") or file.endswith(".psb"):
                psd_files.append(os.path.join(root, file))
    return psd_files

def get_file_name(psd_path: str, save_path: str) -> str:
    file_name = ""
    for folder in psd_path.split("/"):
        file_name = file_name + folder.replace(".", "_") + "_"
    file_name = file_name[1:-1]

    file_path = save_path + file_name + ".png"
    
    return file_path

temp_path = "./temp/temp.json"
temp_psd_path = "./temp/psd_path.txt"
temp_line_path = "./temp/line_dest.txt"
temp_color_path = "./temp/color_dest.txt"
temp_continue_path = "./temp/continue.txt"
temp_message_path = "./temp/message.txt"
temp_comb_path = "./temp/comb.txt"

with gr.Blocks(title="PSD Converter") as demo:

    gr.Markdown(
    """
    # PSD Pipeline
    """
    )

    with open(temp_psd_path, "r", encoding="UTF-8-sig") as f:
        psd_paths = f.read()
        f.close()

    path_box = gr.Textbox(label="enter the path of a psd file or a folder with psd files only", value=psd_paths)
    
    def create_json(path, line_dest, color_dest):
        
        with open(temp_comb_path, "r", encoding="UTF-8-sig") as f:
            comb_list = f.readlines()
            f.close()

        with open(temp_continue_path, "r", encoding="UTF-8-sig") as f:
            continue_path = f.read()
            f.close()
        
        #get the path
        global psd_path, psd_bbox
        if path.endswith(".psd") or path.endswith(".psb"):
            psd_path = [path]
            psd = PSDImage.open(path)
        else:
            if len(comb_list) != 0:
                print(comb_list)
                psd_path = []
                for psd in comb_list:
                    psd = psd.strip()
                    psd_path.append(psd)
            else:
                psd_path = get_all_psd_files(path)
                psd_path = natsort.natsorted(psd_path)
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
        with open(temp_psd_path, "w", encoding="UTF-8-sig") as f:
            f.writelines(path)
            f.close()
        with open(temp_line_path, "w", encoding="UTF-8-sig") as f:
            f.writelines(line_dest)
            f.close()
        with open(temp_color_path, "w", encoding="UTF-8-sig") as f:
            f.writelines(color_dest)
            f.close()
        if continue_path == "":
            with open(temp_message_path, "w", encoding="UTF-8-sig") as f:
                if isinstance(psd_path, list):
                    f.write(f"psd files loaded successfully. please select the layers to convert from \"{psd_path[0]}\"")
                if isinstance(psd_path, str):
                    f.write(f"psd file loaded successfully.")
                f.close()
        if continue_path != "":
            with open(temp_message_path, "w", encoding="UTF-8-sig") as f:
                f.write(f"continuing from the last file \"{continue_path}\"")
                f.close()
        #add something to this code then delete it to reload the demo
        #if os is mac os
        #os.system("sed -i '.bak' '1s/^/import time \\n/' test.py")
        #os.system("sed -i '.bak' '1d' test.py")
        #for linux 
        os.system("sed -i '1s/^/import time \\n/' color_line_ver2.py")
        os.system("sed -i '1d' color_line_ver2.py")

    with open(temp_line_path, "r", encoding="UTF-8-sig") as f:
        line_path = f.read()
        f.close()
    
    with open(temp_color_path, "r", encoding="UTF-8-sig") as f:
        color_path = f.read()
        f.close()
    
    line_dest_box = gr.Textbox(label="enter the save path for line layers", value=line_path)
    color_dest_box = gr.Textbox(label="enter the save path for color layers", value=color_path)

    button = gr.Button("Load PSD")

    line_title = "select line layers"
    color_title = "select color layers"
    checkboxes_line, checkbox_list_line = create_blocks_path(temp_path, line_title)
    checkboxes_color, checkbox_list_color = create_blocks_path(temp_path, color_title)
    button2 = gr.Button("Convert")
    
    with open(temp_message_path, "r", encoding="UTF-8-sig") as f:
        message = f.read()
        f.close()
    
    status = gr.Textbox(label="status of conversion", value=message)
    
    button.click(create_json, inputs=[path_box, line_dest_box, color_dest_box], outputs=status)

    extraction_list = checkbox_list_line + [line_dest_box] + checkbox_list_color + [color_dest_box]

    def extract_both(*extraction_list):
        
        pixel_layers = get_pixel_layers_path(psd_path[0])
        pixel_layers = pixel_layers[::-1]

        line_checkbox_list = extraction_list[:len(checkbox_list_line)]
        line_dest_box = extraction_list[len(checkbox_list_line)]
        color_checkbox_list = extraction_list[len(checkbox_list_line) + 1:-1]
        color_dest_box = extraction_list[-1]

        selected_line_layers = [layer for layer, checkbox in zip(pixel_layers, line_checkbox_list) if checkbox]
        selected_color_layers = [layer for layer, checkbox in zip(pixel_layers, color_checkbox_list) if checkbox]

        print(f"selected line layers: {selected_line_layers}")
        print(f"selected color layers: {selected_color_layers}")

        unmatching_psd = []

        for psd in psd_path:
            pixel_layers = get_pixel_layers_path(psd)
            selected_psd_layers = []
            for line_layer in selected_line_layers:
                for layer in pixel_layers:
                    if layer.name == line_layer.name and layer.parent.name == line_layer.parent.name:
                        selected_psd_layers.append(layer)
                        print(line_layer.name)
            for color_layer in selected_color_layers:
                for layer in pixel_layers:
                    if layer.name == color_layer.name and layer.parent.name == color_layer.parent.name:
                        selected_psd_layers.append(layer)
                        print(color_layer.name)
            if len(selected_psd_layers) == len(selected_line_layers) + len(selected_color_layers):
                print(selected_psd_layers[:len(selected_line_layers)][::-1])
                for layer in selected_psd_layers[:len(selected_line_layers)][::-1]:
                    if layer == selected_psd_layers[0]:
                        line_page = layer.compose(psd_bbox)
                    else:
                        next_page = layer.compose(psd_bbox)
                        line_page.paste(next_page, (0, 0), next_page)
                line_page.save(get_file_name(psd, line_dest_box))
                print(selected_psd_layers[len(selected_line_layers):][::-1])
                for layer in selected_psd_layers[len(selected_line_layers):][::-1]:
                    if layer == selected_psd_layers[len(selected_line_layers):][::-1][0]:
                        color_page = layer.compose(psd_bbox)
                    else:
                        next_page = layer.compose(psd_bbox)
                        color_page.paste(next_page, (0, 0), next_page)
                color_page.paste(line_page, (0, 0), line_page)
                color_page.save(get_file_name(psd, color_dest_box))
            else: 
                print(f"{psd} does not match with {psd_path[0]}")
                unmatching_psd.append(psd)
        
        with open(temp_comb_path, "w", encoding="UTF-8-sig") as f:
            f.writelines(unmatching_psd)
            f.close()

        if unmatching_psd != []:
            return f"some psd files do not match with {psd_path[0]}. please reload and select the layers again"
        else:
            return "conversion successful"
    
    button2.click(extract_both, inputs=extraction_list, outputs=status, concurrency_limit=1, show_progress=True)

if __name__ == "__main__":
    demo.launch()