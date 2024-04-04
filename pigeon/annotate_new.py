"""
This module provides functions for annotating data and organizing images based on their annotations.

Improvements over annotate.py:
- Improved user interface with buttons and interactive widgets.
- Added ability to save annotations as a JSON file.
- Added ability to display the progress of annotation.
- Added ability to display the number of examples annotated and remaining.
- Added ability to display the current example being annotated.
- Added ability to display the current label being annotated.
- Added ability to Add new Class while annotating.
- Added ability to update the annotations in real-time.
- Added ability to display the previous and next examples.
- Added ability to organize images based on their annotations.
- Added option to copy or move images to the output directory.


"""



# Rest of the code...
from IPython.display import HTML
import random
import functools
from IPython.display import display, clear_output
from ipywidgets import Button, Dropdown, HTML, HBox, IntSlider, FloatSlider, Textarea, Output
import json
import os
import shutil






def save_annotations(annotations):
    """
    Save the annotations to a JSON file.

    Parameters:
    annotations (list): A list of tuples representing the annotations.

    Returns:
    None
    """
    with open('annotations.json', 'w') as f:
        annotations_dict = {"annotations" : {item[0]: item[1] for item in annotations}}
        json.dump(annotations_dict, f)




def annotate(examples,
             options=None,
             shuffle=False,
             include_skip=True,
             display_fn=display):
    """
    Build an interactive widget for annotating a list of input examples.

    Parameters
    ----------
    examples: list(any), list of items to annotate
    options: list(any) or tuple(start, end, [step]) or None
             if list: list of labels for binary classification task (Dropdown or Buttons)
             if tuple: range for regression task (IntSlider or FloatSlider)
             if None: arbitrary text input (TextArea)
    shuffle: bool, shuffle the examples before annotating
    include_skip: bool, include option to skip example while annotating
    display_fn: func, function for displaying an example to the user

    Returns
    -------
    annotations : list of tuples, list of annotated examples (example, label)
    """
    examples = list(examples)
    if shuffle:
        random.shuffle(examples)

    annotations = []
    current_index = -1

    def set_label_text():
        nonlocal count_label
        count_label.value = '{} examples annotated, {} examples left'.format(
            len(annotations), len(examples) - current_index
        )

    def show_next():
        nonlocal current_index
        current_index += 1
        set_label_text()
        if current_index >= len(examples):
            for btn in buttons:
                btn.disabled = True
            print('Annotation done.')
            save_annotations(annotations)  # Save annotations as JSON
            return
        with out:
            clear_output(wait=True)
            display_fn(examples[current_index])
            if examples[current_index] in [item[0] for item in annotations]:
                for btn in buttons:
                    if btn.description == annotations[current_index][1]:
                        btn.button_style = 'success'  # Change button style to green if image is already annotated
                    else:
                        btn.button_style = 'primary'  # Change button style to default if image is not annotated
            else:
                for btn in buttons:
                    btn.button_style = 'primary'  # Change button style to default if image is not annotated

    def show_previous():
        nonlocal current_index
        current_index -= 1
        set_label_text()
        if current_index < 0:
            current_index = 0
        with out:
            clear_output(wait=True)
            display_fn(examples[current_index])
            if examples[current_index] in [item[0] for item in annotations]:
                for btn in buttons:
                    if btn.description == annotations[current_index][1]:
                        btn.button_style = 'success'  # Change button style to green if image is already annotated
                    else:
                        btn.button_style = 'primary'  # Change button style to default if image is not annotated
            else:
                for btn in buttons:
                    btn.button_style = 'primary'  # Change button style to default if image is not annotated

    from IPython.display import HTML  # Add the missing import statement

    def add_annotation(annotation):
        annotations.append((examples[current_index], annotation))
        save_annotations(annotations)
        show_next()

    def skip(btn):
        show_next()

    count_label = HTML()
    set_label_text()
    display(count_label)

    if type(options) == list:
        task_type = 'classification'
    elif type(options) == tuple and len(options) in [2, 3]:
        task_type = 'regression'
    elif options is None:
        task_type = 'captioning'
    else:
        raise Exception('Invalid options')

    buttons = []

    # Add text input box
    text_input = Textarea()
    btn_add = Button(description='Add')
    def on_add(btn):
        label = text_input.value
        options = [label]  # Replace the options list with a single label
        btn_label = Button(description=label)
        def on_click(label, btn):
            add_annotation(label)
        btn_label.on_click(functools.partial(on_click, label))
        buttons.append(btn_label)
        display(btn_label)
    btn_add.on_click(on_add)
    display(HBox([text_input, btn_add]))  # Fix: Pass a tuple of the Textarea and Button to the HBox constructor

    # Add previous button
    btn_previous = Button(description='previous')
    btn_previous.on_click(lambda btn: show_previous())
    buttons.append(btn_previous)

    # Add next button
    btn_next = Button(description='next')
    btn_next.on_click(lambda btn: show_next())
    buttons.append(btn_next)

    if include_skip:
        btn = Button(description='skip')
        btn.on_click(skip)
        buttons.append(btn)

    if task_type == 'classification':
        use_dropdown = len(options) > 5

        if use_dropdown:
            dd = Dropdown(options=options)
            display(dd)
            btn = Button(description='submit')
            def on_click(btn):
                add_annotation(dd.value)
            btn.on_click(on_click)
            buttons.append(btn)

        else:
            for label in options:
                btn = Button(description=label)
                def on_click(label, btn):
                    add_annotation(label)
                btn.on_click(functools.partial(on_click, label))
                buttons.append(btn)

    elif task_type == 'regression':
        target_type = type(options[0])
        if target_type == int:
            cls = IntSlider
        else:
            cls = FloatSlider
        if len(options) == 2:
            min_val, max_val = options
            slider = cls(min=min_val, max=max_val)
        else:
            min_val, max_val, step_val = options
            slider = cls(min=min_val, max=max_val, step=step_val)
        display(slider)
        btn = Button(description='submit')
        def on_click(btn):
            add_annotation(slider.value)
        btn.on_click(on_click)
        buttons.append(btn)

    else:
        ta = Textarea()
        display(ta)
        btn = Button(description='submit')
        def on_click(btn):
            add_annotation(ta.value)
        btn.on_click(on_click)
        buttons.append(btn)


    box = HBox(buttons)
    display(box)

    out = Output()
    display(out)

    show_next()

    save_annotations(annotations)
    
    return annotations



def organize_images(annotation_file, image_directory, output_directory, copy_images=False):
    """
    Organizes images based on their annotations.

    Parameters:
    annotation_file (str): The path to the JSON file containing the annotations.
    image_directory (str): The directory where the images are located.
    output_directory (str): The directory where the organized images will be saved.
    copy_images (bool, optional): If True, the images will be copied to the output directory. 
        If False, the images will be moved to the output directory. Defaults to False.
    """
    # Load annotations from JSON file
    with open(annotation_file, 'r') as f:
        annotations = json.load(f)['annotations']
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Iterate over annotations
    for image_name, label in annotations.items():
        # Create class directory if it doesn't exist
        class_directory = os.path.join(output_directory, str(label))
        if not os.path.exists(class_directory):
            os.makedirs(class_directory)
        
        # Get source and destination paths
        source_path = os.path.join(image_directory, image_name)
        destination_path = os.path.join(class_directory, image_name)
        
        # Copy or move the image
        if copy_images:
            shutil.copy(source_path, destination_path)
        else:
            shutil.move(source_path, destination_path)