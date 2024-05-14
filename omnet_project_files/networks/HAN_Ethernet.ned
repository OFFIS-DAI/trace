import inet.node.ethernet.Eth10G;
import inet.node.ethernet.Eth1G;
import inet.node.ethernet.Eth100M;
import inet.node.ethernet.Eth10M;
import inet.node.inet.Router;
import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.StandardHost;


//
// Ethernet home area network
//
network HAN_EthernetNetwork_10Mbps
{
    parameters:
        @display("bgb=100,100");
    submodules:
        configurator: Ipv4NetworkConfigurator {
            parameters:
                @display("p=100,100;is=s");
        }
        router: Router {
            @display("p=47.146667,30.506666");
        }
        household_agent: StandardHost {
            @display("p=71.066666,83.2");
        }
        device_agent_0: StandardHost {
            @display("p=33.626667,63.093334");
        }
        device_agent_1: StandardHost {
            @display("p=81.12,66.90667");
        }
        device_agent_2: StandardHost {
            @display("p=11.093333,63.093334");
        }
        device_agent_3: StandardHost {
            @display("p=11.093333,88.4");
        }
        device_agent_4: StandardHost {
            @display("p=38.13333,85.28");
        }
        device_agent_5: StandardHost {
            @display("p=67.6,13.5199995");
        }
        device_agent_6: StandardHost {
            @display("p=33.626667,15.599999");
        }
        device_agent_7: StandardHost {
            @display("p=20.106667,37.786667");
        }
        device_agent_8: StandardHost {
            @display("p=73.49333,38.13333");
        }
        device_agent_9: StandardHost {
            @display("p=91.86667,29.119999");
        }
    connections:
        router.ethg++ <--> Eth10M <--> household_agent.ethg++;
        router.ethg++ <--> Eth10M <--> device_agent_0.ethg++;
        router.ethg++ <--> Eth10M <--> device_agent_1.ethg++;
        router.ethg++ <--> Eth10M <--> device_agent_2.ethg++;
        router.ethg++ <--> Eth10M <--> device_agent_3.ethg++;
        router.ethg++ <--> Eth10M <--> device_agent_4.ethg++;
        router.ethg++ <--> Eth10M <--> device_agent_5.ethg++;
        router.ethg++ <--> Eth10M <--> device_agent_6.ethg++;
        router.ethg++ <--> Eth10M <--> device_agent_7.ethg++;
        router.ethg++ <--> Eth10M <--> device_agent_8.ethg++;
        router.ethg++ <--> Eth10M <--> device_agent_9.ethg++;

}

//
// Ethernet network
//
network HAN_EthernetNetwork_100Mbps
{
    parameters:
        @display("bgb=100,100");
    submodules:
        configurator: Ipv4NetworkConfigurator {
            parameters:
                @display("p=100,100;is=s");
        }
        router: Router {
            @display("p=47.146667,30.506666");
        }
        household_agent: StandardHost {
            @display("p=71.066666,83.2");
        }
        device_agent_0: StandardHost {
            @display("p=33.626667,63.093334");
        }
        device_agent_1: StandardHost {
            @display("p=81.12,66.90667");
        }
        device_agent_2: StandardHost {
            @display("p=11.093333,63.093334");
        }
        device_agent_3: StandardHost {
            @display("p=11.093333,88.4");
        }
        device_agent_4: StandardHost {
            @display("p=38.13333,85.28");
        }
        device_agent_5: StandardHost {
            @display("p=67.6,13.5199995");
        }
        device_agent_6: StandardHost {
            @display("p=33.626667,15.599999");
        }
        device_agent_7: StandardHost {
            @display("p=20.106667,37.786667");
        }
        device_agent_8: StandardHost {
            @display("p=73.49333,38.13333");
        }
        device_agent_9: StandardHost {
            @display("p=91.86667,29.119999");
        }
    connections:
        router.ethg++ <--> Eth100M <--> household_agent.ethg++;
        router.ethg++ <--> Eth100M <--> device_agent_0.ethg++;
        router.ethg++ <--> Eth100M <--> device_agent_1.ethg++;
        router.ethg++ <--> Eth100M <--> device_agent_2.ethg++;
        router.ethg++ <--> Eth100M <--> device_agent_3.ethg++;
        router.ethg++ <--> Eth100M <--> device_agent_4.ethg++;
        router.ethg++ <--> Eth100M <--> device_agent_5.ethg++;
        router.ethg++ <--> Eth100M <--> device_agent_6.ethg++;
        router.ethg++ <--> Eth100M <--> device_agent_7.ethg++;
        router.ethg++ <--> Eth100M <--> device_agent_8.ethg++;
        router.ethg++ <--> Eth100M <--> device_agent_9.ethg++;

}

