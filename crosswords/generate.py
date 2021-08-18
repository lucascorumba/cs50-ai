import sys
from itertools import product
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var, domain in self.domains.items():
            domain_copy = copy.deepcopy(domain)
            for word in domain_copy:
                if len(word) != var.length:
                    self.domains[var].remove(word)
        return

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        change = False
        # If words overlap
        if self.crossword.overlaps[x, y] is not None:
            domains_copy = copy.deepcopy(self.domains[x])
            # Loop through x's and y's domains
            for i in domains_copy:
                temp_i = set(i)
                # Checks all words in y's domain to current word in x's domain
                for j in self.domains[y]:
                    temp_j = set(j)
                    # If no intersection
                    if temp_i.intersection(temp_j) == 0:
                        # Remove word from x's domain
                        self.domains[x].remove(i)
                        change = True
        return change

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            temp, queue = list(product(self.crossword.variables, self.crossword.variables)), list()
            for arc in temp:
                if arc[0] == arc[1]:
                    continue
                if self.crossword.overlaps[arc[0], arc[1]] is not None:
                    queue.append(arc)
        else:
            queue = arcs
        # Repeat until queue is empty
        while queue:
            x, y = queue.pop(0)
            # Make arc consistent with y
            if self.revise(x, y):
                # If domain is empty -> no solution
                if not self.domains[x]:
                    return False
                # Append arc to queue after changing domain
                for z in (self.crossword.neighbors(x) - {y}):
                    queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if all(assignment.values()) and set(assignment.keys()) == self.crossword.variables:
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        values = list()
        for var, word in assignment.items():
            values.append(word)
            # Word with wrong length
            if var.length != len(word):
                return False
            neighbors = self.crossword.neighbors(var).intersection(assignment.keys())
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[var, neighbor]
                # Conflicting with neighboring variables
                if word[overlap[0]] != assignment[neighbor][overlap[1]]:
                    return False
        # Assignments using same word
        if len(values) != len(set(values)):
            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        var_domain = self.domains[var]
        # Dict mapping values (from var's domain) and how many values they rule out (from neighbors)
        effect_on_neighbors = {
            value: 0 for value in var_domain
        }
        for value in var_domain:
            # Reset ruled_out counter
            ruled_out = 0
            # Loop through var's unassigned neighbors
            for neighbor in (self.crossword.neighbors(var) - assignment.keys()):
                overlap = self.crossword.overlaps[var, neighbor]
                # Loop through neighbor's domain
                for word in self.domains[neighbor]:
                    # If the overlapping character is different, the word is ruled out
                    if value[overlap[0]] != word[overlap[1]]:
                        ruled_out += 1
            # Update dict
            effect_on_neighbors[value] = ruled_out
        ordered = list(effect_on_neighbors.items())
        # Sort values based on how many values they rule out from neighbors
        ordered.sort(key= lambda n:n[1])
        return [value for value, order in ordered]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get unassigned variables
        unassigned = (self.crossword.variables - assignment.keys())
        current_lowest, selected_var = float('inf'), list()
        for var in unassigned:
            domain_length = len(self.domains[var])
            # Checks if current domain is smaller than previous
            if domain_length < current_lowest:
                selected_var.clear()
                current_lowest = domain_length
                selected_var.append(var)
            # If it's equal to previous, append to list of 'tied' domains
            if domain_length == current_lowest:
                selected_var.append(var)
        if len(selected_var) == 1:
            return selected_var[0]
        # Initialize a list with (variable, degree) tuples for tied variables 
        degree = list((var, len(self.crossword.neighbors(var))) for var in selected_var)
        # Sort by highest degree -> number of nodes attached to this node
        degree.sort(key = lambda n:n[1], reverse=True)
        return degree[0][0]          

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = copy.deepcopy(assignment)
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
            assignment.pop(var, None)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
