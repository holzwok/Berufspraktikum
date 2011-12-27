%-------------------------------------
%   Count cells dapi/fitc
%
%   Compare cytosol/nucleus
%
%   Christian Ebbesen, 29.07.2011
%-------------------------------------

% Good sites:
% http://blogs.mathworks.com/steve/2006/06/02/cell-segmentation/
% http://www.mathworks.com/products/demos/image/watershed/ipexwatershed.html
% 
% 
% 

clear all;
close all;

fname = 'testbild.tif';
    
%I = imread(fname, 1);

nCells = [0 0]; %store in matrix

%for k=1:2; % wrap in loop to count dapi/FITC.

I_pre = imread(fname, 1);
I = imclearborder(I_pre);
    
figure(1);

subplot(3, 3, 1);
imshow(I_pre,[])
title('Orig. image')

subplot(3, 3, 2); 
I_eq = adapthisteq(I); % contrast-limited adaptive histogram equalization. CLAHE. 
imshow(I_eq,[])
title('Image w. clearborder und CLAHE')
% % Histogram for billedet.
% [pixelCount grayLevels] = imhist(img1);
% subplot(3, 3, 2); 
% bar(pixelCount); title('Histogram af grey og invert');
% %xlim([0 20]) 
% xlim([0 grayLevels(end)]); % Scale x axis manually.


%Calc stuff

%bw2 = imfill(bw,4,'holes'); % 4 or 8 connected unnötig

SE = strel('disk',2);
clearim = imopen(I_eq, SE);%remove noise with radius smaller than 5

subplot (3, 3, 3);
imshow(clearim,[])
title('Image filtered w. disks w. R=2 px')
% Clear mursten paa randen
clearim1 = imclearborder(clearim);


% Fjern smaa objekter, 8conn 40 px
clearim2 = bwareaopen(clearim1, 200);
clearim2_perim = bwperim(clearim2);
%overlay1 = imoverlay(I_eq, bw5_perim, [.3 1 .3]); tool nicht vorhanden...
% 
% subplot(3, 3, r); 
% imshow(clearim2_perim)
% title('Cell perimiters')

subplot(3, 3, 4); 
bw_pre_clear_b = im2bw(clearim2, 0.4*graythresh(I_eq)); % chooses the threshold to minimize the intraclass variance of the black and white pixels.
bw = imclearborder(bw_pre_clear_b);
imshow(0.5*bw)
title('Binary image')

% SE1 = strel ('disk', 1);
% erodedBW = imerode (bw, SE1);% not a useful method
%subplot(3, 3, 9); 
%imshow(erodedBW)

%im_er = imerode(bw5_perim, SE);
labeledImage = bwlabel(bw); %, 8); Hvorfor 8?     % Label each blob so we can make measurements of it
coloredLabels = label2rgb(labeledImage); % igen, hvad er det her: , 'hsv', 'k', 'shuffle'); % pseudo random color labels


subplot(3, 3, 5); 
imagesc(coloredLabels);


% Get all the blob properties.  Can only pass in originalImage in version R2008a and later.
blobMeasurements = regionprops(labeledImage, I, 'all');   
numberOfBlobs = size(blobMeasurements, 1);

fontSize = 14;	% Used to control size of "blob number" labels put atop the image.
labelShiftX = -7;	% Used to align the labels in the centers of the coins.
blobECD = zeros(1, numberOfBlobs);
% Print header line in the command window.
fprintf(1,'Blob #      Mean Intensity  Area   Perimeter    Centroid       Diameter\n');
% Loop over all blobs printing their measurements to the command window.
for k = 1 : numberOfBlobs           % Loop through all blobs.
	% Find the mean of each blob.  (R2008a has a better way where you can pass the original image
	% directly into regionprops.  The way below works for all versions including earlier versions.)
    thisBlobsPixels = blobMeasurements(k).PixelIdxList;  % Get list of pixels in current blob.
    meanGL = mean(I(thisBlobsPixels)); % Find mean intensity (in original image!)
	meanGL2008a = blobMeasurements(k).MeanIntensity; % Mean again, but only for version >= R2008a
	
	blobArea = blobMeasurements(k).Area;		% Get area.
	blobPerimeter = blobMeasurements(k).Perimeter;		% Get perimeter.
	blobCentroid = blobMeasurements(k).Centroid;		% Get centroid.
	blobECD(k) = sqrt(4 * blobArea / pi);					% Compute ECD - Equivalent Circular Diameter.
    fprintf(1,'#%2d %17.1f %11.1f %8.1f %8.1f %8.1f % 8.1f\n', k, meanGL, blobArea, blobPerimeter, blobCentroid, blobECD(k));
	% Put the "blob number" labels on the "boundaries" grayscale image.
	text(blobCentroid(1) + labelShiftX, blobCentroid(2), num2str(k), 'FontSize', fontSize, 'FontWeight', 'Bold');
