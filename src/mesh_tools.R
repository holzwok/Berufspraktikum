############################################################
# mesh_tools.R
# This file is part of Meshing Tools
#
# Copyright (C) 2011 - Christian Diener
#
# Meshing Tools is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Meshing Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Meshing Tools; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, 
# Boston, MA  02110-1301  USA
############################################################
 
# This include file contains functions to generate Gmsh meshes
# from CellID output along with anaylsis and plotting tools


### Analysis file for cell positions and mesh generation

GFP <- 0
RFP <- 1

# These parameters have to be changed if your image has different measures!
PIXELS = 512
SIZE = 70.14

PIX_PER_UM <- PIXELS/SIZE
RFP_CUT <- 4				# cutoff for cherry fluorescence

# Those are the parameters used for config
# if you redefine them after the include and before
# calling write_conf they will be ignored
P_INIT = c(10, 2.8, 1.4, 0.028)
EC50 = 39.2
NH = 1.45
FMAX = 19.8
FMIN = 2.1

# Values used for mesh element sizes
# Good for fast evals: LCW = 10-16, LCM=0.3-0.5, LCS = 6-8
# Good for accurate: LCW = 6-8, LCM = 0.1-0.25, LCS = 0.5-2

ALPHA = 3
LCW = 8
LCM = 0.5
LCS = 4

GEO_HEAD ='' #sprintf("lc = %0.3f;\n", LC)

# Calculates a density map from a set of xy-positions
# and returns the density along with the binning cuts
generate.dmap.poly = function(x,y, cells)
{   
    dens <- MASS::kde2D(x,y, h=mean(cells$r), n=128)

    mkBreaks <- function(u) u - diff(range(u))/(length(u) - 1)/2

    return( list(xbin=mkBreaks(dens$x), ybin=mkBreaks(dens$y), d=dens$z ) ) 
}

# Takes a binned density map and returns the density for any 
# given point 
get.dens = function(x,y, dm=dmap) 
{
    xbin <- cut(x, dm$xbin, labels = FALSE)
    ybin <- cut(y, dm$ybin, labels = FALSE)
 
    return(dm$d[xbin,ybin])
}

# Helper functions
point = function(idx,x,y, d=dmap) sprintf( 'Point(%i) = {%0.3f, %0.3f, 0.0, %0.5f};' , idx, x, y, max(exp(-get.dens(x,y,d)*ALPHA)*LCS, LCM) )
point.out = function(idx,x,y, lc=LCW) sprintf( 'Point(%i) = {%0.3f, %0.3f, 0.0, %0.5f};' , idx, x, y, lc )
line = function(idx,p1,p2) sprintf( 'Line(%i) = {%i, %i};', idx, p1, p2 )
spline = function(idx, plist) sprintf( 'Spline(%i) = {%s};', idx, paste(plist, collapse=', ') )
circle = function(idx, p1, p2, p3) sprintf( 'Circle(%i) = {%i, %i, %i};', idx, p1, p2, p3 )
loop = function(idx, l1, l2, l3, l4) sprintf( 'Line Loop(%i) = {%i, %i, %i, %i};', idx, l1, l2, l3, l4)

# Takes cell information and the cell boundaries and writes a Gmsh geo file
# nP is the number of points used for the interpolation of the cell boundary
# rad is the radius of the "world"
write.geo.poly = function(cells, surfs ,filename='cells_poly.geo', nP=128, rad=SIZE)
{
    geo <- file(filename, open='w')
    write(GEO_HEAD, file=geo)
    pi <- 0
    li <- nrow(cells)+1
    
    if( ncol(cells) == 6 )
    {
    	MATAL = cells$ID[cells$RFP>RFP_CUT]+1
    	MATA = cells$ID[cells$RFP<=RFP_CUT]+1
    	surfs = surfs[c(MATAL, MATA)]
    }
    else surfs = surfs[cells$ID+1]
    
    
    geo.cell.poly = function(i, surfs, nP, out_file)
    {
        write('\n', file=out_file)
        coord <- get.surface(i, surfs, do.smooth=T, nP=nP)
        n <- length(coord$x)
        
        sapply(1:n, function(k) write( point(pi+k, coord$x[k], coord$y[k]), file=out_file) )
        
        write( spline(li+1, c(pi+1:n, pi+1)), file=out_file )
   
        write( sprintf( 'Line Loop(%i) = {%i};', li+2, li+1), file=out_file )
        write( sprintf( 'Physical Line(%i) = {%i};', i, li+1 ), file=out_file )
        
        pi <<- pi+n
        li <<- li+2
    }
    
    
    write( point.out(pi+1, 0, 0) ,file=geo )
    write( point.out(pi+2, 0, rad) ,file=geo )
    write( point.out(pi+3, rad, 0) ,file=geo )
    write( point.out(pi+4, 0, -rad) ,file=geo )
    write( point.out(pi+5, -rad, 0) ,file=geo )
    pi <- pi+5
    
    write( circle(li+1, 2, 1, 3), file=geo )
    write( circle(li+2, 3, 1, 4), file=geo )
    write( circle(li+3, 4, 1, 5), file=geo )
    write( circle(li+4, 5, 1, 2), file=geo )
        
    write( loop(li+5, li+1, li+2, li+3 ,li+4), file=geo )
    write( sprintf( 'Physical Line(%i) = {%i, %i, %i, %i};', 0, li+1, li+2, li+3, li+4 ), file=geo )
    li <- li+5
    start <- li
    
    dummy <- sapply(1:length(surfs), geo.cell.poly, surfs, nP, geo)
    
    loops <- paste( seq(start,li, by=2), collapse=', ')
    write( sprintf('\nRuled Surface (%i) = { %s };', li+1, loops), file=geo )
    write( sprintf('Physical Surface(%i) = { %i };', nrow(cells)+1, li+1), file=geo )
    close(geo)
}

