from navigator import *

starts = []
for i in range(10, 20):
    for j in range(25, 30):
        starts.append((i, j))
targets = []
for i in range(20, 25):
    for j in range(30, 35):
        targets.append((i, j))


navs=[]

for start in starts:
    for target in targets:
        navs.append(Navigator(start, target)) 
#print(navs)
#nav = Navigator((0, 0), (20, 6))



big_strides = [i for i in range(1, 3)]
max_steps_big_stride = [i for i in range(1, 3)]


output = ''''''


table = {
            0:["nav #", "start point", "target point", "bigstride steps", "stride size", "path length"]
        }

nav_counter = 1
row = 1
table[row] = []
for nav in navs:
    

    for max_steps_for_big_stride in max_steps_big_stride:
        
        for stride_ in big_strides:
            
            step_count = 0
            while (not (nav.current == nav.target)):
                
                if (step_count < max_steps_for_big_stride):
                    nav.step(stride = stride_)
                    step_count += 1
                else:
                    nav.step()
            table[row].append(nav_counter)
            table[row].append(f"{nav.start}")
            table[row].append(f"{nav.target}")
            table[row].append(max_steps_for_big_stride)
            table[row].append(stride_)
            table[row].append(len(nav.path))
            nav.path = [nav.start]
            nav.current = nav.start
            row += 1
            table[row] = []
            #print(table)
    nav_counter += 1

table.pop(row)


row = 0
table_string = ""
for row in list(table.keys()):
    column_string = ""
    for col in table[row]:
        
        column_string += f"{str(col):<22}"
    table_string += column_string + "\n"

with open("table.txt", "w") as file:
    file.write(table_string)
file.close()
#print(table_string)
