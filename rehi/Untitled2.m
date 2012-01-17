


imshow(bw)
ultimateErosion = bwulterode(bw);
figure, subplot (3, 3, 1)
imshow(ultimateErosion)

SE2 = strel ('disk', 7);
bw_dil = imdilate(ultimateErosion, SE2);
subplot (3, 3, 2)
imshow(bw_dil)
overlay = imoverlay(10*bw, ~bw, [.3 1 .3]);
subplot (3, 3, 3)
imshow(overlay,[])
