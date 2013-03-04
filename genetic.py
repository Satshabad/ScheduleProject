import csv
import random

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


def generate_pop(profs, quarters, size):

    chromos = []

    for __ in range(size):
        chromo = {}

        for quarter, courses in quarters.iteritems():
            prof_list = profs.keys()
            chromo[quarter] = {}
            for course in courses:
                prof_pick = random.randint(0, len(prof_list)-1)
                chromo[quarter][course] = prof_list[prof_pick]
                del prof_list[prof_pick]



        chromos.append(chromo)
    return chromos

def get_fitness(chromo, costs):
    fitness = 0
    for quarter, courses in chromo.iteritems():
        for course, prof in courses.iteritems():
            fitness += int(costs[prof][course[:3]])

    return fitness

def mutate_all(chromos):

    for chromo in chromos:
        for quarter, courses in chromo.iteritems():
            if random.randint(0, 1):
                for __ in range(random.randint(0, 6)):
                    course_list = courses.keys()
                    swap_course1 = course_list[random.randint(0, len(courses.keys())-1)]
                    swap_course2 = course_list[random.randint(0, len(courses.keys())-1)]
                    temp_prof = courses[swap_course1]
                    courses[swap_course1] = courses[swap_course2]
                    courses[swap_course2] = temp_prof
    return chromos

def prune(chromos):

    ranked = []

    for chromo in chromos:
        ranked.append((chromo, get_fitness(chromo))

    ranked.sort(key=lambda x: x[1]))





profs, quarters = getdata()
pop = generate_pop(profs, quarters, 100)

for _ in range(100000):

    mut_pop = mutate_all(pop)
    pop = prune(pop+mut_pop)

    print best(pop)

