end


noCells = num2str(numberOfBlobs);
title(['Labeled regions. No. of cells is ' noCells])


%erode image to seperate cells.

SE1 = strel ('disk', 3);
bw_er=bw;
for k=1:4
bw_er = imerode (bw_er, SE1);% not a useful method
end

SE2 = strel ('disk', 2);
bw_er = imdilate(bw_er, SE2);
% COmplement image to make valleys out of the peaks

er_in = imcomplement(bw_er);

subplot(3, 3, 6); 
imshow(bw_er)
title('4x eroded, 2x dilated, inverted')


bw_half=0.5*bw;

I_mod = imimposemin(bw_half,bw_er);


L = watershed(I_mod);

subplot(3,3,7)
imshow(label2rgb(L))
title('Watershed of original image using markers')

% multiply to get only the nucleus:

nuc = L.*bw;

subplot(3,3,8)
imshow(nuc)

title('Final image w. separated cells')


labeledImage = bwlabel(nuc); %, 8); Hvorfor 8?     % Label each blob so we can make measurements of it
coloredLabels = label2rgb(labeledImage); % igen, hvad er det her: , 'hsv', 'k', 'shuffle'); % pseudo random color labels


subplot(3, 3, 9); 
imagesc(coloredLabels);


% Get all the blob properties.  Can only pass in originalImage in version R2008a and later.
blobMeasurements = regionprops(labeledImage, I, 'all');   
numberOfBlobs = size(blobMeasurements, 1);

fontSize = 14;	% Used to control size of "blob number" labels put atop the image.
labelShiftX = -7;	% Used to align the labels in the centers of the coins.
blobECD = zeros(1, numberOfBlobs);
% Print header line in the command window.
fprintf(1,'Blob #      Mean Intensity  Area   Perimeter    Centroid       Diameter\n');
% Loop over all blobs printing their measurements to the command window.
for k = 1 : numberOfBlobs           % Loop through all blobs.
	% Find the mean of each blob.  (R2008a has a better way where you can pass the original image
	% directly into regionprops.  The way below works for all versions including earlier versions.)
    thisBlobsPixels = blobMeasurements(k).PixelIdxList;  % Get list of pixels in current blob.
    meanGL = mean(I(thisBlobsPixels)); % Find mean intensity (in original image!)
	meanGL2008a = blobMeasurements(k).MeanIntensity; % Mean again, but only for version >= R2008a
	
	blobArea = blobMeasurements(k).Area;		% Get area.
	blobPerimeter = blobMeasurements(k).Perimeter;		% Get perimeter.
	blobCentroid = blobMeasurements(k).Centroid;		% Get centroid.
	blobECD(k) = sqrt(4 * blobArea / pi);					% Compute ECD - Equivalent Circular Diameter.
    fprintf(1,'#%2d %17.1f %11.1f %8.1f %8.1f %8.1f % 8.1f\n', k, meanGL, blobArea, blobPerimeter, blobCentroid, blobECD(k));
	% Put the "blob number" labels on the "boundaries" grayscale image.
	text(blobCentroid(1) + labelShiftX, blobCentroid(2), num2str(k), 'FontSize', fontSize, 'FontWeight', 'Bold');
end


noCells = num2str(numberOfBlobs);
title(['Labeled regions. No. of cells is ' noCells])





