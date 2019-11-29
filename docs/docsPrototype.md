# Documentation

## Glossary
- Agent - single application instance, is able to compute one subproblem (task) at a time
- Computational problem - problem solvable with Codeine. It should be divisible into a finite amount of subproblems (tasks) which can be solved independent of each other
- Computational network (usually referred to as "network") - a network of agents communicating with each other, who together solve one computational problem
- Task - a single subproblem of the computational problem

## Requirements
- Project should implement peer-to-peer networking on LAN
- We should assume that about 5 agents at once can work on our computational problem
- Every agent should have exactly the same application
- After application launch, agent should automatically connect with all other agents in the network
- The computational problem itself doesn't matter, it should only allow for long enough computing time to let us see the network working as intended (officially 1 hour on 5 agents, non-officially 10 - 20 mins)
- Task assignment should be decentralized
- Agents should be immune to other agents disconnecting from the network, there should be no side effects
- Results should be visualized, accessible (in the best case in real time)

## Assumptions & Constraints
- Packet type - a seven letter long word consisting only of upper case letters (e.g. IMALIVE, NETTOPO)
- The solution of a single task should be able to fit in a single UDP packet (<64kB)
- Every task has it's **ID** and immutable **State**, common for all tasks
- Every task can be solved

## Packets

* Topology discovery, registering agents, agent check
    * `IMALIVE` - i am alive. `<>`
    * `NETTOPO` - send network topology. `<agent[]>`
* Task assignment
    * `REGTASK` - register new task. `<task_id>`  
    * `CARRYON` - carry on with that task. `<task_id>`
    * `STOPWIP` - don't start: this task is work-in-progress. `<task_id>`
    * `STOPLOW` - don't start: lower priority. `<task_id>`
* Result distribution
    * `TASKRES` - send task result. `<task_id, task_result>`
* Confirmation
    * `ACKNOWL` - acknowledge. `<previous_package_control_sum>`
 
### Rules (~broadcast)
* `~IMALIVE` -> `NETTOPO` (optional)
* `~REGTASK` -> `CARRYON` | `STOPWIP` | `STOPLOW` | `TASKRES`
* `~TASKRES` -> `ACKNOWL` ?


## Network scenarios

### Possible errors:
- Agent receives 2 TASKRES packets with the same task ID, yet different results (Scenario 5).
- Agent can't register any task because they are all WIP on other agents.


### Scenario 1 
Story:  

>Agent tries to join the network right after launching Codeine.

Prerequisites: None

Scenario 1:
1. Agent broadcasts IMALIVE packet.
2. Agent waits for ??? seconds for replies from every other agent already in the network.
3. Every other agent already in the network replies with NETTOPO packet.
4. Agent registers the network. End of Scenario 1.

Scenario extensions:  
3a. There is no response from the network (proceed to calculations). End of Scenario 1.

### Scenario 2

Story:

>Agent periodically informs the network that he's still alive.


Prerequisites:
- Agent is already in the network.

Scenario:  
1. Agent broadcasts IMALIVE packet. End of Scenario 2.

### Scenario 3

Story:

>Agent wants to register a task

Prerequisites:
- Agent is already in the network

Scenario:
1. Agent broadcasts REGTASK packet.
2. Agent waits for ??? seconds for replies.
3. Every other agent registered in his net topology base replies with CARRYON.
4. Agent starts calculations on that task. End of Scenario 3.

Scenario extensions:  
3a. There is no response from the network.  
3a.1. Agent starts calculations on that task. End of Scenario 3.  

3b. An agent replies with STOPWIP.
3b.1. Agent sets that task's state to WIP.
3b.2. Agent chooses another task. Repeat from point 1. End of Scenario 3.  

3c. An agent replies with STOPLOW.  
3c.1. Agent chooses another task. Repeat from point 1. End of Scenario 3.  

3d. An agent replies with TASKRES.  
3d.1. Agent registers received task result.  
3d.2. Agent chooses another task. Repeat from point 1. End of Scenario 3.

### Scenario 4

Story:

>Agent wants to broadcast task results.

Prerequisites:
- Agent is already in the network
- Agent has calculated a task and received a concrete result

Scenario:
1. Agent broadcast TASKRES packet.
2. Agent waits for ??? seconds for replies.
3. Every other agent registered in his net topology base replies with ACKNOWL. End of Scenario 4.

Scenario extensions:  
3a. If any agent hasn't replied with ACKNOWL, send packet TASKRES again to him. Repeat ??? times.  
3a.1. An agent hasn't replied after ??? sent TASKRES packets. Remove him from net topology base.

### Scenario 5

Story:

>Agent has received a TASKRES packet with task ID of a task he already has a result of.

Prerequisites:
- Agent is already in the network
- Agent already has results of at least one task

Scenario:
1. Agent received a TASKRES packet.
2. Agent tries to register the task result. Task with that ID already has a registered result.
3. Task result of received packet is ignored. 
4. Reply with ACKNOWL packet. End of Scenario 5.

### Scenario 6

Story:

>Agent A tries to register a task with ID == X. Agent B replies with STOPWIP packet. Agent A sets task X's state to WIP. Agent B then disconnects.

Prerequisites:
- Agent is already in the network

Scenario:
1. Agent A broadcasts REGTASK packet with task ID == X.
2. Agent B replies with STOPWIP.
3. Agent A sets task X's state to WIP.
4. Agent B disconnects.
5. Agent A doesn't receive IMALIVE packets from agent B for ??? minutes.
6. Agent A sets task X's state to unregistered/free/not-yet-completed. End of Scenario 6.

### My thoughts:
- Can STOPLOW/STOPWIP be changed to just STOPTSK? They both inform you that you should not calculate a task because it either is or will very, very soon be WIP. Do we really need a reason to know why?
