I = imread('nuclei.png');
I_cropped = I(400:900, 465:965);
#imshow(I_cropped)

I_eq = I_cropped; # adapthisteq(I_cropped); # function does not exist in Octave
#imshow(I_eq)

bw = im2bw(I_eq, graythresh(1.5*I_eq));
imshow(bw)

bw2 = bwfill(bw,'holes');
bw3 = imopen(bw2, ones(5,5));
bw4 = bw2; #bwareaopen(bw3, 40); # function does not exist in Octave
bw4_perim = bwperim(bw4);
overlay1 = imoverlay(I_eq, bw4_perim, [.3 1 .3]);
imshow(overlay1)

I_eq_c = imcomplement(I_eq);
I_mod = I_eq_c # imimposemin(I_eq_c, ~bw4 | mask_em);
L = watershed(I_mod);
imshow(label2rgb(L))
