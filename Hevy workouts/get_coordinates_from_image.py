import matplotlib.pyplot as plt
from PIL import Image

# Load the image
image_path = r'C:\Users\mikip\Downloads\human_body.jpg'
img = Image.open(image_path)

# Display the image
fig, ax = plt.subplots()
ax.imshow(img)

coords = []

# Function to be called when a mouse event happens
def onclick(event):
    ix, iy = event.xdata, event.ydata
    coords.append((ix, iy))
    print(f'Coordinates: ({ix}, {iy})')
    if len(coords) == 12: # You can adjust this to the number of clicks you need
        plt.close()

# Connect the click event to the function
cid = fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()

print(f'Collected coordinates: {coords}')
