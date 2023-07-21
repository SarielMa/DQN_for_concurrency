import docker
import random
#q1 = [0,0,0,0,0,0,0,0]
#q2 = [0,0,0,0,0,0,0,0]

#q1 = [1,1,1,1,1,1,1,1]
#q2 = [1,1,1,1,1,1,1,1]

class stealQueue(object):
    def __init__(self):
        super(stealQueue, self).__init__()
        #self.queue1 = [0,0,0,0,0,0,0,0]
        #self.queue2 = [0,0,0,0,0,0,0,0]

        self.max_action = 3
        self.queue1 = [random.randint(0, self.max_action - 1) for _ in range(8)]
        self.queue2 = [random.randint(0, self.max_action - 1) for _ in range(8)]

        #self.action_space = [0,1,2,3,4,5,6,7]
        self.n_actions = len(self.queue1) # length of the queries
        self.n_features = len(self.queue1) * 2  # state/observation 
        self.max_step = 10 # number of iters in each epoch
        self.steps = 0 # counter
        client = docker.from_env()
        containerId = "ef22199e51c69421943234a98110001fa6ac37a94521367b4621554b3846e0f9"
        self.container = client.containers.get(containerId)
        self.someReword = {}
        

    def step(self, action):
        self.steps += 1
        self.queue2[action] = (self.queue2[action] + 1)%self.max_action
        #当前状态 归一化
        state = (self.queue1 + self.queue2) 
        state_ = [item/self.max_action for item in state]
        tupleS = tuple(state_)
        if self.someReword.get(tupleS) is not None: # this can be removed 
            reward = self.someReword[tupleS]
        else :
            reward = self.getReward_tasn() # remove the duplicates
            self.someReword[tupleS] = reward
        end = False
        if self.steps >= self.max_step :
            end = True
            self.steps = 0
        return state_, reward, end
    
    def getReward_tasn(self) :
        #defult: python dockerTest.py --suffix_labels1=\"1,0;1,0;0,0;1,0;0,0;0,0\" --suffix_labels2=\"0,0;1,0;0,0;1,0;1,0;1,0\"
        #defult: python /workdir/PERIOD/test/mars/test.py --suffix_labels1=\"1,0;1,0;0,0;1,0;0,0;0,0\" --suffix_labels2=\"0,0;1,0;0,0;1,0;1,0;1,0\"
        run = "python /workdir/PERIOD/test/mars/test.py --suffix_labels1=\""
        for i in range(int(self.n_features/2)) :
            run += str(self.queue1[i])
            run += ",0"
            if i < self.n_features/2 - 1 :
                run += ";"
            else :
                run += "\""
        run += " --suffix_labels2=\""
        for i in range(int(self.n_features/2)) :
            run += str(self.queue2[i])
            run += ",0"
            if i < self.n_features/2 - 1 :
                run += ";"
            else :
                run += "\""
        ping = self.container.exec_run(run)
        warnings = ping.output.decode("utf-8").split("\n")
        reward = 0
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

        return len(dataRace)
       
    def reset(self) :
        self.queue1 = [random.randint(0,1) for _ in range(8)]
        self.queue2 = [random.randint(0,1) for _ in range(8)]
        self.steps = 0
        state = (self.queue1 + self.queue2)
        state_ = [item/self.max_action for item in state]
        return state_
    
    def getReward(self) :
        #defult: python dockerTest.py --suffix_labels1=\"1,0;1,0;0,0;1,0;0,0;0,0\" --suffix_labels2=\"0,0;1,0;0,0;1,0;1,0;1,0\"
        run = "python /workdir/PERIOD/test/mars/test_Peroid.py --suffix_labels1=\""
        for i in range(int(self.n_features/2)) :
            run += str(self.queue1[i])
            run += ",0"
            if i < self.n_features/2 - 1 :
                run += ";"
            else :
                run += "\""
        run += "--suffix_labels2=\""
        for i in range(int(self.n_features/2)) :
            run += str(self.queue2[i])
            run += ",0"
            if i < self.n_features/2 - 1 :
                run += ";"
            else :
                run += "\""
        #docker run period
        ping = self.container.exec_run(run)
        lines = ping.output.decode("utf-8").split("\n")
        reward = 0
        for line in lines :
            print (line)
            if line.find("Error")>=0 and line.find("Interleavings")>=0 :
                nums = line.split(" ")
                reward = nums[3]
                break
        return int(reward)
    



