from csp import Constraint, Variable, CSP
from constraints import *
from backtracking import bt_search
import sys
import argparse
import copy

def print_solution(s, size):
  s_ = {}
  for (var, val) in s:
    s_[int(var.name())] = val
  for i in range(1, size-1):
    for j in range(1, size-1):
      print(s_[-1-(i*size+j)],end="")
    print('')

#parse board and ships info
#file = open(sys.argv[1], 'r')
#b = file.read()
parser = argparse.ArgumentParser()
parser.add_argument(
  "--inputfile",
  type=str,
  required=True,
  help="The input file that contains the puzzles."
)
parser.add_argument(
  "--outputfile",
  type=str,
  required=True,
  help="The output file that contains the solution."
)
args = parser.parse_args()
file = open(args.inputfile, 'r')
b = file.read()
b2 = b.split()
size = len(b2[0])
size = size + 2
b3 = []
b3 += ['0' + b2[0] + '0']
b3 += ['0' + b2[1] + '0']
b3 += [b2[2] + ('0' if len(b2[2]) == 3 else '')]
b3 += ['0' * size]
for i in range(3, len(b2)):
  b3 += ['0' + b2[i] + '0']
b3 += ['0' * size]

###################
#Pre-processing

#make grid
grid = list()
for i in b3[3:]:
  liststring = list(i)
  grid.append(liststring)

#make row constr
row_constraints = []
for i in b3[0:][0]:
  row_constraints += [int(i)]
#print(row_constraints)

#make col constr
col_constraints = []
for i in b3[1:][0]:
  col_constraints += [int(i)]
#print(col_constraints)

#if row adds up to 0, replace grid row with '.'
count = 1
for i in row_constraints[1:len(row_constraints)-1:]:
  if int(i) == 0:
      
    for j in range(1, len(row_constraints)-1):
      grid[count][j] = '.'
              
  count+=1
 
#if col adds up to 0, replace grid col with '.'
count = 1
for i in col_constraints[1:len(col_constraints)-1:]:
  if int(i) == 0:
      
    for j in range(1, len(col_constraints)-1):
      grid[j][count] = '.'
              
  count+=1

