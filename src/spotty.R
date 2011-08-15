# Script to find fluorescent spots for individual cells with varying background
# via local thresholding and Gaussian mixture clustering (EM+BIC)
# Author: Christian Diener (diener@molgen.mpg.de)

# finds spots for a single cell
get.spots = function(int.data, x.center=x.center, y.center=y.center)
{
	int.data[,1] = int.data[,1] - x.center
	int.data[,2] = int.data[,2] - y.center
	F = int.data[,4]
	
	res = data.frame()

	if(max(F) == 0) return(res)
    else F = F

	tol = 2*mad(F)

	if(tol < 0.1*median(F))
	{
		write(paste("Bad noise/signal ratio for cell #", int.data[1,3],"!", sep="") ,file="")
		tol = 0.1*median(F)
	}

	cutoff = median(F)+tol
	
	if(cutoff>max(F)) return(res)
    else
	{
		spots = int.data[F>cutoff, 1:2]
		
		if(nrow(spots) == 1)
		{
			x = spots[,1]
			y = spots[,2]
			pixels = 1
			f.tot = int.data[F>cutoff,4]
		} 
		else
		{
			cl = Mclust(spots)
			x=cl$parameters$mean[1,] 
			y=cl$parameters$mean[2,]
			pixels = as.numeric( table(cl$classification) )
			f.tot = tapply( int.data[F>cutoff,4], cl$classification, sum )
		}	
        
		res = data.frame( ID = int.data[1,3],
						  x=x, y=y, 
						  pixels = pixels,
						  f.tot = f.tot,
						  f.median = median( F ),
						  f.mad = mad( F )
						 )

		return(res)
	}
}

# Main part, executed

args = commandArgs(trailingOnly=T)

if(length(args)<4) stop( "Need at least 3 arguments [ i) x-center ii) y-center iii) interior pixel file(s) ] !!!" )

x.center = as.numeric( args[2] )
y.center = as.numeric( args[3] )
interior.files = args[4:length(args)]

require(mclust)

for( int.file in interior.files )
{
	basename = strsplit( int.file, '\\.' )[[1]][1]	
	filename = tail(strsplit( basename, '/')[[1]], 1)

	int.data = read.table(int.file, header=F)	
	spots = by( int.data, int.data[,3], get.spots, x.center=x.center, y.center=y.center )
	# int.data[,3] is the cell number, so get.spots is applied multiple times to data belonging to one cell each
	all = data.frame()
	sapply(spots, function(x) all <<- rbind(all, x)) -> dummy
	all$filename = apply(all, 1, function(x) filename) 
	write.table( all, file=paste(basename, "_SPOTS.xls", sep=""), quote=F, row.names=F )
}
