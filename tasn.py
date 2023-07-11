import os
import commands
import random
import json
import leven
#import subprocess
#random.seed(2)
funs = 3
seeds = 4
windows = funs+2
runs = 5
maxAct = 80
matrix1 = [[0 for j in range(funs)] for i in range(funs)]
matrix2 = [[0 for j in range(funs)] for i in range(funs)]

def getRandoms():
    q1s = []
    q2s = []
    for i in range(seeds):
        q1 = []
        q2 = []
        for j in range(windows):
            q1.append(random.randrange(funs))
            q2.append(random.randrange(funs))
        q1s.append(q1)
        q2s.append(q2)
    return q1s, q2s

def allRandoms():
    length = random.randrange(maxAct)
    q1 = []
    q2 = []
    for i in range(length):
        q1.append(random.randrange(funs))
        q2.append(random.randrange(funs))
    return q1,q2

def diff(q1s, q2s, m1, m2):
    global matrix1
    global matrix2
    index1 = 0
    index2 = 0
    diff1 = 0
    diff2 = 0
    for i in range(seeds):
        q1 = q1s[i]
        q2 = q2s[i]
        book1 = []
        book2 = []
        d1 = 0
        d2 = 0
        #print("\nq1s[i] : {}".format(q1s[i]))
        temp1 = [[0 for j in range(funs)] for k in range(funs)]
        temp2 = [[0 for j in range(funs)] for k in range(funs)]
        #print("m1[-1] : {}".format(m1[-1]))
        if(len(m2) > 0) :
            temp1[m1[-1]][q1[0]] = 1
            temp2[m2[-1]][q2[0]] = 1
        for j in range(windows-1):
            temp1[q1[j]][q1[j+1]] = 1
            temp2[q2[j]][q2[j+1]] = 1
        for j in range(windows):
            if(q1[j] not in m1 and q1[j] not in book1):
                book1.append(q1[j])
                d1 += 4
            if(q2[j] not in m2 and q2[j] not in book2):
                book2.append(q2[j])
                d2 += 4 
        #print("temp1 : {}".format(temp1))
        for j in range(funs):
            for k in range(funs):
                if(temp1[j][k] - matrix1[j][k] >= 1):
                    d1 += 1
                if(temp2[j][k] - matrix2[j][k] >= 1):
                    d2 += 1
        #print("d1:{}".format(d1))
        if (d1 >= diff1) :
            diff1 = d1
            index1 = i
            diffM1 = temp1[:]
        if (d2 >= diff2) :
            diff2 = d2
            index2 = i
            diffM2 = temp2[:]
    for j in range(funs):
        for k in range(funs):
            if(diff1 != 0 and diffM1[j][k] >= 1):
                matrix1[j][k] = 1
            if(diff2 != 0 and diffM2[j][k] >= 1):
                matrix2[j][k] = 1
    
    for i in range(windows):
        m1.append(q1s[index1][i])
        m2.append(q2s[index2][i])
    #print("matrix1 : {}".format(matrix1))
    return m1, m2

def test(q1, q2, num):
    output_file = open('outputTsan.txt', 'w')
    l = len(q1)
    mars = "python /workdir/DQNTest/mars/main.py --suffix_labels1=\""
    for i in range(l) :
        mars += str(q1[i])
        mars += ",0"
        if i < l - 1 :
            mars += ";"
        else:
            mars += "\""
    mars += " --suffix_labels2=\""
    for i in range(l) :
        mars += str(q2[i])
        mars += ",0"
        if i < l - 1 :
            mars += ";"
        else :
            mars += "\""
    print(mars)
    #mars = "python DQNTest/mars/main.py --suffix_labels1=\"1,0;1,0;1,0;0,0;1,0;1,0\" \
    #       --suffix_labels2=\"0,0;0,0;0,0;1,0;1,0;1,0\""
    commands.getoutput(mars)
    #os.system(mars)

    copy = "cp /workdir/DQNTest/mars/tests/test_try2_gen.cpp /workdir/threadTest/test_try2_gen.cpp"
    commands.getoutput(copy)
    #os.system(copy)

    build = "clang++ -fsanitize=thread -g -o thread{} test_try2_gen.cpp".format(num)
    #build = "clang++ -g -o thread{} test_try2_gen.cpp -lpthread".format(num)
    commands.getoutput(build)
    #os.system(build)
    '''
    test = "/workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 2 /workdir/PERIOD/test/mars/test_try2_gen"
    test = test.split(' ')
    subprocess.run(args=test, stdout=output_file, stderr=subprocess.STDOUT, timeout=600)
    #subprocess.run(args=test)
    '''
    output_file.close()

