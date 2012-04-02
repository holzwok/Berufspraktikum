from PIL import Image, ImageOps, ImageFilter

# the image we want to paste in the transparent mask
background = Image.open("")

# the mask, where we insert our image
mask = Image.open("my_mask.png")

# mask, that we overlay
frame_mask = Image.open("")

# smooth the mask a little bit, if you want
# mask = mask.filter(ImageFilter.SMOOTH)
# resize/crop the image to the size of the mask-image
cropped_image = ImageOps.fit(background, mask.size, method=Image.ANTIALIAS)
# get the alpha-channel (used for non-replacement)
cropped_image = cropped_image.convert("RGBA")
r,g,b,a = mask.split()
# paste the frame mask without replacing the alpha mask of the mask-image
cropped_image.paste(frame_mask, mask=a)
cropped_image.save("my_generated_image.png")