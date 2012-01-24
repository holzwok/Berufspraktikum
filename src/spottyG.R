# Script to find fluorescent spots for individual cells with varying background
# via local thresholding and Gaussian mixture clustering (EM+BIC)
# Author: Christian Diener (diener@molgen.mpg.de)
# Modified by: Martin Seeger

# finds spots for a single cell
get.spots = function(int.data, x.center=x.center, y.center=y.center, Gmax=Gmax)
{
	minpixels = 2 		      # smallest permissible spot in pixels          # TODO: make this an argument
	totalsignalnoisecutoff = 0.08 # smallest permissible S/N ratio (entire spot) # TODO: make this an argument
	int.data[, 1] = int.data[, 1] - x.center
	int.data[, 2] = int.data[, 2] - y.center
	F = int.data[, 4]
	
	res = data.frame()

	if(max(F) == 0) return(res)
	
	else F = F

	tol = 1.5*mad(F)
	#tol = 2*mad(F) #original parameter

	if(tol < 0.15*median(F)) #original parameter was 0.3*median(F) 
	{
		write(paste("Bad noise/signal ratio for cell #", int.data[1,3],"!", sep="") ,file="")
		#tol = 0.15*median(F) # commented out in order to accept spots with lower signal/noise
	}
	cutoff = median(F)+tol
	
	if(cutoff > max(F)) return(res)
	
	else
	{
		spots = int.data[F > cutoff, 1:2]

		if(nrow(spots) == 1)
		{
			x = spots[, 1]
			y = spots[, 2]
			pixels = 1
			f.tot = int.data[F>cutoff, 4]  # counts intensity above cutoff but does not subtract median
			f.sig = int.data[F>cutoff, 4] - median(F) # counts intensity above median (subtracts median)
		} 
		else
		{
			cl = Mclust(spots, G=1:Gmax) 
			#modelName = cl$modelName
			#numobs = cl$n
			#dim = cl$d
			#numcom = cl$G
			#optbic = cl$bic
			#loglik = cl$loglik
			#proportion = cl$pro
			x = cl$parameters$mean[1, ] 
			y = cl$parameters$mean[2, ]
			pixels = as.numeric(table(cl$classification))
			#uncertainty = cl$uncertainty
			f.tot = tapply(int.data[F>cutoff, 4], cl$classification, sum) # counts intensity above cutoff but does not subtract median
			f.sig = tapply(int.data[F>cutoff, 4], cl$classification, sum) - median(F)*pixels # counts intensity above cutoff (subtracts median)
		}	
		res = data.frame(ID = int.data[1, 3],
						  x = x, y = y, 
						  pixels = pixels,
						  f.tot = f.tot,
						  f.sig = f.sig,
						  f.median = median(F),
						  f.mad = mad(F))
		res = subset(res, pixels > minpixels) # remove small clusters from data structure. these are usually the cause for false positives.
		res = subset(res, f.sig > f.tot * totalsignalnoisecutoff) # remove noisy spots. these usually occur in relatively homogenous cells and cause false positives.
		#write(paste("---------------------------------------------") ,file="")
		write(paste("Mclust running..."), file="")
		#write(paste(names(cl), ": ", cl) ,file="") # diagnostic output
		#print(res) # diagnostic output
		return(res)
	}
}


# Main part, executed

args = commandArgs(trailingOnly=T)

if(length(args)<5) stop("Need at least 4 arguments [ i) x-center ii) y-center iii) maximum number of clusters iv) interior pixel file(s) ]!")

x.center = as.numeric(args[2])
y.center = as.numeric(args[3])
Gmax = as.numeric(args[4])
interior.files = args[5:length(args)]

require(mclust)

for(int.file in interior.files)
{
	write(paste("spottyG.R running on ", int.file, "...", sep="") ,file="")
	basename = strsplit(int.file, '\\.')[[1]][1]	
	filename = tail(strsplit(basename, '/')[[1]], 1)

	int.data = read.table(int.file, header=F)	
	spots = by(int.data, int.data[,3], get.spots, x.center=x.center, y.center=y.center, Gmax=Gmax)
	# int.data[,3] is the cell number, so get.spots is applied multiple times to data belonging to one cell each (this is what the by function does)

	all = data.frame()
	sapply(spots, function(x) all <<- rbind(all, x)) -> dummy
	all$filename = apply(all, 1, function(x) filename) 
	write.table(all, file=paste(basename, "_SPOTS.xls", sep=""), quote=F, row.names=F)
	write(paste("Written to output file ", basename, "_SPOTS.xls", ".", sep="") ,file="")
}
