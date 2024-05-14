import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.networklayer.ipv4.RoutingTableRecorder;
import inet.node.ethernet.Eth10G;
import inet.node.ethernet.Eth10M;
import inet.node.inet.Router;
import inet.node.inet.StandardHost;
import simu5g.common.binder.Binder;
import simu5g.common.carrierAggregation.CarrierAggregation;
import simu5g.nodes.Ue;
import simu5g.nodes.eNodeB;
import simu5g.nodes.PgwStandard;
import simu5g.world.radio.LteChannelControl;


network WAN_LTE
{
    parameters:
        int numUe = default(1);
        @display("i=block/network2;bgb=991,558;bgi=background/budapest");
    submodules:
        channelControl: LteChannelControl {
                @display("p=50,25");
        }
        routingRecorder: RoutingTableRecorder {
                @display("p=50,75");
        }
        configurator: Ipv4NetworkConfigurator {
                @display("p=50,125");
        }
        binder: Binder {
                @display("p=50,175");
        }
        carrierAggregation: CarrierAggregation {
                @display("p=50.993748,258.7");
        }
        server: StandardHost {
                @display("p=212,118");
        }
        router: Router {
                @display("p=321,136");
        }
        pgw: PgwStandard {            
                @display("p=519,175");
        }
        eNB: eNodeB {
                @display("p=391,259");
        }
        household_agent_0: Ue {
                @display("p=737,404");
        }
        household_agent_1: Ue {
                @display("p=0,0");
        }
        control_center_agent: Ue {
                @display("p=100,100");
        }
        market_agent: Ue {
                @display("p=357,308");
        }
        aggregator_agent: Ue {
                @display("p=100,100");
        }
        pdc_agent: Ue {
                @display("p=327,171");
        }
        grid_operator_agent: Ue {
                @display("p=109,152");
        }
        substation_agent: Ue {
                @display("p=136,31");
        }
    connections:
        server.pppg++ <--> Eth10G <--> router.pppg++;
        router.pppg++ <--> Eth10G <--> pgw.filterGate;
        pgw.pppg++ <--> Eth10G <--> eNB.ppp;
}
