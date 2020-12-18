from enum import Enum
from collections import deque
from automic_counter import AtomicCounter

class Queue:
    #  队列类，用于管理与维护进程队列

    def __init__(self):
        self.deques = [deque([]) for _ in range(3)]
        # 3个优先级的就绪队列

    def get_ready_queue(self):
        ready_queue = Queue()
        return ready_queue

    def add_process(self, process):
        # 将进程加入到其对应优先级的就绪队列中
        priority = process.get_priority()
        the_deque = self.deques[priority]
        the_deque.append(process)

    def get_process(self):
        # 获得就绪队列里面优先级最高的进程，若对列为空返回None
        for i in range(2, 0, -1):
            the_deque = self.deques[i]
            if the_deque:
                return the_deque[0]
        return None

    def remove_process(self, process):
        # 删除就绪队列里面指定的进程
        priority = process.get_priority()
        deque = self.deques[priority]
        deque.remove(process)
        return

class PCB:
    # PCB（进程管理块）类，用于进程的管理

    ready_queue = Queue().get_ready_queue()
    # 生成就绪队列
    # 整个程序只能实例化一个ready_queue，就是PCB中的ready_queue，其他地方都使用pcb.ready_queue来访问，否则会有多个实例导致程序出错

    def __init__(self):
        self.exist_process = {} # 当前所有存活的进程，包括Running, Blocked, Ready
        self.current_process = None # 当前占用CPU的进程
        self.PID_generator = AtomicCounter() # 生成唯一的进程编号PID


    def get_PCB(self):
        pcb = PCB()
        return pcb

    def get_current_process(self):
        return self.current_process

    def set_current_process(self, current_process):
        self.current_process = current_process

    def generate_PID(self):
        return self.PID_generator.increment() # 自增方式避免重复

    def add_exist_list(self, process):
        # 每个进程一经创建，便会调用该方法，将其放在exist_list中
        self.exist_process[process.get_process_name()] = process
        return process

    def create_process(self, process_name, priority):
        # 创建新进程
        current_process = pcb.get_current_process()
        process = Process(pcb.generate_PID(), process_name, priority, 'new', {}, current_process, [])
        if current_process: # 排除创建的进程为第一个进程的特殊情况
            current_process.get_children().append(process) # 新创建进程作为当前进程的子进程
            process.set_parent(current_process) # 旧进程作为新创建进程的父进程
            pcb.add_exist_list(process)
            self.ready_queue.add_process(process)
        else: # 系统初始化时没有current_process，需要设置
            self.current_process = process
            pcb.add_exist_list(process)

        # 将以下两行代码放到上面的if-else结构中，因为系统初始化时init进程无需放到ready_queue里，
        # 直接通过scheduler调度进入running态。否则会导致ready_queue的deques[0]里有两个init进程。
        # pcb.add_exist_list(process)
        # self.ready_queue.add_process(process)

        process.set_state('ready')
        pcb.scheduler()
        return process

    def exist_name(self, name):
        return name in self.exist_process

    def find_process(self, process_name):
        for entry in self.exist_process.keys():
            if entry == process_name:
                return self.exist_process[entry]
        return None

    def scheduler(self):
        # 进程调度
        current_process = pcb.get_current_process()
        ready_process = self.ready_queue.get_process()
        if ready_process == None:
            # 就绪队列为空时，CPU正在运行的只有init进程
            pcb.get_current_process().set_state('running')
            return
        elif current_process == None:
            # 此处只有在刚初始化系统时才可能发生
            self.ready_queue.remove_process(ready_process)
            pcb.set_current_process(ready_process)
            ready_process.set_state('running')
        elif (current_process.get_state() == 'blocked') | (current_process.get_state() == 'terminated'):
            # 当前进程被阻塞或者已被终止
            # 从就绪队列取出一个就绪进程并设置为运行态
            self.ready_queue.remove_process(ready_process)
            pcb.set_current_process(ready_process)
            ready_process.set_state('running')
        elif current_process.get_state() == 'running':
            # 对应的是新创建了进程或者阻塞队列中的进程转移到ready_list的状态
            if current_process.get_priority() < ready_process.get_priority():
                # 若就绪进程优先级更高，则抢占
                self.preempt(ready_process, current_process)
        elif current_process.get_state() == 'ready':
            # 对应的是时间片完的情况
            if current_process.get_priority() <= ready_process.get_priority():
                # 若有进程的优先级大于等于当前的就绪进程，则抢占
                self.preempt(ready_process, current_process)
            else:
                # 若没有高优先级的就绪进程，则当前进程继续运行
                current_process.set_state('running')
        return

    def preempt(self, ready_process, current_process):
        #进程抢占（切换）
        if self.exist_name(current_process.get_process_name()):
            self.ready_queue.add_process(current_process)
            current_process.set_state('ready')
            self.ready_queue.remove_process(ready_process)
            pcb.set_current_process(ready_process)
            ready_process.set_state('running')
            return

    def timeout(self):
        # 时间片完后切换进程
        pcb.get_current_process().set_state('ready')
        self.scheduler()

    def kill_process(self, process):
        # 从exist_process队列中删除进程
        name = process.get_process_name()
        self.exist_process.pop(name)