%
% Now try to get the shapes of the cytosols from the DIC image
%

DIC= imread(fname, 3);


figure(2)

subplot(3,3,1)
imshow(DIC,[])
title('Raw DIC image')


hy = fspecial('sobel');
hx = hy';
DICy = imfilter(double(DIC), hy, 'replicate');
DICx = imfilter(double(DIC), hx, 'replicate');
gradmag = sqrt(DICx.^2 + DICy.^2);
subplot(3,3,2)
imshow(gradmag,[]), title('gradmag')


% Filter image w imopen 20 disks

se = strel('disk', 2);
Io = imopen(gradmag, se);
subplot(3,3,3)
imshow(Io,[]), title('Io')

%  filter again

se = strel('disk', 4);
Io2 = imopen(Io, se);
subplot(3,3,4)
imshow(Io2,[]), title('Io2')

% smoothen w gaussian

gaufilter = fspecial('gaussian',[20, 20], 6);
Io_gau = imfilter(Io2, gaufilter); % 'symmetric', 'conv')
subplot(3,3,5)
imshow(Io_gau,[]), title('Io_gau')

% opwn with disks

se = strel('disk', 15);
Io3 = imopen(Io_gau, se);
subplot(3,3,6)
imshow(Io3,[]), title('Io3')

% make binary:
Io4 = Io3./256;
dbw = im2bw(Io4, 0.6*graythresh(Io4)); % chooses the threshold to minimize the intraclass variance of the black and white pixels.
subplot(3,3,7)
imshow(dbw,[]), title('dbw')



% now we need the image with fitc:

F = imread(fname, 2);

num = double(dbw)

F_clear = num.*double(F);

subplot(3,3,8)
imshow(F_clear,[]), title('F')



I_mod = imimposemin(0.5*num,nuc);


L = watershed(I_mod);

L2 = num.*L

subplot(3,3,9)

imshow(label2rgb(L2))
title('Watershed of cytosols')


figure(3)

nuc_perim = bwperim(nuc);
L2_perim = bwperim(L2)
overlay1 = imoverlay(10*DIC, nuc_perim, [.3 1 .3]);
imshow(overlay1,[])
title('WOW, look at these amazing nuclei!')

figure(4)
overlay2 = imoverlay(10*DIC, L2_perim, [.3 1 .3]);
imshow(overlay2,[])
title('WOW, look at these fantastic cytosols!')






% % Next compute the opening-by-reconstruction using imerode and imreconstruct.
% 
% Ie = imerode(DIC, se);
% Iobr = imreconstruct(Ie, DIC);
% subplot(3,3,4)
% imshow(Iobr,[]), title('Iobr')
% 
% 
% 
% % Following the opening with a closing can remove the dark spots and stem marks. 
% % Compare a regular morphological closing with a closing-by-reconstruction. First try imclose:
% 
% Ioc = imclose(Io, se);
% subplot(3,3,5), 
% imshow(Ioc,[]), title('Ioc')
% 
% 
% 
% % Now use imdilate followed by imreconstruct. Notice you must complement 
% % the image inputs and output of imreconstruct.
% 
% Iobrd = imdilate(Iobr, se);
% Iobrcbr = imreconstruct(imcomplement(Iobrd), imcomplement(Iobr));
% Iobrcbr = imcomplement(Iobrcbr);
% subplot(3,3,6), 
% imshow(Iobrcbr,[]), title('Iobrcbr')
% 
% 
% % As you can see by comparing Iobrcbr with Ioc, reconstruction-based 
% % opening and closing are more effective than standard opening and closing 
% % at removing small blemishes without affecting the overall shapes of the objects. 
% % Calculate the regional maxima of Iobrcbr to obtain good foreground markers.
% 
% fgm = imregionalmax(Iobrcbr);
% subplot(3,3,7)
% imshow(fgm,[]), title('fgm')



