#for any KNOWN location of a piece either water or ship piece. remove that from domains and if a ship piece, make its surrounding pieces water and remove them from domain
for i in range(1, len(row_constraints)-1):
  for j in range(1, len(col_constraints)-1):
    
    if grid[i][j] in ['S']:
      #remove ij from domain and its surrounding pieces
      if i!=1 and i !=len(row_constraints)-1 and j!=1 and j!=len(row_constraints)-1: #if the known sub is not on edge of board
        grid[i-1][j] = grid[i+1][j] = grid[i][j-1] = grid[i][j+1] = grid[i-1][j-1] = grid[i-1][j+1] = grid[i+1][j-1] = grid[i+1][j+1] = '.'
        
          
      #if known sub is on top row and not on side edges
      elif i==1 and j!= 1 and j!=len(row_constraints)-1:
        grid[i][j-1] = grid[i][j+1] = grid[i+1][j] = grid[i+1][j-1] = grid[i+1][j+1] = '.'
          
      
      #if known sub is on bottom row and not on edges
      elif i==len(row_constraints)-1 and j!=1 and j!=len(row_constraints)-1:
        grid[i][j-1] = grid[i][j+1] = grid[i-1][j] = grid[i-1][j-1] = grid[i-1][j+1] = '.'
          
          
      #if known sub is on left edge
      elif i!=1 and i!=len(row_constraints)-1 and j == 1:
        grid[i-1][j] = grid[i+1][j] = grid[i-1][j+1] = grid[i+1][j+1] = grid[i][j+1] = '.'
          
                              
      #if known sub is on right edge
      elif i!= 1 and i!=len(row_constraints)-1 and j==len(row_constraints)-1:
        grid[i-1][j] = grid[i+1][j] = grid[i-1][j-1] = grid[i+1][j-1] = grid[i][j-1] = '.'
          
      #if known sub is left corner
      elif i==1 and j==1:
        grid[i+1][j] = grid[i][j+1] = grid[i+1][j+1] = '.'
      #if known sub is in right corner
      elif i== 1 and j== len(row_constraints)-1:
        grid[i+1][j] = grid[i][j-1] = grid[i+1][j-1] = '.'
          
      #if known sub is in bottom left corner
      elif i==len(row_constraints)-1 and j==1:
        grid[i-1][j] = grid[i][j+1] = grid[i-1][j+1] = '.'
          
      #if known sub is in bottom right corner
      elif i==len(row_constraints)-1 and j == len(row_constraints)-1:
        grid[i-1][j] = grid[i-1][j-1] = grid[i][j-1] = '.'

    elif grid[i][j] == '<':
      #if on grid top left edge
      if i==1 and j==1:
        grid[i+1][j] = grid[i+1][j+1] = '.'
      #if grid on bottom left edge
      elif i==len(row_constraints)-1 and j== 1:
        grid[i-1][j] = grid[i-1][j+1] = '.'
      #in between rows but on left edge
      elif i!=1 and i!=len(row_constraints)-1 and j==1:
        grid[i-1][j] = grid[i-1][j+1] = grid[i+1][j+1] = grid[i+1][j] = '.'
      #if anywhere else
      else:
        grid[i-1][j] = grid[i][j-1] = grid[i+1][j] = grid[i-1][j-1] = grid[i+1][j-1] = grid[i-1][j+1] = grid[i+1][j+1] = '.'

    elif grid[i][j] == '>':
      #if on grid top right edge
      if i==1 and j== len(row_constraints)-1:
        grid[i+1][j] = grid[i+1][j-1] = '.'
      #if grid on bottom right edge
      elif i==len(row_constraints)-1 and j==len(row_constraints)-1:
        grid[i-1][j] = grid[i-1][j-1] = '.'
      #in between rows but on right edge
      elif i!=1 and i!=len(row_constraints)-1 and j==len(row_constraints)-1:
        grid[i-1][j] = grid[i+1][j] = grid[i-1][j-1] = grid[i+1][j-1] = '.'
      #if anywhere else
      else:
        grid[i-1][j-1] = grid[i-1][j] = grid[i-1][j+1] = grid[i][j+1] = grid[i+1][j+1] = grid[i+1][j] = grid[i+1][j-1] = '.'

    elif grid[i][j] =='^':
      #top left
      if i==1 and j==1:
        grid[i][j+1] = grid[i+1][j+1] = '.'
      
      #top mid
      elif i==1 and j!=1 and j!=len(row_constraints)-1:
        grid[i][j-1] =grid[i][j+1] = grid[i+1][j+1] = grid[i+1][j-1] = '.'
      
      #top right
      elif i==1 and j==len(row_constraints)-1:
        grid[i][j-1] = grid[i+1][j-1] = '.'
      
      #right mid
      elif i!=1 and i!=len(row_constraints)-1 and j==len(row_constraints)-1:
        grid[i-1][j] = grid[i-1][j-1] = grid[i][j-1] = grid[i+1][j-1] = '.'
      
      #left mid
      elif i!=1 and i!=len(row_constraints) and j==1:
        grid[i-1][j] = grid[i-1][j+1] = grid[i][j+1] = grid[i+1][j+1] = '.'
      
      else:
        grid[i-1][j-1] = grid[i-1][j] = grid[i-1][j+1] = grid[i][j+1] = grid[i+1][j+1] = grid[i+1][j-1] = grid[i][j-1] = '.'
    
    elif grid[i][j] == 'v':
      if i==len(row_constraints)-1 and j==1:
        grid[i-1][j+1] = grid[i][j+1] = '.'
      elif i==len(row_constraints)-1 and j==len(row_constraints)-1:
        grid[i-1][j-1] = grid[i][j-1] = '.'
      
      elif i!=len(row_constraints)-1 and j==1:
        grid[i+1][j] = grid[i][j+1] = grid[i-1][j+1] = grid[i+1][j+1] = '.'
      
      elif i!= len(row_constraints)-1 and j==len(row_constraints)-1 :
        grid[i-1][j-1] = grid[i][j-1] = grid[i+1][j-1] = grid[i+1][j] = '.'
      
      elif i==len(row_constraints)-1 and j!=1 and j!=len(row_constraints)-1:
        grid[i][j-1] = grid[i][j+1] = grid[i-1][j+1] = grid[i-1][j-1] = '.'
      
      else:
        grid[i-1][j-1] = grid[i][j-1] = grid[i+1][j-1] = grid[i+1][j] = grid[i+1][j+1] = grid[i][j+1] = grid[i-1][j+1] = '.' 
    
    elif grid[i][j] == 'M':
      if j==1:
        grid[i-1][j+1] = grid[i+1][j+1] = '.'
      elif i==1:
        grid[i+1][j-1] = grid[i+1][j+1] = '.'
      elif j== len(row_constraints)-1:
        grid[i-1][j-1] = grid[i+1][j-1] = '.'
      elif i== len(row_constraints)-1:
        grid[i-1][j-1] = grid[i-1][j+1] = '.'
      else:
        grid[i-1][j-1] = grid[i-1][j+1] = grid[i+1][j+1] = grid[i+1][j-1] = '.'
    
