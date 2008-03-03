debug=0
"""
Codes are based on http://www.nar-associates.com/nurbs/c_code.html#chapter3
"""

"""
/*
    Subroutine to generate a B-spline open knot vector with multiplicity
    equal to the order at the ends.
	
    c            = order of the basis function
    n            = the number of defining polygon vertices
    nplus2       = index of x() for the first occurence of the maximum knot vector value
    nplusc       = maximum value of the knot vector -- $n + c$
    x()          = array containing the knot vector
*/

knot(n,c,x)

int n,c;
int x[];

{
	int nplusc,nplus2,i;

	nplusc = n + c;
	nplus2 = n + 2;

	x[1] = 0;
		for (i = 2; i <= nplusc; i++){
		    if ( (i > c) && (i < nplus2) )
				x[i] = x[i-1] + 1;
	    else
				x[i] = x[i-1];
		}
}

"""
"""
  n          - the number of control points minus 1
  t          - the degree of the polynomial plus 1
void compute_intervals(int *u, int n, int t)   // figure out the knots
{
  int j;

  for (j=0; j<=n+t; j++)
  {
    if (j<t)
      u[j]=0;
    else
    if ((t<=j) && (j<=n))
      u[j]=j-t+1;
    else
    if (j>n)
      u[j]=n-t+2;  // if n-t=-2 then we're screwed, everything goes to 0
  }
}
"""

def knot(npts,order):
	x=[]
	x.append(0)
	mode=1
	for i in range(1,npts+order,1):
		if mode==2 and i<order:
			x.append(0)
		elif i>=order and i<=npts:
			if mode==1:
				x.append(x[i-1]+1)
			else:
				x.append(i-order+1)
		else:
			if mode==1:
				x.append(x[i-1])
			else:
				x.append(npts-order+2)
	return x


"""
/*  Subroutine to generate B-spline basis functions for open knot vectors

	C code for An Introduction to NURBS
	by David F. Rogers. Copyright (C) 2000 David F. Rogers,
	All rights reserved.
	
	Name: basis.c
	Language: C
	Subroutines called: none
	Book reference: p. 279

    c        = order of the B-spline basis function
    d        = first term of the basis function recursion relation
    e        = second term of the basis function recursion relation
    npts     = number of defining polygon vertices
    n[]      = array containing the basis functions
               n[1] contains the basis function associated with B1 etc.
    nplusc   = constant -- npts + c -- maximum number of knot values
    t        = parameter value
    temp[]   = temporary array
    x[]      = knot vector
*/	

#include 	<stdio.h>

basis(c,t,npts,x,n)

int c,npts;
int x[];
float t;
float n[];

{
	int nplusc;
	int i,k;
	float d,e;
	float temp[36];

	nplusc = npts + c;

/*		printf("knot vector is \n");
		for (i = 1; i <= nplusc; i++){
			printf(" %d %d \n", i,x[i]);
		}
		printf("t is %f \n", t);
*/

/* calculate the first order basis functions n[i][1]	*/

	for (i = 1; i<= nplusc-1; i++){
	    	if (( t >= x[i]) && (t < x[i+1]))
				temp[i] = 1;
		    else
				temp[i] = 0;
	}

/* calculate the higher order basis functions */

	for (k = 2; k <= c; k++){
	    	for (i = 1; i <= nplusc-k; i++){
		        	if (temp[i] != 0)    /* if the lower order basis function is zero skip the calculation */
	           			d = ((t-x[i])*temp[i])/(x[i+k-1]-x[i]);
			        else
				d = 0;
	
		    	    if (temp[i+1] != 0)     /* if the lower order basis function is zero skip the calculation */
	        			e = ((x[i+k]-t)*temp[i+1])/(x[i+k]-x[i+1]);
		        	else
	    			e = 0;
	
	    	    	temp[i] = d + e;
		}
	}
	
		if (t == (float)x[nplusc]){		/*    pick up last point	*/
	 		temp[npts] = 1;
		}
	
	/* put in n array	*/
	
		for (i = 1; i <= npts; i++) {
	    	n[i] = temp[i];
	}
}

"""

def basis(order,parameter,npts,knots):
	nplusc=npts+order
	basis_values=[]
	for i in range(0,nplusc-1,1):
		if parameter>=knots[i] and parameter<knots[i+1]:
			basis_values.append(1)
		else:
			basis_values.append(0)

	for k in range(2,order+1,1):
		for i in range(0,nplusc-k,1):
			if basis_values[i]!=0:
				d=((parameter-knots[i])*basis_values[i])/(knots[i+k-1]-knots[i])
			else:
				d=0
			if basis_values[i+1]!=0:
				e=((knots[i+k]-parameter)*basis_values[i+1])/(knots[i+k]-knots[i+1])
			else:
				e=0
			basis_values[i]=d+e
	if parameter==knots[nplusc-1]:
		basis_values[npts-1]=1
	if debug>1:
		print 'basis:',"order=",order,"parameter=",parameter,"npts=",npts,"knots=",knots
		print "\tbasis_values=",basis_values
	return basis_values

