# Battleship_Solitaire_Solver
Program that solves Battleship Solitaire puzzles by encoding the puzzles as CPSs and implementing a CSP solver.

Battleship Solitaire shows the number of ship parts in each row and column, and your goal is to deduce the location of each ship.

You can play games of battleship solitaire for free at [https://lukerissacher.com/battleships ](https://lukerissacher.com/battleships) 

The following is a sample board we could potentially solve:

![image](https://github.com/danielrafiqueUtoronto/Battleship_Solitaire_Solver/assets/79722816/cafe2e99-0afc-4a25-bb5f-73e4fb7a7618)

The program uses forward checking and AC-3 arc consistency algorithms to solve the formulated CSP.

To run the program, input the following in terminal (sample input and output files are provided):
python3 battle.py --inputfile <input file> --outputfile <output file>
