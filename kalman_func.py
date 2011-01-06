import numpy

def kalman(z, z_sigma, Q, dt):

	sz = (len(z),)

	# allocate space for arrays
	xhat=numpy.zeros(sz)      # a posteri estimate of x
	P=numpy.zeros(sz)         # a posteri error estimate
	xhatminus=numpy.zeros(sz) # a priori estimate of x
	Pminus=numpy.zeros(sz)    # a priori error estimate
	K=numpy.zeros(sz)         # gain or blending factor


	#extra, for calculated system dynamics
	x_dt			= numpy.zeros(sz)	#the measurements derivatives. We use this to decide if we should increase or lower our estimates
	x_dt2			= numpy.zeros(sz)	#the measurements derivatives. We use this to decide if we should increase or lower our estimates
	z_dt			= numpy.zeros(sz)	#the measurements derivatives. We use this to decide if we should increase or lower our estimates
	z_dt2			= numpy.zeros(sz)	#the measurements derivatives. We use this to decide if we should increase or lower our estimates
	x_integral 		= numpy.zeros(sz)
	xhat_integral 	= numpy.zeros(sz)
	z_integral 		= numpy.zeros(sz)
	xhat_int_error	= numpy.zeros(sz)
	z_int_error		= numpy.zeros(sz)

	R = z_sigma**2 # estimate of measurement variance, change to see effect

	# intial guesses
	xhat[0] = z[0]
	P[0] = 1e-1

	n_iter  = len(z)
	for k in range(1,n_iter):
	    # time update	
	    xhatminus[k] 	= (xhat[k-1]) +  (x_dt[k-1]+x_dt2[k-1])*dt
	    Pminus[k] 		= P[k-1]+Q

	    # measurement update
	    K[k] 		= Pminus[k]/( Pminus[k]+R )
	    xhat[k] 	= xhatminus[k]	+	K[k]*(z[k]-xhatminus[k])
	    P[k] 		= (1-K[k])*Pminus[k]

	    x_dt[k] 	= (xhat[k] - xhat[k-1])		#first derivative
	    x_dt2[k] 	= (x_dt[k] - x_dt[k-1])		#second derivative
	    z_dt[k] 	= (z[k] 	- z[k-1])		#first derivative
	    z_dt2[k] 	= (z_dt[k] - z_dt[k-1])		#second derivative

	    #x_integral[k] 		=	x_integral[k-1]		+ x[k]*dt 
	    xhat_integral[k] 	=	xhat_integral[k-1]	+ xhat[k]*dt
	    z_integral[k]		=	z_integral[k-1]		+ z[k]*dt
	    
	    #xhat_int_error[k]	=	x_integral[k] - xhat_integral[k]
	    #z_int_error[k]		=	x_integral[k] - z_integral[k]

	return (xhat, xhat_integral, z_integral)	    