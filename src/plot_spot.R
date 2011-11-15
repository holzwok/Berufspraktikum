############################################################
# plot_helper.R
# This file is part of Mesh Tools
#
# Copyright (C) 2011 - Christian Diener
#
# Mesh Tools is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Mesh Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mesh Tools; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, 
# Boston, MA  02110-1301  USA
############################################################
 
# Plots a profile
# usage:
# >Rscript plot_helper.R --args cellID_file boundary_file interior_file out_name 

### Analysis file for cell positions and mesh generation

source("mesh_tools.R")

# These parameters have to be changed if your image has different measures!
PIXELS = 512
SIZE = 70.14

PIX_PER_UM <- PIXELS/SIZE
UM_PER_PIX <- SIZE/PIXELS

cm = colorRampPalette(c("darkblue", "blue", "red"))

choose.col = function(F, cutoff, ncol=512)
{
	pvals = 1 - pnorm(F, mean=median(F), sd=mad(F))
	cols = cm(ncol) 

	out = cols[511*(1-pvals)+1]
	out[F>cutoff] = "black"

	return(out)
}

args = commandArgs(1)

cells = read.cellID(args[2], RFP=F)
bl = read.boundary(args[3])
int = read.interior(args[4])
surfs = interpolate.surface(cells, bl)

jpeg(args[5], width=2400, height=1800, pointsize=60)
l=layout(t(1:2), widths=c(3,1))
plot(NULL, xlim=c(-SIZE/2, SIZE/2), ylim=c(-SIZE/2, SIZE/2), main="",
	xlab=expression(paste("x [", mu, "m]")), ylab=expression(paste("y [", mu, "m]")))

# this would be faster with an apply, but it's more readable that way ;)
for(cell in int)
{
	# Calculate the cutoff as used in spotty	
	F = cell[, 3]
	if(max(F) == 0) return(res)
	else F = F
	tol = 2*mad(F)
	if(tol < 0.3*median(F))
	{
		#write(paste("Bad noise/signal ratio for cell #", int.data[1,3],"!", sep="") ,file="")
		tol = 0.3*median(F)
	}
	cutoff = median(F)+tol

	#rect( cell[,1]-UM_PER_PIX, cell[,2]-UM_PER_PIX, cell[,1]+UM_PER_PIX, cell[,2]+UM_PER_PIX,
	#	border=NA, col=choose.col(F, cutoff) )	<- uncomment to rather draw the pixels instead of circles
	# Plot each pixel as acircle coloured by the p-value of the internal backgropund (from gaussian)
	points( cell[,1], cell[,2], pch=19, col=choose.col(F, cutoff), cex=0.1)
}

# Plot the smoothened membranes of the cells
dummy = sapply(1:length(surfs), function(i){ s = get.surface(i, surfs, do.smooth=0.7); polygon(s$x, s$y, lwd=4, border="black")})
# Plot the color-key
scale = seq(0, 1, length.out=512)
image(y=scale, z=t(scale), col=rev(cm(512)), ylab="p-value", xaxt="n")
dev.off()
