#testline

import time 
import gradio as gr
import json
import os
from psd_tools import PSDImage
from PIL import Image 

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
            if file.endswith(".psd"):
                psd_files.append(os.path.join(root, file))
    return psd_files

temp_path = "./temp/temp.json"
temp_psd_path = "./temp/psd_path.txt"
temp_line_path = "./temp/line_dest.txt"
temp_color_path = "./temp/color_dest.txt"
temp_continue_path = "./temp/continue.txt"
temp_message_path = "./temp/message.txt"

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
        
        with open(temp_continue_path, "r", encoding="UTF-8-sig") as f:
            continue_path = f.read()
            f.close()
        #get the path
        global psd_path, psd_bbox
        if path.endswith(".psd"):
            psd_path = path
            psd = PSDImage.open(path)
        else:
            psd_path = get_all_psd_files(path)
            for idx, psd in enumerate(psd_path):
                if psd == continue_path:
                    psd_path = psd_path[idx:]
                    break
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

        os.system("sed -i '1s/^/import time \\n/' color_line.py")
        os.system("sed -i '1d' color_line.py")

        

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
 
    def get_file_name(psd_path: str, save_path: str) -> str:
        file_name = ""
        for folder in psd_path.split("/"):
            file_name = file_name + folder.replace(".", "_") + "_"
        file_name = file_name[1:-1]

        file_path = save_path + file_name + ".png"
        
        return file_path

    def composite_images_first(psd_path: str, checkbox_list: list, save_path: str) -> list:
        pixel_layers = get_pixel_layers_path(psd_path)
        pixel_layers = pixel_layers[::-1]
        selected_layers = [layer for layer, selected in zip(pixel_layers, checkbox_list) if selected]
        composite_images_list = []
        for layer in selected_layers[::-1]:
            layer.visible = "visible"
            image = layer.compose(psd_bbox)
            composite_images_list.append(image)
        for image in composite_images_list[1:]:
            composite_images_list[0].paste(image, (0, 0), image)
        image = composite_images_list[0]

        if save_path:
            file_path = get_file_name(psd_path, save_path)
            image.save(file_path) 

        return selected_layers, image
    
    def composite_from_first(argument_list: str):
        pixel_layers = get_pixel_layers_path(argument_list[0])
        pixel_layers = pixel_layers[::-1]
        composite_images_list = []
        for selected_layer in argument_list[1][::-1]:
            for layer in pixel_layers:
                if layer.name == selected_layer.name and layer.parent.name == selected_layer.parent.name:
                    print(layer.name)
                    print(selected_layer.name)
                    print(layer.parent.name)
                    print(selected_layer.parent.name)
                    layer.visible = "visible"
                    composite_images_list.append(layer.compose(psd_bbox))
        if len(composite_images_list) != len(argument_list[1]):
            return ("layer structure is different", "")
        
        for image in composite_images_list[1:]:
            composite_images_list[0].paste(image, (0, 0), image)

        image = composite_images_list[0]

        if argument_list[2]:
            file_path = get_file_name(argument_list[0], argument_list[2])
            image.save(file_path)

        return image, argument_list[0]

    #applying multiprocessing
    import multiprocessing

    def multi_process_layers(pool: multiprocessing.Pool, psd_path: list, selected_layers: list, save_path: list):
        selected_layers_list = [selected_layers for psd in psd_path]
        print(selected_layers)
        save_path_list = [save_path for _ in psd_path]
        arg_list = zip(psd_path, selected_layers_list, save_path_list)
        result = pool.map(composite_from_first, arg_list)
        print(result)
        ordered_result = []
        for psd in psd_path:
            for image_tuple in result:
                if image_tuple[1] == psd:
                    ordered_result.append(image_tuple[0])
                elif image_tuple[0] == "layer structure is different":
                    ordered_result.append(image_tuple[0])
                    return ordered_result, psd
        return ordered_result, ""
        
    def extract_layers(psd_path, checkbox_list: list, save_path: str, global_start_idx: int, starting_psd: str):
        global selected_layers
        local_psd_path = psd_path
        print(local_psd_path)
        images = []
        if isinstance(local_psd_path, list):
            start_idx = 0
            
            if global_start_idx == 0:
                selected_layers, image = composite_images_first(starting_psd, checkbox_list, save_path)
                images.append(image)
                start_idx = 1
            else:
                pixel_layers = get_pixel_layers_path(starting_psd)
                pixel_layers = pixel_layers[::-1]
                selected_layers = [layer for layer, selected in zip(pixel_layers, checkbox_list) if selected]
            
            num_process = len(psd_path)

            end_idx = start_idx + num_process

            pool = multiprocessing.Pool(processes=len(local_psd_path[start_idx:end_idx]))

            result, psd = multi_process_layers(pool, local_psd_path[start_idx:end_idx], selected_layers, save_path)
            
            if "layer structure is different" in result:
                images.extend(result[:-1])
                return images, psd
            
            images.extend(result)                 

        elif isinstance(psd_path, str):
            selected_layers, image = composite_images_first(local_psd_path, checkbox_list, save_path)
            images = [image]
        with open(temp_continue_path, "w", encoding="UTF-8-sig") as f:
            f.write("")
            f.close()

        return images, "conversion completed"

    def extract_both(*extraction_list):
        global psd_path 
        num_process = multiprocessing.cpu_count()
        start_idx = 0
        end_idx = start_idx + num_process

        line_checkbox_list = extraction_list[:len(checkbox_list_line)]
        line_dest_box = extraction_list[len(checkbox_list_line)]

        color_checkbox_list = extraction_list[len(checkbox_list_line) + 1:-1]
        color_dest_box = extraction_list[-1]

        try:
            while end_idx < len(psd_path):
                temp_psd_path = psd_path[start_idx:end_idx]

                line_images, line_limit = extract_layers(temp_psd_path, line_checkbox_list, line_dest_box, start_idx, psd_path[0])
                
                if line_limit != "conversion completed":
                    line_limit_idx = psd_path.index(line_limit)
                    psd_path = psd_path[:line_limit_idx]

                color_images, color_limit = extract_layers(temp_psd_path, color_checkbox_list, global_start_idx=start_idx, save_path=None, starting_psd=psd_path[0])

                make_message = lambda psd: "The layer structure is different" + f" from \"{psd}\"." \
                                + " To continue from the file, please load the psd file again."
                
                def save_make_message(psd):
                    with open(temp_continue_path, "w", encoding="UTF-8-sig") as f:
                        f.write(psd)
                        f.close()   
                    return make_message(psd)
                
                
                for line_image, color_image, psd in zip(line_images, color_images, temp_psd_path):
                    color_image.paste(line_image, (0, 0), line_image)
                    file_path = get_file_name(psd + "/color", color_dest_box)
                    color_image.save(file_path)
                
                if color_limit != "conversion completed":
                    message = save_make_message(color_limit)
                    return message
                elif color_limit == "conversion completed" and line_limit != "conversion completed":
                    message = save_make_message(line_limit)
                    return message
                else: 
                    message = "conversion completed"

                start_idx += num_process
                end_idx += num_process

                if end_idx >= len(psd_path):
                    temp_psd_path = psd_path[start_idx:]

                    line_checkbox_list = extraction_list[:len(checkbox_list_line)]
                    line_dest_box = extraction_list[len(checkbox_list_line)]

                    line_images, line_limit = extract_layers(temp_psd_path, line_checkbox_list, line_dest_box, start_idx, psd_path[0])
                    
                    if line_limit != "conversion completed":
                        line_limit_idx = psd_path.index(line_limit)
                        psd_path = psd_path[:line_limit_idx]

                    color_checkbox_list = extraction_list[len(checkbox_list_line) + 1:-1]
                    color_dest_box = extraction_list[-1]

                    color_images, color_limit = extract_layers(temp_psd_path, color_checkbox_list, global_start_idx=start_idx, save_path=None, starting_psd=psd_path[0])

                    make_message = lambda psd: "The layer structure is different" + f" from \"{psd}\"." \
                                    + " To continue from the file, please load the psd file again."

                    for line_image, color_image, psd in zip(line_images, color_images, temp_psd_path):
                        color_image.paste(line_image, (0, 0), line_image)
                        file_path = get_file_name(psd + "/color", color_dest_box)
                        color_image.save(file_path)
                    
                    if color_limit != "conversion completed":
                        message = save_make_message(color_limit)
                        return message
                    elif color_limit == "conversion completed" and line_limit != "conversion completed":
                        message = save_make_message(line_limit)
                        return message
                    else: 
                        message = "conversion completed"
                    
            return message

        except NameError:
            return "Please load the psd file again, then try again."
    
    button2.click(extract_both, inputs=extraction_list, outputs=status, concurrency_limit=1, show_progress=True)

if __name__ == "__main__":
    demo.launch()