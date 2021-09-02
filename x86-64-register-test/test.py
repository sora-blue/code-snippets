import random

register_data = dict()
register_num = 0
register_vis = []

# TO-DO: sum score for each process, visualize how many exercises have been done


def read_data(filepath):
    global register_num, register_data, register_vis
    f = open(filepath, mode="r", encoding="utf8")
    for line in f.readlines():
        line = line.strip()
        if len(line) == 0:
            continue
        if line[0:2] == "//":
            continue
        line = line.split('-')
        key = line.pop(0)
        if key not in register_data:
            register_num += 1
        register_data[key] = line
    register_vis = [False for i in range(register_num)]
    f.close()


def start_test():
    global register_num, register_data, register_vis
    while True:
        hav_responded = 0
        keys = [str(key) for key in register_data.keys()]
        while hav_responded < register_num:
            random_index = random.randint(0, register_num - 1)
            while register_vis[random_index]:
                random_index = random.randint(0, register_num - 1)
            hav_responded += 1

            assert register_num > 4;
            register = keys[random_index]
            register_bit = register_data[register][0]
            register_description = register_data[register][1]
            another_register = keys[random_index + 4 if random_index + 4 < register_num else random_index - 4]
            another_register_description = register_data[another_register][1]
            A_des = ""
            B_des = ""
            print("%s: How many bits? Which description is right?" % register)
            if random.randint(0, 1) == 1:
                A_des = register_description
                B_des = another_register_description
            else:
                A_des = another_register_description
                B_des = register_description
            print("A: %s\nB: %s" % (A_des, B_des))
            inputList = input("你的答案: ")
            if inputList == "exit":
                return
            bit, description = inputList.split(' ')
            description = A_des if description.find("A") != -1 or description.find("a") != -1 else B_des
            if len(description.strip()) == 0:
                description = ""
            if bit == register_bit and description == register_description:
                print("Correct!\n")
                register_vis[random_index] = True
            else:
                print("Wrong!\n %s:\n Bits: %s\n Description: %s\n" % (register, register_bit, register_description))
            print("------------------------------------------------")

        respond = input("You've completed all registers!\nWanna play again?(y/n)\n")
        if respond.find("y") == -1 and respond.find("Y") == -1:
            print("See u again.")
            break
        register_vis = [False for i in range(register_num)]


if __name__ == '__main__':
    read_data("data.txt")
    start_test()
