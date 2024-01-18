def imshow(titles=None, images=None, size=5):
    '''This function plots 1 or more images read by OpenCV'''
    # If titles and images are not lists, convert them to lists
    if not isinstance(titles, list):
        titles = [titles]
    if not isinstance(images, list):
        images = [images]

    num_images = len(images)

    # Create a subplot with the desired number of columns
    fig, axes = plt.subplots(1, num_images, figsize=(size * num_images, size))

    # Ensure axes is always treated as a list
    if num_images == 1:
        axes = [axes]

    # Iterate through titles and images to display them
    for i in range(num_images):
        w, h = images[i].shape[0], images[i].shape[1]
        aspect_ratio = w / h
        axes[i].imshow(cv2.cvtColor(images[i], cv2.COLOR_BGR2RGB))
        axes[i].set_title(titles[i])
       # axes[i].axis('off')  # Turn off axis labels

    plt.show()
