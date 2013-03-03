import csv
from collections import defaultdict
from itertools import dropwhile
import subprocess


class Variable():
    def __init__(self, prof, course, quarter, cost):
        self.prof = prof
        self.course = course
        self.quarter = quarter
        self.cost = cost

    def __repr__(self):
        return str((self.get_name(), self.cost))

    def get_name(self):
        return "_".join(["x", self.prof, self.course, self.quarter])

    def get_mathprog_init(self):
        return "var " + self.get_name() + " >=0, binary;"

    def get_mathprog_z_contib(self):
        return "+" + str(self.cost) + "*" + self.get_name()

def getdata():


    reader = csv.reader(open('profcosts.csv'))

    costs = {}

    classes = reader.next()

    classes = ['0'] + classes[1:]

    for row in reader:
        costs[row[0]] = {}
        for i, cost in enumerate(row[1:]):
            costs[row[0]][classes[i+1]] = cost

    reader = csv.reader(open('classesneeded.csv'))

    quarters = map(lambda x: x.strip(), reader.next())

    quarters_dict = {quarter:[] for quarter in quarters }

    for row in reader:
        for i, course in enumerate(row):
            quarters_dict[quarters[i]].append(course)

    return costs, quarters_dict



def generate_variables(profs, quarters):
    variables = []

    for quarter, courses in quarters.iteritems():
        for course in courses:
            for prof in profs:
                variables.append(Variable(prof, course, quarter, profs[prof][course[:3]]))
    return variables


def generate_objective_function(variables):
    return "minimize z: " + " ".join(var.get_mathprog_z_contib() for var in variables) + ";"

def generate_variable_declarations(variables):
    return "\n".join(var.get_mathprog_init() for var in variables)

def generate_course_constraints(quarters, variables):
    constraints = ""
    for quarter, courses in quarters.iteritems():
        for course in courses:
            curr_constraint = "s.t. "  + quarter + "_" + course +" :"
            for var in variables:
                if var.course == course and var.quarter == quarter:
                    curr_constraint += " + " + var.get_name()
            curr_constraint += " = 1;\n"
            constraints += curr_constraint

    return constraints

def generate_prof_constraints(quarters, variables, profs):
    constraints = ""
    for quarter, courses in quarters.iteritems():
        for prof in profs:
            curr_constraint = "s.t. "  + quarter + "_" + prof +" :"
            for var in variables:
                if var.prof == prof and var.quarter == quarter:
                    curr_constraint += " + " + var.get_name()
            curr_constraint += " = 1;\n"
            constraints += curr_constraint

    return constraints

def generate_series_constraints(quarters, variables, series):

    def next_quarter(q):
        if q == 'Fall': return 'Winter'
        if q == 'Spring': return 'Spring'


    constraints = ""
    for course1, course2 in series:
        for quarter, courses in quarters.iteritems():
            for var1 in variables:
                if var1.course[:3] == course1 and var1.quarter == quarter:
                    for var2 in variables:
                        if var2.course[:3] == course2 \
                            and var2.course[3:] == var1.course[3:] \
                            and var2.prof == var1.prof \
                            and var2.quarter == next_quarter(quarter):

                            constraints += "s.t. " + "_".join([var1.prof, var1.course, var2.course]) \
                                         + " : " + var1.get_name()+ "=" +var2.get_name() + ";\n"

    return constraints









profs, quarters = getdata()
variables = generate_variables(profs, quarters)
decls = generate_variable_declarations(variables)
objective_func = generate_objective_function(variables)
course_constraints = generate_course_constraints(quarters, variables)
prof_constraints = generate_prof_constraints(quarters, variables, profs)
series_constraints = generate_series_constraints(quarters, variables, [('153', '154'),
                                                                       ('221', '222'),
                                                                       ('238', '239'),
                                                                       ('312', '313'),
                                                                       ('346', '347'),
                                                                       ('412', '413'),
                                                                       ('482', '483')])
problem = open('assignment.mod', 'w')
problem.write(decls)
problem.write("\n\n")
problem.write(objective_func)
problem.write("\n\n")
problem.write(course_constraints)
problem.write("\n\n")
problem.write(prof_constraints)
problem.write("\n")
problem.write(series_constraints)
problem.write("\n")
problem.write("end;")
problem.close()

cmd = "glpsol -m assignment.mod --write out.sol -o readable.sol".split(" ")
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

result = open('out.sol')

output = result.readlines()[-1200:]

for i, line in enumerate(output):
    if int(line.strip()) == 1:
        print variables[i]