def display_grid(grid):
  for i in grid:
    for j in i:
        print(j, end="")
    print("")
        
####################
for i in range(len(grid)):
  resstr = ''.join(grid[i])
  b3[3+i] = resstr
  #print(resstr)


board = "\n".join(b3)
print(board)
print("")

input_grid = copy.deepcopy(grid)
#display_grid(input_grid)

varlist = []
varn = {}
conslist = []


#1/0 variables
for i in range(0,size):
  for j in range(0, size):
    v = None
    if i == 0 or i == size-1 or j == 0 or j == size-1:
      v = Variable(str(-1-(i*size+j)), [0]) #for padded border of water
    else:
      v = Variable(str(-1-(i*size+j)), [0,1]) #either water or ship part
    varlist.append(v)
    varn[str(-1-(i*size+j))] = v #making a dictionary with key as variable # 0 to size and value as the actual Variable object

#make 1/0 variables match board info
ii = 0
for i in board.split()[3:]:
  jj = 0
  for j in i:
    if j != '0' and j != '.':
      conslist.append(TableConstraint('boolean_match', [varn[str(-1-(ii*size+jj))]], [[1]]))
    elif j == '.':
      conslist.append(TableConstraint('boolean_match', [varn[str(-1-(ii*size+jj))]], [[0]]))
    jj += 1
  ii += 1

#row and column constraints on 1/0 variables
row_constraint = []
for i in board.split()[0]:
  row_constraint += [int(i)]

for row in range(0,size):
  conslist.append(NValuesConstraint('row', [varn[str(-1-(row*size+col))] for col in range(0,size)], [1], row_constraint[row], row_constraint[row]))

col_constraint = []
for i in board.split()[1]:
  col_constraint += [int(i)]

for col in range(0,size):
  conslist.append(NValuesConstraint('col', [varn[str(-1-(col+row*size))] for row in range(0,size)], [1], col_constraint[col], col_constraint[col]))

#diagonal constraints on 1/0 variables
for i in range(1, size-1):
    for j in range(1, size-1):
      for k in range(9):
        conslist.append(NValuesConstraint('diag', [varn[str(-1-(i*size+j))], varn[str(-1-((i-1)*size+(j-1)))]], [1], 0, 1))
        conslist.append(NValuesConstraint('diag', [varn[str(-1-(i*size+j))], varn[str(-1-((i-1)*size+(j+1)))]], [1], 0, 1))

#ship constraints on 1/0 variables

"""
#./S/</>/v/^/M variables
#these would be added to the csp as well, before searching,
#along with other constraints
for i in range(0, size):
  for j in range(0, size):
    v = Variable(str(i*size+j), ['.', 'S', '<', '^', 'v', 'M', '>'])
    varlist.append(v)
    varn[str(str(i*size+j))] = v
    #connect 1/0 variables to W/S/L/R/B/T/M variables
    conslist.append(TableConstraint('connect', [varn[str(-1-(i*size+j))], varn[str(i*size+j)]], [[0,'.'],[1,'S'],[1,'<'],[1,'^'],[1,'v'],[1,'M'],[1,'>']]))
"""