class Process:
    # 进程类，用于进程的定义和进程状态的管理

    state = Enum('state', ('new', 'ready', 'running', 'blocked', 'terminated'))
    pcb = PCB().get_PCB()
    # ready_queue = Queue().get_ready_queue() # 不能重新实例化ready_queue，应直接用pcb.ready_queue访问
    ready_queue = pcb.ready_queue
    block_resource = [] # 若进程状态为阻塞，该属性指向被阻塞的资源，否则为空

    def __init__(self, PID, process_name, priority, state, resource_map: dict, parent_process, children_process):
        self.PID = PID
        self.process_name = process_name
        self.priority = priority
        self.state = state
        self.resource_map = resource_map # 进程拥有的资源和对应的数量
        self.parent_process = parent_process
        self.children_process = children_process

    def get_PID(self):
        return self.PID

    def get_process_name(self):
        return self.process_name

    def get_priority(self):
        return self.priority

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def set_parent(self, parent_process):
        self.parent_process = parent_process

    def get_children(self):
        return self.children_process

    def get_block_resource(self):
        return self.block_resource

    def get_resource_map(self):
        return self.resource_map

    def set_block_resource(self, block_resource):
        self.block_resource = block_resource

    def destroy_process(self):
        # 删除进程时调用
        self.kill_sub_tree()
        pcb.scheduler()

    def remove_child(self, parent):
        # 删除子进程
        for child in parent.children_process:
            if child == self:
                parent.children_process.remove(child)

    def kill_sub_tree(self):
        # 删除进程及以其为根的进程树
        if self.children_process: # 当前进程子树不为空
            child_count = len(self.children_process)
            for i in range(child_count):
                child = self.children_process[0]
                child.kill_sub_tree() # 递归删除子树

        if self.get_state() == 'terminated':
            # 进程为终止态，删除成功
            pcb.kill_process(self)
        elif self.get_state() == 'ready':
            # 进程为就绪态，从就绪队列删除，修改其状态为终止态
            self.ready_queue.remove_process(self)
            pcb.kill_process(self)
            self.set_state('terminated')
        elif self.get_state() == 'blocked':
            # 进程为阻塞态，从阻塞队列删除，修改其状态为终止态
            block_resource = self.get_block_resource()
            block_resource.remove_block_process(self)
            pcb.kill_process(self)
            self.set_state('terminated')
        elif self.get_state() == 'running':
            # 进程为运行态，直接终止，修改其状态为终止态
            pcb.kill_process(self)
            self.set_state('terminated')
        # 清除父进程的子进程列表中的对应进程
        parent = self.parent_process
        self.remove_child(parent)
        self.parent_process = []
        # 释放资源
        duplicate_resource_map = self.resource_map.copy() # prevent: RuntimeError: dictionary changed size during iteration
        for resource in duplicate_resource_map:
            resource.release_all(self)
        return

    def print_process_info(self):
        # 打印进程信息
        print()
        print('...process info...')
        print('process id: ' + str(self.PID))
        print('process name: ' + self.process_name)
        print('process priority: ' + str(self.priority))
        print('process state: ' + self.state)
        # 获取父进程名称并打印
        parent_process_name = self.parent_process.process_name
        print('parent process: ' + parent_process_name)
        # 获取子进程树并打印
        children_process_name_list = []
        for child in self.children_process:
            children_process_name_list.append(child.process_name)
        print('children process: ' + str(children_process_name_list))
        # 获取资源占用并打印占用的资源名称和数量
        process_resource_name_list = list(self.resource_map.keys())
        process_resource_count_list = list(self.resource_map.values())
        process_resource_info = {}
        for i in range(len(self.resource_map)):
            resource_name = 'R' + str(process_resource_name_list[i].RID)
            resource_count = process_resource_count_list[i]
            process_resource_info[resource_name] = resource_count
        print('process resource: ' + str(process_resource_info))
        print('...process info ends...')
        print()
        return

