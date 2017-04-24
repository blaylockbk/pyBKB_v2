# Brian Blaylock
# April 7, 2016

# Two functions to conver V and U staggered grids to mass points.
# For example:
# Usefull to convert U winds, XLAT_U, and XLONG_U, to a mass point
# using basic averaging between the left and right side of the grid point.
        
import numpy as np  
          
def Vstagger_to_mass(V):
    """
    V are the data on the top and bottom of a grid box    
    A simple conversion of the V stagger grid to the mass points.
    Calculates the average of the top and bottom value of a grid box. Looping
    over all rows reduces the staggered grid to the same dimensions as the 
    mass point.
    Useful for converting V, XLAT_V, and XLONG_V to masspoints
    Differnce between XLAT_V and XLAT is usually small, on order of 10e-5
    
    (row_j1+row_j2)/2 = masspoint_inrow
    
    Input:
        Vgrid with size (##+1, ##)
    Output:
        V on mass points with size (##,##)
        
    """
    
    # create the first column manually to initialize the array with correct dimensions
    V_masspoint = (V[0,:]+V[1,:])/2. # average of first and second column
    V_num_rows = int(V.shape[0])-1 # we want one less row than we have
    
    # Loop through the rest of the rows
    # We want the same number of rows as we have columns.
    # Take the first and second row, average them, and store in first row in V_masspoint
    for row in range(1,V_num_rows):
        row_avg = (V[row,:]+V[row+1,:])/2.
        # Stack those onto the previous for the final array        
        V_masspoint = np.row_stack((V_masspoint,row_avg))
    
    return V_masspoint
    
def Ustagger_to_mass(U):
    """
    U are the data on the left and right of a grid box    
    A simple conversion of the U stagger grid to the mass points.
    Calculates the average of the left and right value of a grid box. Looping
    over all columns it reduces the staggered grid to the same dimensions as the 
    mass point.
    Useful for converting U, XLAT_U, and XLONG_U to masspoints
    Differnce between XLAT_U and XLAT is usually small, on order of 10e-5
    
    (column_j1+column_j2)/2 = masspoint_incolumn
    
    Input:
        Ugrid with size (##, ##+1)
    Output:
        U on mass points with size (##,##)
        
    """
    
    # create the first column manually to initialize the array with correct dimensions
    U_masspoint = (U[:,0]+U[:,1])/2. # average of first and second row
    U_num_cols = int(U.shape[1])-1 # we want one less column than we have
    # Loop through the rest of the columns
    # We want the same number of columns as we have rows.
    # Take the first and second column, average them, and store in first column in U_masspoint
    for col in range(1,U_num_cols):
        col_avg = (U[:,col]+U[:,col+1])/2.
        # Stack those onto the previous for the final array        
        U_masspoint = np.column_stack((U_masspoint,col_avg))
    
    return U_masspoint
        
if __name__=="__main__":
    V = np.array([[1,2,3],[4,5,6],[7,8,9],[1,2,3]])
    print V
    a = Vstagger_to_mass(V)
    print a

    print ""
    print ""

    U = np.array([[1,2,3,4],[4,5,6,7],[7,8,9,10]])
    print U
    b = Ustagger_to_mass(U)
    print b
