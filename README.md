# Image Collection

This Blender addon allows you to combine multiple images into a single image using different packing algorithms. You can also add padding to each image as needed. The Image Collection panel is only visible in the Image Editor area.

![Screenshot](screenshot.png)

## Installation

To install this addon, do the following:

1. Download the latest release from the [releases page](https://github.com/HerrWaffel/image-collection/releases).
2. In Blender, go to Edit > Preferences > Add-ons.
3. Click the "Install" button, and select the downloaded .zip file.
4. Enable the addon by checking the checkbox next to its name.

## Usage

To use this addon, do the following:

1. Open a new Blender file.
2. Go to the Image Editor area.
3. Open the Image Collection panel and set the collection name and background colour.
4. In the Image Collection panel, select the images you want to combine.
5. Choose a packing algorithm from the dropdown menu.
6. Optionally, adjust the padding value as needed.
7. Click the "Make Collection" button to generate the combined image.

## Configuration

This addon has the following configuration options:

- Packing algorithm: Choose from several different algorithms for packing the images together, including:
  - Square packing: This algorithm scales each image to have the same width and height, and the combined image is also a square.
  - Auto sort: This algorithm uses a divide and conquer algorithm (implemented with the Python dependency `rpack`) to find the optimal packing solution.
  - Row packing: This algorithm keeps the images in the order of the collection list and scales the images to have the same width or height.
  - Next fit packing: This algorithm keeps the size of the images and follows the order of the collection list, but may result in gaps between the rows.
- Padding: Adjust the amount of padding to add around each image.

## Troubleshooting

If you experience any issues with this addon, try the following:

1. Make sure you have installed the latest version of the addon.
2. Check the Blender console (Window > Toggle System Console) for any error messages.
3. If you still can't resolve the issue, open an issue on the [GitHub repository](https://github.com/HerrWaffel/image-collection/issues).

## Contributing

If you would like to contribute to this addon, please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes, and commit them with a descriptive commit message.
4. Push your changes to your fork.
5. Create a pull request from your fork to the main repository.

## License

This addon is released under the MIT License. See [LICENSE](LICENSE) for details.