class Resource:
    # 资源类，用于资源的定义与资源管理

    pcb = PCB().get_PCB()
    # ready_queue = Queue().get_ready_queue()
    ready_queue = pcb.ready_queue

    class BlockProcess:
        # 阻塞进程
        def __init__(self, process, need):
            self.process = process
            self.need = need # 需要请求的资源数量

        def get_process(self):
            return self.process

        def get_need(self):
            return self.need

    def __init__(self, RID, max):
        self.RID = RID
        self.max = max
        self.remaining = max
        self.block_deque = deque([])

    def get_RID(self):
        return self.RID

    def add_remaining(self, num):
        self.remaining += num

    def remove_block_process(self, process):
        # 在阻塞队列中直接删除指定进程，在终止进程时调用
        for blocked_process in self.block_deque:
            if blocked_process.get_process() == process:
                self.block_deque.remove(blocked_process)
                return True
        return False

    def request(self, process, need):
        # 进程请求资源
        if need > self.max:
            print('请求资源失败！请求资源大于最大数量！')
            return
        elif (need > self.remaining) & (process.get_process_name() != 'init'):
            # 对于非init进程，需要阻塞
            self.block_deque.append(self.BlockProcess(process, need))
            process.set_state('blocked')
            process.set_block_resource(self)
            pcb.scheduler()
            return
        elif (need > self.remaining) & (process.get_process_name() == 'init'):
            # init进程不阻塞
            return
        else:
            # 正常分配资源
            self.remaining = self.remaining - need
            resource_map = process.get_resource_map()
            if self in resource_map:
                already_allocated_num = resource_map.get(self)
                resource_map[self] = already_allocated_num + need
            else:
                resource_map[self] = need

    def release_all(self, process):
        # 释放当前持有的所有资源
        # 进程释放资源并唤醒阻塞进程
        num = process.get_resource_map().pop(self)
        if num == 0:
            return
        self.remaining = self.remaining + num
        while self.block_deque:
            block_process = self.block_deque[0]
            need = block_process.get_need()
            if self.remaining >= need:
                ready_process = block_process.get_process()
                self.request(ready_process, need)
                self.block_deque.popleft()
                self.ready_queue.add_process(ready_process)
                ready_process.set_state('ready')
                ready_process.set_block_resource([])
                if ready_process.get_priority() > pcb.get_current_process().get_priority():
                    pcb.preempt(ready_process, pcb.get_current_process())
                # else:
                #     break
            else:
                break

    def release(self, process, num):
        # 释放指定数量的资源
        # 进程释放资源并唤醒阻塞进程
        if num == 0:
            return
        self.remaining = self.remaining + num
        while self.block_deque:
            block_process = self.block_deque[0]
            need = block_process.get_need()
            if self.remaining >= need: # 大于等于 不是大于
                ready_process = block_process.get_process()
                self.request(ready_process, need)
                self.block_deque.popleft()
                self.ready_queue.add_process(ready_process)
                ready_process.set_state('ready')
                ready_process.set_block_resource([])
                if ready_process.get_priority() > pcb.get_current_process().get_priority():
                    pcb.preempt(ready_process, pcb.get_current_process())
                # else:
                #     break
            else:
                break
        return

    def print_current_status(self):
        # 打印当前资源信息
        string = 'res-'
        string += str(self.RID)
        string += '{max='
        string += str(self.max)
        string += ',remaining:'
        string += str(self.remaining)
        string += '}'
        print(string)

    def print_block_deque(self):
        # 打印资源阻塞队列信息
        string = 'res-'
        string += str(self.RID)
        string += ' block_deque '
        for blocked_process in self.block_deque:
            string += '{'
            string += blocked_process.get_process().get_process_name()
            string += ':'
            string += str(blocked_process.get_need())
            string += '}'
        print(string)

def load_file(filename):
    # 加载文件并读取命令
    file = open(filename, 'r')
    commands = file.readlines()
    for line in commands:
        commands[commands.index(line)] = line.strip()
    return commands