#check solution valid
def check_valid(s, size, sub, des, crus, bat, input_grid):
  #takes in a solution and returns if its valid based on constraints and also converts board to correct symbols
  s_ = {}
  grid = []
  for (var, val) in s:
    s_[int(var.name())] = val
  for i in range(0, size):
    temp = list()
    for j in range(0, size):
      temp.append(s_[-1-(i*size+j)])
    grid.append(temp)
    
  real_edge = len(grid)-1
  
  num_subs = 0
  num_des = 0
  num_crus = 0
  num_bat = 0
  valid = False
  
  for i in range(1, real_edge):
    for j in range(1, real_edge):
      #if subsequent 1s alligned count as ship and convert to ship icons
      
      #identify subs
      if grid[i][j] == 1 and grid[i][j+1] == 0 and grid[i+1][j] == 0 and grid[i-1][j] == 0:
        grid[i][j] = 'S'
        num_subs+=1
      #identify destroyers horizontal
      if j!=real_edge:
        if grid[i][j] == 1 and grid[i][j+1] == 1 and grid[i][j+2]==0:
          grid[i][j] = '<'
          grid[i][j+1] = '>'
          num_des+=1
      #identify cruisers horizontal
      if j!= real_edge-1:
        if grid[i][j] == 1 and grid[i][j+1] == 1 and grid[i][j+2] == 1 and grid[i][j+3] == 0:
          grid[i][j] = '<'
          grid[i][j+1] = 'M'
          grid[i][j+2] = '>'
          num_crus+=1
      
      #identify battleships horizontal
      if j!= real_edge-2:
        if grid[i][j] == 1 and grid[i][j+1] == 1 and grid[i][j+2] == 1 and grid[i][j+3] == 1 and grid[i][j+4] == 0:
          grid[i][j] = '<'
          grid[i][j+1] = 'M'
          grid[i][j+2] = 'M'
          grid[i][j+3] = '>'
          num_bat+=1
      #identify destoryers vertical
      if i!=real_edge:
        if grid[i][j] == 1 and grid[i+1][j] == 1 and grid[i+2][j] == 0:
          grid[i][j] = '^'
          grid[i+1][j] = 'v'
          num_des+=1
          
      if i!=real_edge-1:
        if grid[i][j] == 1 and grid[i+1][j] == 1 and grid[i+2][j] == 1 and grid[i+3][j] == 0:
          grid[i][j] = '^'
          grid[i+1][j] = 'M'
          grid[i+2][j] = 'v'
          num_crus+=1
          
      if i!=real_edge-2:
        if grid[i][j] == 1 and grid[i+1][j] == 1 and grid[i+2][j] == 1 and grid[i+3][j] == 1 and grid[i+4][j]==0:
          grid[i][j] = '^'
          grid[i+1][j] = 'M'
          grid[i+2][j] = 'M'
          grid[i+3][j] = 'v'
          num_bat+=1
  
  for i in range(real_edge):
    for j in range(real_edge):
      if grid[i][j] == 0:
        grid[i][j] = '.'
  
  
  if num_subs == sub and num_des == des and num_crus ==crus and num_bat == bat:
    valid = True
    
  #now check if solution pieces match puzzle givens
  for i in range(1, real_edge):
    for j in range(1, real_edge):
      if input_grid[i][j]!='0':
        if grid[i][j] != input_grid[i][j]:
          valid = False
  
  return grid, valid

#find all solutions and check which one has right ship #'s
csp = CSP('battleship', varlist, conslist)
solutions, num_nodes = bt_search('GAC', csp, 'mrv', True, False)
#print("numSols")
#print(len(solutions))
outputfile = open(args.outputfile, "w")

ship_constraints = []
for i in board.split()[2]:
  ship_constraints += [int(i)]
#print(ship_constraints)

for i in range(len(solutions)):
  
  grid, valid = check_valid(solutions[i], size, ship_constraints[0], ship_constraints[1], ship_constraints[2], ship_constraints[3], input_grid)
  if valid == True:
    for i in range(1, len(grid)-1):
      for j in range(1, len(grid)-1):
        print(grid[i][j], end='')
        outputfile.write(f'{grid[i][j]}')
      outputfile.write("\n")
      print("")

"""
sys.stdout = open(args.outputfile, 'w')
for i in range(len(solutions)):
    print_solution(solutions[i], size)
    print("--------------")
"""