//
// Ethernet network
//
network HAN_EthernetNetwork_1000Mbps
{
    parameters:
        @display("bgb=100,100");
    submodules:
        configurator: Ipv4NetworkConfigurator {
            parameters:
                @display("p=100,100;is=s");
        }
        router: Router {
            @display("p=47.146667,30.506666");
        }
        household_agent: StandardHost {
            @display("p=71.066666,83.2");
        }
        device_agent_0: StandardHost {
            @display("p=33.626667,63.093334");
        }
        device_agent_1: StandardHost {
            @display("p=81.12,66.90667");
        }
        device_agent_2: StandardHost {
            @display("p=11.093333,63.093334");
        }
        device_agent_3: StandardHost {
            @display("p=11.093333,88.4");
        }
        device_agent_4: StandardHost {
            @display("p=38.13333,85.28");
        }
        device_agent_5: StandardHost {
            @display("p=67.6,13.5199995");
        }
        device_agent_6: StandardHost {
            @display("p=33.626667,15.599999");
        }
        device_agent_7: StandardHost {
            @display("p=20.106667,37.786667");
        }
        device_agent_8: StandardHost {
            @display("p=73.49333,38.13333");
        }
        device_agent_9: StandardHost {
            @display("p=91.86667,29.119999");
        }
    connections:
        router.ethg++ <--> Eth1G <--> household_agent.ethg++;
        router.ethg++ <--> Eth1G <--> device_agent_0.ethg++;
        router.ethg++ <--> Eth1G <--> device_agent_1.ethg++;
        router.ethg++ <--> Eth1G <--> device_agent_2.ethg++;
        router.ethg++ <--> Eth1G <--> device_agent_3.ethg++;
        router.ethg++ <--> Eth1G <--> device_agent_4.ethg++;
        router.ethg++ <--> Eth1G <--> device_agent_5.ethg++;
        router.ethg++ <--> Eth1G <--> device_agent_6.ethg++;
        router.ethg++ <--> Eth1G <--> device_agent_7.ethg++;
        router.ethg++ <--> Eth1G <--> device_agent_8.ethg++;
        router.ethg++ <--> Eth1G <--> device_agent_9.ethg++;

}

//
// Ethernet network
//
network HAN_EthernetNetwork_10000Mbps
{
    parameters:
        @display("bgb=100,100");
    submodules:
        configurator: Ipv4NetworkConfigurator {
            parameters:
                @display("p=100,100;is=s");
        }
        router: Router {
            @display("p=47.146667,30.506666");
        }
        household_agent: StandardHost {
            @display("p=71.066666,83.2");
        }
        device_agent_0: StandardHost {
            @display("p=33.626667,63.093334");
        }
        device_agent_1: StandardHost {
            @display("p=81.12,66.90667");
        }
        device_agent_2: StandardHost {
            @display("p=11.093333,63.093334");
        }
        device_agent_3: StandardHost {
            @display("p=11.093333,88.4");
        }
        device_agent_4: StandardHost {
            @display("p=38.13333,85.28");
        }
        device_agent_5: StandardHost {
            @display("p=67.6,13.5199995");
        }
        device_agent_6: StandardHost {
            @display("p=33.626667,15.599999");
        }
        device_agent_7: StandardHost {
            @display("p=20.106667,37.786667");
        }
        device_agent_8: StandardHost {
            @display("p=73.49333,38.13333");
        }
        device_agent_9: StandardHost {
            @display("p=91.86667,29.119999");
        }
    connections:
        router.ethg++ <--> Eth10G <--> household_agent.ethg++;
        router.ethg++ <--> Eth10G <--> device_agent_0.ethg++;
        router.ethg++ <--> Eth10G <--> device_agent_1.ethg++;
        router.ethg++ <--> Eth10G <--> device_agent_2.ethg++;
        router.ethg++ <--> Eth10G <--> device_agent_3.ethg++;
        router.ethg++ <--> Eth10G <--> device_agent_4.ethg++;
        router.ethg++ <--> Eth10G <--> device_agent_5.ethg++;
        router.ethg++ <--> Eth10G <--> device_agent_6.ethg++;
        router.ethg++ <--> Eth10G <--> device_agent_7.ethg++;
        router.ethg++ <--> Eth10G <--> device_agent_8.ethg++;
        router.ethg++ <--> Eth10G <--> device_agent_9.ethg++;

}