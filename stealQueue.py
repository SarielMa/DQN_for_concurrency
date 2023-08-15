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
        self.sequence_len = 8
        self.max_action = 3
        self.queue1 = [random.randint(0, self.max_action - 1) for _ in range(self.sequence_len)]
        self.queue2 = [random.randint(0, self.max_action - 1) for _ in range(self.sequence_len)]

        #self.action_space = [0,1,2,3,4,5,6,7]
        # try increasing steps
        self.n_actions = self.sequence_len * 2 * self.max_action # length of the queries
        self.n_features = self.sequence_len * 2  # state/observation , for this, it is the binary sequence in the test case
        #[1,2,...8][2,3,..9]...[12,...x] => [1...1] 
        # I want to encode all the existing sequence as the state... how?
        self.max_step = 50 # upper bound of number of iters in each epoch
        self.steps = 0 # counter
        self.step_in_vain = 0 # count how many continuous steps with no new races
        client = docker.from_env()
        containerId = "ef22199e51c69421943234a98110001fa6ac37a94521367b4621554b3846e0f9"
        self.container = client.containers.get(containerId)
        self.discovered_dataraces = set() # the full-picture of data races,  a set
        self.dataraces = set() # the full-picture of data races,  a set, only for each epoch
        
    def get_next_state(self, action):
        # this version, the action is to change a function on one position
        # the draw back: this method exploration range is too small: e.g.,
        tid = action // (self.sequence_len * self.max_action) # for here, 0 or 1
        action -= tid * self.sequence_len * self.max_action
        position = action // self.max_action
        function = action % self.max_action
        if tid == 0:
            self.queue1[position] = function
        else:
            self.queue2[position] = function
        state = (self.queue1 + self.queue2)
        return [item / self.max_action for item in state] # just put them to 0 ~ 1 range

    def step(self, action):
        # get the reward in this function
        self.steps += 1
        #self.queue2[action] = (self.queue2[action] + 1) % self.max_action # why only q2 is changed?
        #self.queue2[action] = ?
        #当前状态 归一化
        #state = (self.queue1 + self.queue2) 
        #state_ = [item/self.max_action for item in state]
        state_ = self.get_next_state(action)
        # get the reward for this case
        new_races = self.getReward_tasn() # this return is a key-value pair, key is the race id
        new_races = set(new_races.keys())
        reward = 0
        diff = new_races - self.dataraces
        if len(diff) > 0:
            reward = len(diff) # newly found races are the reward
            self.dataraces = self.dataraces.union(new_races) # update the discovered races
            self.step_in_vain = 0
        else:
            # no new races detected
            self.step_in_vain += 1
            #inverse_diff = self.dataraces - new_races
            if len(new_races) == 0:
                reward = -2 
            else:
                reward = 0
            

        # detemine if this should end 
        end = False
        if  self.step_in_vain == self.sequence_len * 2 * 3 or self.steps == self.max_step:
            end = True
            self.steps = 0
            self.step_in_vain = 0
            self.discovered_dataraces = self.discovered_dataraces.union(self.dataraces)

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
            if flag == 4:
                key += words[2]
                dataRace[key] = 1
                key = ''
                flag = 5
            elif flag == 3:
                if preFlag in words:
                    key += words[1]
                    #print(words[1])
                    flag = 4
            elif flag == 2:
                key += words[2]
                flag = 3
            elif flag == 1:
                key += words[0]
                #key += words[5]
                #print(words[0])
                flag = 2
            elif warnFlag in words:
                flag = 1

        return dataRace # this is a dict
      
    def reset(self) :
        self.queue1 = [random.randint(0,self.max_action - 1) for _ in range(self.sequence_len)]
        self.queue2 = [random.randint(0,self.max_action - 1) for _ in range(self.sequence_len)]
        self.steps = 0
        state = (self.queue1 + self.queue2)
        state_ = [item/self.max_action for item in state]
        self.dataraces = set()
        return state_
    """
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
        """