# Writes the configuration used for simulation
write.conf = function(cells, filename='conf.txt')
{
	out = file(filename, open='w')
	
	write(length(MATAL), file=out)
	write(length(MATA), file=out)
	
	sapply(P_INIT, write, file=out)
	F = cells$GFP[(cells$ID+1) %in% MATA]
	F.zero = cells$GFP[(cells$ID+1) %in% MATAL]
	write( paste("Zero level:",mean(F.zero),"+-",sd(F.zero)) ,file="" )
	

	F = F -mean(F.zero) + FMIN
	F[F<FMIN] = FMIN
	alpha = EC50*( (F-FMIN)/(FMAX-F+FMIN) )^(1/NH)
	
	sapply(alpha, write, file=out)
	
	close(out)
}

# Reads the cell boundaries from CellID_hack output
read.boundary = function(file)
{
    bound <- read.table(file, header=F)
    bound[,1] <- (bound[,1] - PIXELS/2)/PIX_PER_UM
    bound[,2] <- (PIXELS/2 - bound[,2])/PIX_PER_UM
    
    return( lapply(unique(bound[,3]), function(i) bound[bound[,3]==i,1:2]) )
}

# Reads the cell's interior pixels from CellID_hack output
read.interior = function(file)
{
    int <- read.table(file, header=F)
    int[,1] <- (int[,1] - PIXELS/2)/PIX_PER_UM
    int[,2] <- (PIXELS/2 - int[,2])/PIX_PER_UM
    
    return( lapply(unique(int[,3]), function(i) int[int[,3]==i,c(1,2,4)]) )
}

# Takes the surface and transforms them to polar coordinates
interpolate.surface = function(cells, borders)
{
    #Helper functions to interpolate a single surface first
    
    d.e = function(p1,p2){
        p1 <- as.numeric(p1)
        p2 <- as.numeric(p2)
        return( sqrt(sum((p1-p2)*(p1-p2))) )
    }
    angle = function(p, ref, mid)
    {
        pm <- p - mid
        refm <- ref - mid
        
        if(all(pm==refm)) return(0)
        else if(all(pm==-refm)) return(pi)
        else return(  acos(sum(pm*refm)/sqrt(sum(pm*pm))/sqrt(sum(refm*refm)) ) )
    }
    
    inter.single = function(bID, bor)
    {
        surf.points <- bor[[bID+1]]
        surf.mid <- colMeans(surf.points)


        t.p <- surf.points[surf.points[,2]>surf.mid[2],]
        l.p <- surf.points[surf.points[,2]<=surf.mid[2],]

        t.i <- which.min( t.p[ ,2] )
        t.s <- t.p[t.i, ]
        t.ccw <- t.s[1] > surf.mid[1]
        
        l.i <- which.max( l.p[ ,2] )
        l.s <- l.p[l.i, ]
        l.ccw <- l.s[1] < surf.mid[1]
        
        t.a <- apply(t.p, 1, angle, ref=t.s, mid=surf.mid)
        t.r <- apply(t.p, 1, d.e, p2=surf.mid)
        if(!t.ccw) t.a <- pi - t.a
        
        l.a <- apply(l.p, 1, angle, ref=l.s, mid=surf.mid)
        l.r <- apply(l.p, 1, d.e, p2=surf.mid)
        if(l.ccw) l.a <- l.a + pi else l.a <- 2*pi - l.a

        phi <- c(t.a,l.a)
        r <- c(t.r, l.r)
        ix <- sort(phi, index.return=T)$ix
        phi <- phi[ix]
        r <- r[ix]
        #r <- rep(10,length(phi))
        
        out <- list(mid=surf.mid, phi=phi, r=r )
        return(out)
    }   
    
    surf <- list()
    surf[cells$ID+1] <- lapply(cells$ID, inter.single, bor=borders)
    return(surf)
    
}

