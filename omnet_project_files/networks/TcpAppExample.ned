//
// Copyright (C) 2000 Institut fuer Telematik, Universitaet Karlsruhe
//
// SPDX-License-Identifier: LGPL-3.0-or-later
//
//

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.StandardHost;
import ned.DatarateChannel;
import inet.node.inet.Router;

network TcpAppExample
{
    types:
        channel C extends DatarateChannel
        {
            datarate = 10Mbps;
            delay = 1ms;
        }
    submodules:
        configurator: Ipv4NetworkConfigurator {
            parameters:
                @display("p=100,100;is=s");
        }
        client0: StandardHost {
            parameters:
                @display("p=200,138;i=device/pc3");
        }
        client1: StandardHost {
            parameters:
                @display("p=143,273;i=device/pc2");
        }
        client2: StandardHost {
            parameters:
                @display("p=92,259;i=device/pc2");
        }
        client3: StandardHost {
            parameters:
                @display("p=247,312;i=device/pc2");
        }
        client4: StandardHost {
            parameters:
                @display("p=200,363;i=device/pc2");
        }
        client5: StandardHost {
            parameters:
                @display("p=143,351;i=device/pc2");
        }
        client6: StandardHost {
            parameters:
                @display("p=92,312;i=device/pc2");
        }
        client7: StandardHost {
            parameters:
                @display("p=38,305;i=device/pc2");
        }
        client8: StandardHost {
            parameters:
                @display("p=389,305;i=device/pc2");
        }
        client9: StandardHost {
            parameters:
                @display("p=308,305;i=device/pc2");
        }
        router: Router {
            @display("p=292,139");
        }
    connections:
        
        client0.ethg++ <--> C <--> router.ethg++;
        router.ethg++ <--> C <--> client1.ethg++;
        router.ethg++ <--> C <--> client2.ethg++;
        router.ethg++ <--> C <--> client3.ethg++;
        router.ethg++ <--> C <--> client4.ethg++;
        router.ethg++ <--> C <--> client5.ethg++;
        router.ethg++ <--> C <--> client6.ethg++;
        router.ethg++ <--> C <--> client7.ethg++;
        router.ethg++ <--> C <--> client8.ethg++;
        router.ethg++ <--> C <--> client9.ethg++;
}

