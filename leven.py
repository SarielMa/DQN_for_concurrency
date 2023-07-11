

def get_best_case1(el,cl):#max dis from all  
    maxdis=0
    #best_case = cl[0]
    for c in cl:
        dis=0
        for ce in el:
            edis=distance(c,ce)
            dis+=edis
        if maxdis<=dis:
            maxdis=dis
            best_case=c
    '''print 'best is '+str(best_case)'''
    return best_case

def distance(c4,c3):
    return levenshtein(c4, c3)
	#return levenshtein(c4[1],c3[1])+levenshtein(c4[2],c3[2])#only compare suffixes differences

def levenshtein(s1,s2):
    if len(s1)>len(s2):
        return levenshtein(s2,s1)
    distances=range(len(s1)+1)
    for i2,c2 in enumerate(s2):
        distances_=[i2+1]
        for i1,c1 in enumerate(s1):
            if c1==c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1+min(distances[i1],distances[i1+1],distances_[-1]))
        distances=distances_
    return distances[-1]

if __name__ == "__main__":
    s1 = [0,1,2]
    s2 = [1,0,1]
    s3 = [2,1,1]
    s4 = []
    s4.append(s2)
    s4.append(s3)
    s5 = []
    #s5.append(s1)
    c = get_best_case1(s5, s4)
    print(c)