% 
% % Calculating mean Area
% %if blob area is two times mean blob area --> two overlapping blobs
% mean_Area = 0;
% for k = 1:numberOfBlobs
%     mean_Area = mean_Area + blobMeasurements(k).Area;
% end
% 
% mean_Area = mean_Area / numberOfBlobs;
% realNumberOfBlobs = numberOfBlobs; 
% for k = 1:numberOfBlobs
%     if blobMeasurements(k).Area >= 1.8* mean_Area
%         realNumberOfBlobs = realNumberOfBlobs + 1;
%     end
% end
% 
% 
% 




% Areas = ones(numel(numberOfBlobs),1);
% for k = 1:numberOfBlobs
%     Areas(k) = blobMeasurements(k).Area;
% end
% subplot(3, 3, 8);
% hist(Areas,30)
% caption = sprintf('Histogram over arealdistribution');
% title(caption);
% xlabel('pixels');
% ylabel('N')
% 
% 
% Intens = ones(numel(numberOfBlobs),1);
% for k = 1:numberOfBlobs
%     Intens(k) =  blobMeasurements(k).MeanIntensity; % Mean again, but only for version >= R2008a;
% end
% subplot(3, 3, 9);
% hist(Intens,30)
% caption = sprintf('Histogram over Intensitet');
% title(caption);
% xlabel('Norm. intens.');
% ylabel('N')


% 
% % figure(3)
% subplot(3,3,5)
% imagesc(coloredLabels);
% 
% 
% fontSize = 14;	% Used to control size of "blob number" labels put atop the image.
% labelShiftX = -7;	% Used to align the labels in the centers of the coins.
% blobECD = zeros(1, numberOfBlobs);
% % Print header line in the command window.
% fprintf(1,'Blob #      Mean Intensity  Area   Perimeter    Centroid       Diameter\n');
% % Loop over all blobs printing their measurements to the command window.
% for k = 1 : numberOfBlobs           % Loop through all blobs.
% 	% Find the mean of each blob.  (R2008a has a better way where you can pass the original image
% 	% directly into regionprops.  The way below works for all versions including earlier versions.)
%     thisBlobsPixels = blobMeasurements(k).PixelIdxList;  % Get list of pixels in current blob.
%     meanGL = mean(I(thisBlobsPixels)); % Find mean intensity (in original image!)
% 	meanGL2008a = blobMeasurements(k).MeanIntensity; % Mean again, but only for version >= R2008a
% 	
% 	blobArea = blobMeasurements(k).Area;		% Get area.
% 	blobPerimeter = blobMeasurements(k).Perimeter;		% Get perimeter.
% 	blobCentroid = blobMeasurements(k).Centroid;		% Get centroid.
% 	blobECD(k) = sqrt(4 * blobArea / pi);					% Compute ECD - Equivalent Circular Diameter.
%     fprintf(1,'#%2d %17.1f %11.1f %8.1f %8.1f %8.1f % 8.1f\n', k, meanGL, blobArea, blobPerimeter, blobCentroid, blobECD(k));
% 	% Put the "blob number" labels on the "boundaries" grayscale image.
% 	text(blobCentroid(1) + labelShiftX, blobCentroid(2), num2str(k), 'FontSize', fontSize, 'FontWeight', 'Bold');
% end
% 
% %nCells(1,k) = numberOfBlobs
% 
% %end



% 
% %
% %   Watershead by marker
% %
% 
% % Extended max or gray
% 
% mask_em = im2bw(I_eq, 0.5*graythresh(I_eq));
% imshow(mask_em)
% 
% 
% 
% 
% 
% % Overlay
% figure(6)
% mask_em = imclose(mask_em, ones(5,5));
% mask_em = imfill(mask_em, 'holes');
% mask_em = bwareaopen(mask_em, 40);
% overlay2 = imoverlay(I_eq, bw5_perim | mask_em, [.3 1 .3]);
% imshow(mask_em)
% 
% 
% 
% I_eq_c = imcomplement(I_eq);
% 
% 
% I_mod = imimposemin(I_eq_c, ~bw5 | mask_em);
% 
% 
% figure(5)
% imshow(I_eq_c)
% 
% L = watershed(mask_em);
% figure(4)
% imshow(label2rgb(L))