def exec_commands(cmds):
    # 根据命令调度相应的内核函数完成操作，并输出相应信息

    if cmds[0] == 'cr': # 创建进程
        if not len(cmds) == 3:
            print('错误！输入命令格式不合法！')
            return -1
        else:
            process_name = cmds[1]
            try:
                priority = int(cmds[2])
                if priority <= 0 | priority > 2:
                    print('错误！输入参数不合法！')
                    return -1
            except:
                print('错误！输入参数不合法！')
                return -1
            if pcb.exist_name(process_name):
                print('错误！进程名' + process_name + '已经存在，请选择其他的进程名！')
                return -1
            pcb.create_process(process_name, priority)

    elif cmds[0] == 'de': # 删除进程
        if not len(cmds) == 2:
            print('错误！输入命令格式不合法！')
            return -1
        else:
            process_name = cmds[1]
            process = pcb.find_process(process_name)
            if process == None:
                print('错误！没有名为' + process_name + '的进程！')
                return -1
            elif process_name == 'init':
                print('错误！没有权限中止init进程！')
                return -1
            else:
                process.destroy_process()

    elif cmds[0] == 'req': # 进程请求资源
        if not len(cmds) == 3:
            print('错误！输入命令格式不合法！')
            return -1
        else:
            resource_name = cmds[1]
            try:
                need_num = int(cmds[2])
            except:
                print('错误！输入参数不合法！')
                return -1
            current_process = pcb.get_current_process()
            if resource_name == 'R1':
                R1.request(current_process, need_num)
            elif resource_name == 'R2':
                R2.request(current_process, need_num)
            elif resource_name == 'R3':
                R3.request(current_process, need_num)
            elif resource_name == 'R4':
                R4.request(current_process, need_num)
            else:
                print('错误！输入参数不合法！')
                return -1

    elif cmds[0] == 'rel': # 进程释放资源
        if not len(cmds) == 3:
            print('错误！输入命令格式不合法！')
            return -1
        else:
            resource_name = cmds[1]
            try:
                rel_num = int(cmds[2])
            except:
                print('错误！输入参数不合法！')
                return -1
            current_process = pcb.get_current_process()
            if resource_name == 'R1':
                R1.release(current_process, rel_num)
            elif resource_name == 'R2':
                R2.release(current_process, rel_num)
            elif resource_name == 'R3':
                R3.release(current_process, rel_num)
            elif resource_name == 'R4':
                R4.release(current_process, rel_num)
            else:
                print('错误！输入参数不合法！')
                return -1

    elif cmds[0] == 'to': # 时钟中断
        pcb.timeout()

    elif (cmds[0] == 'list') & (cmds[1] == 'ready'): # 打印ready队列中的进程
        print()
        print('...ready list...')
        queue = pcb.ready_queue
        for priority in range(3):
            print(str(priority) + ':', end=' ')
            for process in queue.deques[priority]:
                process_name = process.get_process_name()
                print(' ' + process_name, end=' ')
            print()
        print('...ready list ends...')
        print()
        return 0

    elif (cmds[0] == 'list') & (cmds[1] == 'block'): # 打印阻塞队列
        print()
        print('...block list...')
        R1.print_block_deque()
        R2.print_block_deque()
        R3.print_block_deque()
        R4.print_block_deque()
        print('...block list ends...')
        print()
        return 0

    elif (cmds[0] == 'list') & (cmds[1] == 'res'): # 打印资源状态
        print()
        print('...resource list...')
        R1.print_current_status()
        R2.print_current_status()
        R3.print_current_status()
        R4.print_current_status()
        print('...resource list ends...')
        print()
        return 0

    elif (cmds[0] == 'pr'): # 打印进程信息
        if not len(cmds) == 2:
            print('错误！输入命令格式不合法！')
            return -1
        else:
            process_name = cmds[1]
            process = pcb.find_process(process_name)
            if process == None:
                print('错误！没有名为' + process_name + '的进程！')
                return -1
            else:
                process.print_process_info()
                return 0

    else:
        print('错误！请输入合法的命令！')
        return -1

    if not pcb.get_current_process() == None:
        # 打印现在正在运行的进程
        print('running: ' + pcb.get_current_process().get_process_name())
        return 0

if __name__ == '__main__':
    # 创建PCB与资源，定义资源数量
    pcb = PCB()
    R1 = Resource(1, 1)
    R2 = Resource(2, 2)
    R3 = Resource(3, 3)
    R4 = Resource(4, 4)

    # 创建init进程，系统初始化
    pcb.create_process('init', 0)
    print('init' + ' ')

    # 从文件读取数据
    filename = '0.txt'
    commands = load_file(filename)

    # 逐条执行文件中的命令
    for command in commands:
        cmds = command.split(' ')
        exec_commands(cmds)

