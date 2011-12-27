


ultimateErosion = bwulterode(bw);
figure, subplot (3, 3, 1) 
imshow(bw)

subplot (3, 3, 2)
imshow(ultimateErosion)

SE2 = strel ('disk', 6);
bw_dil = imdilate(ultimateErosion, SE2);
subplot (3, 3, 3)
imshow(bw_dil)
%overlay = imoverlay(10*bw, ~ultimateErosion, [.3 1 .3]);
%imshow(overlay,[])