def getDataRace(num):
    
    r = "./thread{}".format(num)
    report = commands.getoutput(r)
    warnings = report.split("\n")
    warnFlag = "WARNING:"
    preFlag = "Previous"
    dataRace = {}
    key = ''
    flag = 0
    for line in warnings:
        words = list(filter(None, line.split(' ')))
        if flag is 4:
            key += words[2]
            dataRace[key] = 1
            key = ''
            flag = 5
        elif flag is 3:
            if preFlag in words:
                key += words[1]
                #print(words[1])
                flag = 4
        elif flag is 2:
            key += words[2]
            flag = 3
        elif flag is 1:
            key += words[0]
            #key += words[5]
            #print(words[0])
            flag = 2
        elif warnFlag in words:
            flag = 1
    '''
    with open('/workdir/dataRace.json', 'r') as f:
        dataRace = json.load(f)
    '''
    print(len(dataRace))
    return dataRace
    
                      

if __name__ == "__main__":

    times = 50
    #act = funs
    act = 1
    randomRace = [0]*runs
    testRace = [0]*runs
    allRace = [0]*runs
    levenRace = [0]*runs
    randomMax = [0]*runs
    testMax = [0]*runs
    allMax = [0]*runs
    levenMax = [0]*runs

    for ep in range(times) :
        
        print("times : {}".format(ep))
        '''
        s1, s2 = getRandoms()
        start1 = s1[0]
        start2 = s2[0]

        for i in range(windows-1):
            matrix1[start1[i]][start1[i+1]] = 1
            matrix2[start2[i]][start2[i+1]] = 1
        '''

        for i in range(funs):
            for j in range(funs):
                matrix1[i][j] = 0
                matrix2[i][j] = 0

        ever1 = []
        ever2 = []

        dataRace1 = {}
        dataRace2 = {}
        allRandomRace = {}
        levenTestRace = {}
        
        for i in range(runs):
            '''
            empty = []
            for k in range(act):
                ever1.append(empty[:])
                ever2.append(empty[:])
                leven1.append(empty[:])
                leven2.append(empty[:])
                random1.append(empty[:])
                random2.append(empty[:])
            
            for k in range(act):
                tempRandom1 = []
                tempRandom2 = []
                for j in range(windows):
                    tempRandom1.append(q1s[k][j])
                    tempRandom2.append(q2s[k][j])
                for index in range(windows):
                    random1[k].append(tempRandom1[index])
                    random2[k].append(tempRandom2[index])
            '''
            random1 = []
            random2 = []

            m1 = []
            m2 = []

            leven1 = []
            leven2 = []

            q1s, q2s = getRandoms()
            for j in range(windows):
                random1.append(q1s[0][j])
                random2.append(q2s[0][j])
            #allrandom1, allrandom2 = allRandoms()
            m1, m2 = diff(q1s, q2s, m1, m2)
            
            #for k in range(act):
            levenget1 = leven.get_best_case1(ever1, q1s)
            levenget2 = leven.get_best_case1(ever2, q2s)
            ever1.append(levenget1)
            ever2.append(levenget2)
            for j in range(windows):
                leven1.append(levenget1[j])
                leven2.append(levenget2[j])
                #q1s, q2s = getRandoms()
        
            
            #m2 = random2[0][:]
            #m2 = m1[:]
            '''
            print("random1 : {}".format(random1))
            print("random2 : {}".format(random2))
            print("m1 : {}".format(m1))
            print("m2 : {}".format(m2))
            '''
            #random
            num = 1
            for k in range(act):
                test(random1, random2, num)
                rRace = getDataRace(num)
                dataRace1.update(rRace)
            randomRace[i] += len(dataRace1)
            randomMax[i] = max(randomMax[i], len(dataRace1))
            
            #leven
            for k in range(act):
                test(leven1, leven2, num)
                rRace = getDataRace(num)
                levenTestRace.update(rRace)
            levenRace[i] += len(levenTestRace)
            levenMax[i] = max(levenMax[i], len(levenTestRace))
            '''
            #allRandom
            test(allrandom1, allrandom2, num)
            rRace = getDataRace(num)
            allRandomRace.update(rRace)
            allRace[i] += len(allRandomRace)
            allMax[i] = max(allMax[i], len(allRandomRace))
            '''
            #test
            for actor in range(act):
                actm = [actor] * len(m2)
                #test(actm, m2, num+1)
                test(m1, m2, num+1)
                mRace = getDataRace(num+1)
                dataRace2.update(mRace)
            testRace[i] += len(dataRace2)
            testMax[i] = max(testMax[i], len(dataRace2))

            print("\n")
            
    for i in range(runs):
        randomRace[i] = float(randomRace[i])/times
        testRace[i] = float(testRace[i])/times
        levenRace[i] = float(levenRace[i])/times

    print("randomRace : {}".format(randomRace))
    print("levenRace : {}".format(levenRace))
    print("testRace : {}".format(testRace))

    print("randomMax : {}".format(randomMax))
    print("levenMax : {}".format(levenMax))
    print("testMax : {}".format(testMax))