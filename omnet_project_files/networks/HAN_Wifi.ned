import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.WirelessHost;
import inet.node.wireless.AccessPoint;
import inet.physicallayer.wireless.ieee80211.packetlevel.Ieee80211ScalarRadioMedium;
import inet.visualizer.contract.IIntegratedVisualizer;

network HAN_WifiNetwork
{
    parameters:
        **.mgmt.numChannels = 2;
        @display("bgb=100,100");
    submodules:
        visualizer: <default(firstAvailableOrEmpty("IntegratedCanvasVisualizer"))> like IIntegratedVisualizer if typename != "" {
            parameters:
                @display("p=10,10;is=s");
        }
        configurator: Ipv4NetworkConfigurator {
            parameters:
                @display("p=23.162306,6.733228;is=s");
                config = xml("<config><interface hosts='*' address='145.236.x.x' netmask='255.255.0.0'/></config>");
        }
        radioMedium: Ieee80211ScalarRadioMedium {
            parameters:
                @display("p=9.695848,21.277;is=s");
        }
        household_agent: WirelessHost {
            @display("p=81.06807,87.262634;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
        device_agent_0: WirelessHost {
            @display("p=57.097775,89.6866;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
        ap: AccessPoint {
            @display("p=50,50;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtApSimplified";
        }
        device_agent_1: WirelessHost {
            @display("p=20.469013,87.262634;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
        device_agent_2: WirelessHost {
            @display("p=41.207355,69.21758;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
        device_agent_3: WirelessHost {
            @display("p=83.76136,11.850482;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
        device_agent_4: WirelessHost {
            @display("p=39.322052,36.359432;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
        device_agent_5: WirelessHost {
            @display("p=14.813102,66.793625;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
        device_agent_6: WirelessHost {
            @display("p=70.56423,67.06295;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
        device_agent_7: WirelessHost {
            @display("p=75.14283,39.59138;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
        device_agent_8: WirelessHost {
            @display("p=20.469013,39.59138;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
        device_agent_9: WirelessHost {
            @display("p=46.59394,14.274444;r=,,#707070");
            wlan[*].mgmt.typename = "Ieee80211MgmtStaSimplified";
            wlan[*].agent.typename = "";
        }
}
