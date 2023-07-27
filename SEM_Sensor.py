import cv2
import matplotlib.pyplot as plt
import os


def read_yolo_annotations(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    annotations = [line.strip().split() for line in lines]
    return annotations


def plot_annotations_with_widths(image_path, annotations, HFW):
    img = cv2.imread(image_path)
    image_width, image_height = img.shape[1], img.shape[0]

    scale_factor_x = (HFW * 1000) / image_width  # Scale factor in X direction (nanometer/pixel)
    scale_factor_y = (HFW * 1000) / image_height  # Scale factor in Y direction (nanometer/pixel)

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), extent=[0, image_width, image_height, 0])

    width = []  # list to store the widths
    height = []  # list to store the heights

    X_positions = []
    Y_positions = []

    image_name = os.path.basename(image_path).split('.')[0]
    result_dir = os.path.join(os.path.dirname(image_path), image_name)
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    for k, annotation in enumerate(annotations):
        class_id, center_x, center_y, box_width, box_height = map(float, annotation)
        center_x_pixels = center_x * image_width
        center_y_pixels = center_y * image_height
        bbox_width_pixels = box_width * image_width
        bbox_height_pixels = box_height * image_height

        X_positions.append(center_x_pixels * scale_factor_x)
        Y_positions.append(center_y_pixels * scale_factor_y)

        bbox_width_real = bbox_width_pixels * scale_factor_x
        bbox_height_real = bbox_height_pixels * scale_factor_y

        width.append(bbox_width_real)  # Add the width to the list
        height.append(bbox_height_real)  # Add the height to the list

        #print(f'Object {k + 1}: width = {bbox_width_real:.2f} nm, height = {bbox_height_real:.2f} nm')

        # Calculate the coordinates for the bounding box in the upper-left corner format (xmin, ymin)
        xmin = int(center_x_pixels - bbox_width_pixels / 2)
        ymin = int(center_y_pixels - bbox_height_pixels / 2)

        # Draw bounding box
        rect = plt.Rectangle((xmin, ymin), bbox_width_pixels, bbox_height_pixels, edgecolor='r', linewidth=1.5,
                             fill=False)
        ax.add_patch(rect)

    # Save the plot with the image name without sizes
    plt.savefig(os.path.join(result_dir, f'{image_name}_annotations_no_sizes.png'), bbox_inches='tight',
                dpi=300)  # Increase dpi to 300 or higher for better resolution

    # Continue to annotate with real-world width and height
    for k, annotation in enumerate(annotations):
        class_id, center_x, center_y, box_width, box_height = map(float, annotation)
        center_x_pixels = center_x * image_width
        center_y_pixels = center_y * image_height
        bbox_width_pixels = box_width * image_width
        bbox_height_pixels = box_height * image_height

        bbox_width_real = bbox_width_pixels * scale_factor_x
        bbox_height_real = bbox_height_pixels * scale_factor_y

        # Calculate the coordinates for the bounding box in the upper-left corner format (xmin, ymin)
        xmin = int(center_x_pixels - bbox_width_pixels / 2)
        ymin = int(center_y_pixels - bbox_height_pixels / 2)

        # Add real-world width annotation
        ax.text(xmin, ymin - 10, f'{bbox_width_real:.2f} nm', color='yellow', fontsize=12)

    plt.title('Image with bounding boxes and sizes')
    plt.axis('off')  # Turn off axis for a cleaner visualization

    # Save the plot with the image name with sizes
    plt.savefig(os.path.join(result_dir, f'{image_name}_annotations.png'), bbox_inches='tight',
                dpi=300)  # Increase dpi to 300 or higher for better resolution
    plt.show()

    return width, height, X_positions, Y_positions


def analyze_image(image_path, yolo_annotations_path, HFW=8.29):
    annotations = read_yolo_annotations(yolo_annotations_path)
    width, height, X_positions, Y_positions = plot_annotations_with_widths(image_path, annotations, HFW)

    # Define your datasets and corresponding titles and colors
    datasets = [width, height, X_positions, Y_positions]
    titles = ['Object Widths', 'Object Heights', 'Object X Positions', 'Object Y Positions']
    colors = ['blue', 'green', 'purple', 'orange']

    image_dir = os.path.dirname(image_path)  # gets the directory of the image
    image_name = os.path.basename(image_path).split('.')[0]

    # creates a new directory with the image name inside the image directory
    result_dir = os.path.join(image_dir, image_name)
    os.makedirs(result_dir, exist_ok=True)

    # Loop through the datasets and create/save the plots
    for data, title, color in zip(datasets, titles, colors):
        plt.figure(figsize=(10, 5))
        plt.hist(data, bins=50, color=color, edgecolor='black')
        plt.title(f'Histogram of {title}')
        plt.xlabel(f'{title} (nm)')
        plt.ylabel('Count')
        plt.savefig(os.path.join(result_dir, f'histogram_{image_name}_{title.lower().replace(" ", "_")}.png'))
        plt.show()

    output_file_path = os.path.join(result_dir, "object_information.txt")  # save the text file in the image directory

    output_file_path = "object_information.txt"
    object_info = f"Number of objects: {len(annotations)}\n"
    object_info += f"X position range: min = {min(X_positions):.2f} nm, max = {max(X_positions):.2f} nm\n"
    object_info += f"Y position range: min = {min(Y_positions):.2f} nm, max = {max(Y_positions):.2f} nm\n"

    with open(output_file_path, 'w') as file:
        file.write(object_info)

    return width, height, X_positions, Y_positions, object_info