# Takes a surface, smoothes it and returns the resulting xy coordinates
get.surface = function(idx, surfaces, do.smooth=0.3, nP = 256)
{
    if(do.smooth!=0)
    {		
        n <- length( surfaces[[idx]]$phi ) 
        x <- surfaces[[idx]]$phi
        x <- c(x[-n]-2*pi,x,2*pi+x[-1])
        y <- surfaces[[idx]]$r
        y <- c(y[-n],y,y[-1])
        smo <- smooth.spline(x,y,spar=0.3)
        #smo <- loess(y ~ x, span=1/nP*6, degree=2)
        phi <- seq(2*pi/nP,2*pi,length.out=nP)
        r <- predict(smo, phi)$y-2*SIZE/PIXELS
    }
    else
    {
        phi <- surfaces[[idx]]$phi
        r <- surfaces[[idx]]$r
    }
    
    return( list(x=surfaces[[idx]]$mid[1]+cos(phi)*r, y=surfaces[[idx]]$mid[2]+sin(phi)*r) )
}

read.cellID = function(filename, RFP=T, remove.irregular=F)
{
	raw_data <- read.table( filename, header=T)
	raw_data$xpos <- (raw_data$xpos - PIXELS/2)/PIX_PER_UM
	raw_data$ypos <- (PIXELS/2 - raw_data$ypos)/PIX_PER_UM

	attach(raw_data)	

	if(RFP) 
	{
		cells <- matrix(nrow=nrow(raw_data)/2, ncol=6)
		colnames(cells) <- c('ID', 'x', 'y', 'r', 'GFP', 'RFP')
		cells[, 1] = unique(cellID)
		cells[, 2] = xpos[flag==GFP]
		cells[, 3] = ypos[flag==GFP]
		cells[, 4] = .25*( maj.axis[flag==GFP] + min.axis[flag==GFP] )/PIX_PER_UM
		cells[, 5] = (f.tot[flag==GFP] + f.tot.m3[flag==GFP])/(a.tot.m3[flag==GFP] + a.tot[flag==GFP])/f.bg[flag==GFP] - 1
		cells[, 6] = f.tot[flag==RFP]/a.tot[flag==RFP]/f.bg[flag==RFP] - 1 
	}
	else 
	{
		cells <- matrix(nrow=nrow(raw_data), ncol=5)
		colnames(cells) <- c('ID', 'x', 'y', 'r', 'GFP')
		cells[, 1] <- cellID
		cells[, 2] <- xpos
		cells[, 3] <- ypos
		cells[, 4] <- .25*( maj.axis + min.axis )/PIX_PER_UM
		cells[, 5] <- (f.tot + f.tot.m3)/(a.tot.m3 + a.tot)/f.bg - 1
	}

	detach(raw_data)

	return( data.frame(cells) )
}

cm = colorRampPalette( c('blue', 'white', 'red') )

plot.profile = function(cells, surfs, vtu_mat, out_file = "profile.jpg", name.alpha=T)
{
	m = as.matrix(read.table(vtu_mat, header=F))
	x = seq(-ceiling(SIZE/1.5), ceiling(SIZE/1.5), length.out=512)

	jpeg(out_file, width=1700, height=1250, pointsize=40)
	l=layout(t(1:2), widths=c(3,1))
	image(x,y,m, col=cm(512), xlab=expression(paste("x [", mu, "m]")), ylab=expression(paste("y [", mu, "m]")))
	
	if( ncol(cells) == 6)
	{
		MATAL = cells$ID[cells$RFP>RFP_CUT]+1
    		MATA = cells$ID[cells$RFP<=RFP_CUT]+1
		sapply(MATAL, function(i){ s = get.surface(i, surfs); polygon(s$x, s$y, lwd=2, col="darkred")})
		sapply(MATA, function(i){ s = get.surface(i, surfs); polygon(s$x, s$y, lwd=2, col="white")})
		
	}
	else
		sapply(1:length(surfs), function(i){ s = get.surface(i, surfs); polygon(s$x, s$y, lwd=2, col="white")})
	
	scale = seq(min(m), max(m), length.out=512)
	
	if(name.alpha)
		image(y=scale, z=t(scale), col=cm(512), ylab=expression(paste(alpha-plain(factor)," [nM]",sep=" ")), xaxt="n")
	else
		image(y=scale, z=t(scale), col=cm(512), ylab="Bar1 activity [nM]", xaxt="n")
}