"""
/*  Subroutine to generate a B-spline curve using an uniform open knot vector

	C code for An Introduction to NURBS
	by David F. Rogers. Copyright (C) 2000 David F. Rogers,
	All rights reserved.
	
	Name: bspline.c
	Language: C
	Subroutines called: knot.c, basis.c, fmtmul.c
	Book reference: Section 3.5, Ex. 3.4, Alg. p. 281

    b[]        = array containing the defining polygon vertices
                  b[1] contains the x-component of the vertex
                  b[2] contains the y-component of the vertex
                  b[3] contains the z-component of the vertex
    k           = order of the \bsp basis function
    nbasis      = array containing the basis functions for a single value of t
    nplusc      = number of knot values
    npts        = number of defining polygon vertices
    p[,]        = array containing the curve points
                  p[1] contains the x-component of the point
                  p[2] contains the y-component of the point
                  p[3] contains the z-component of the point
    p1          = number of points to be calculated on the curve
    t           = parameter value 0 <= t <= 1
    x[]         = array containing the knot vector
*/

bspline(npts,k,p1,b,p)

int npts,k,p1;

float b[];
float p[];

{
	int i,j,icount,jcount;
	int i1;
	int x[30];		/* allows for 20 data points with basis function of order 5 */
	int nplusc;

	float step;
	float t;
	float nbasis[20];
	float temp;


	nplusc = npts + k;

/*  zero and redimension the knot vector and the basis array */

	for(i = 0; i <= npts; i++){
		 nbasis[i] = 0.;
	}

	for(i = 0; i <= nplusc; i++){
		 x[i] = 0.;
		}

/* generate the uniform open knot vector */

	knot(npts,k,x);

/*
	printf("The knot vector is ");
	for (i = 1; i <= nplusc; i++){
		printf(" %d ", x[i]);
	}
	printf("\n");
*/

	icount = 0;

/*    calculate the points on the bspline curve */

	t = 0;
	step = ((float)x[nplusc])/((float)(p1-1));

	for (i1 = 1; i1<= p1; i1++){

		if ((float)x[nplusc] - t < 5e-6){
			t = (float)x[nplusc];
		}

	    basis(k,t,npts,x,nbasis);      /* generate the basis function for this value of t */
/*
		printf("t = %f \n",t);
		printf("nbasis = ");
		for (i = 1; i <= npts; i++){
			printf("%f  ",nbasis[i]);
		}
		printf("\n");
*/
		for (j = 1; j <= 3; j++){      /* generate a point on the curve */
			jcount = j;
			p[icount+j] = 0.;

			for (i = 1; i <= npts; i++){ /* Do local matrix multiplication */
				temp = nbasis[i]*b[jcount];
			    p[icount + j] = p[icount + j] + temp;
/*
				printf("jcount,nbasis,b,nbasis*b,p = %d %f %f %f %f\n",jcount,nbasis[i],b[jcount],temp,p[icount+j]);
*/
				jcount = jcount + 3;
			}
		}
/*
		printf("icount, p %d %f %f %f \n",icount,p[icount+1],p[icount+2],p[icount+3]);
*/
    	icount = icount + 3;
		t = t + step;
	}
}



"""

def bspline(orig_points,order=1):
	npts=len(orig_points)
	max_dimension=len(orig_points[0])
	p1=npts*5
	nplusc=npts+order
	knots=knot(npts,order)

	step=float(knots[nplusc-1])/float(p1-1)
	if debug>1:
		print 'step',step,"=",knots[nplusc-1],"/",p1-1

	result_points=[]
	for result_point_pos in range(0,p1,1):
		if debug>1:
			print "result_point_pos=",result_point_pos
		parameter=result_point_pos*step
		if (float(knots[-1])-parameter) < 5e-6:
			parameter=knots[-1]
		nbasis=basis(order,parameter,npts,knots) #(order,parameter,npts,knots)
		result_point=[0.0]*max_dimension
		for dimension in range(0,max_dimension,1):
			if debug>1:
				print "\tdimension=",dimension
			for current_point in range(0,npts,1):
				temp=nbasis[current_point]*orig_points[current_point][dimension]
				result_point[dimension]+=temp
				if debug>1:
					print "\t\tnbasis[",current_point,"]=",nbasis[current_point],"*",orig_points[current_point][dimension],"=",temp
		result_points.append(result_point)
	return result_points
		
		
if __name__=='__main__':

	orig_points=[
		[1,1],
		[2,3],
		[4,3],
		[3,1]
	]
	result_points=bspline(orig_points,2)
	print result_points
	