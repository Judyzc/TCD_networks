# TCD_networks

## How to Use
To test the simulation, simply run ```python lunar.py``` in one terminal and ```python earth.py``` in another. Text input/commands can sent from Earth: "FORWARD", "BACK", "LEFT", "RIGHT", "STOP".

To test accross multiple machines, edit ```env_variables.py``` and appropriately change ```LUNAR_IP```, ```EARTH_IP```.

The lunar instance runs a P2P data trade discovery, as well as a P2P data trade receiver, and will simulate trading with itself. You can also run an instance of ```lunar_friend.py``` (which is a P2P trade receiver) in a 3rd terminal and change ```LUNAR_IP_RANGE``` (if running on separate machine) to allow that node to be discovered and traded with.

To test channel simulation properties, you can change the parameters of delays/errors by editing ```MOON_TO_EARTH_LATENCY```, ```LATENCY_JITTER_FACTOR```, ```PACKET_LOSS_PROBABILITY```, ```PACKET_LOSS_FACTOR```, ```BER``` in ```env_variables.py```.

Messages in all of the terminals will demonstrate the bahaviour of the network.


## Rough Version History 
1/3/2025: Version 1.1
- super rough, check out packets.py. Run with ```python packets.py``` or ```python3 packets.py```. currently, packet building, sending, and environment simulation all in there. will move out into separate files later. a lot of code is built with help from genAI, so mostly its just for reference/outlining the concept
- ```utils.py``` is for various utility functions, currently using the @timefunc wrapper to just keep track of function timing 
- the ./randompractice folder is just for more reference code and isn't used by our actual ```packets.py``` file.

27/3/2025: Version 1.2
- moved functions into separate files 

27/3/2025: Version 1.3
- changed code from using UDP to TCP 

27/3/2025: Version 1.4 
- tested running ```earth.py``` and ```lunar.py``` on different laptops 
- moving constants into ```env_variables.py```
- next to-do: security (bonus), create a rover object (status, direction, movement), UDP for video?, probably can't get parsing of data from others but could get scanning for connection

29/3/2025: Version 2.1
- Added lunar rover sending temperature and system status data 

29/3/2025: Version 2.2 
- To-do: 
    * Add control processes from Earth
    * Move processes (temp, status) into different ports
    * Add general scanning for connections -> 4th communication type? 
    * Email advisor (w/ updates and any questions)

31/3/2025: Version ? 
- scanning 
- movement (broken into 2 ports) 
