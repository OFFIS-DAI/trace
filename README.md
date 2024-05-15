# trace: TRAining data generation tool for combined Communication and Energy system scenarios

## Introduction
The project trace is designed to enhance the integration and analysis of energy and communication systems through a 
well-defined modeling approach. 
As energy and communication systems become increasingly intertwined, understanding their interactions and the potential 
applications becomes crucial. 
This tool uses a classification of communication behaviors within energy systems based on parameters such as 
packet sizes and frequencies. 

## Project Structure
- **agent_communication_generation_tool**: Contains Python files to define and simulate communication behavior and message flows for both simple and complex use cases.
- **network_generation**: Includes scripts to transform Simbench power networks into communication networks suitable for simulation.
- **omnet_project_files**: This directory holds the project files needed to import into the network simulator OMNeT++ for simulating the communication technologies.

## Installation Requirements
- **OMNeT++ Setup**: 
  - OMNeT++ version 6 is required.
  - The project requires inet4.5 and simu5G version 1.2.2.
  - Ensure that all project files are located at the same directory level within your local setup (under the project folder "trace").
  
- **Python Environment**:
  - Python 3.9 is necessary for running the scripts.
  - Dependencies can be installed using the provided `requirements.txt` file.

## Setup Instructions
1. **Clone the Repository**:
   ```
   git clone [repository-url]
   cd trace
   ```

2. **Install Python Dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Setting up OMNeT++**:
   - Install OMNeT++ 6 and ensure inet4.5 and simu5G 1.2.2 are configured properly.
   - Import the project files from the `omnet_project_files` directory into OMNeT++.
   - Change the INET path in the file [communication_scenario_description.py](agent_communication_generation_tool/description_classes/communication_scenario_description.py) to your local installation path.

## Usage
You can run either all simple/complex use cases by executing 
[run_complex.sh](agent_communication_generation_tool/run_complex.sh) or  
[run_simple.sh](agent_communication_generation_tool/run_simple.sh) or you can also execute single scenarios from the 
corresponding folders.

## Additional information
Additional information is provided as a uml class diagramm and sequence diagrams on the agent-based applications in [docs](docs). 

## Support
For any questions or suggestions contact malin.radtke@offis.de.

## License
Distributed under the MIT license.
