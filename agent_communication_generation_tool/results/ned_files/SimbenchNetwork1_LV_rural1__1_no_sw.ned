import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.networklayer.ipv4.RoutingTableRecorder;
import inet.node.ethernet.Eth10G;
import inet.node.inet.Router;
import inet.node.inet.StandardHost;
import simu5g.common.binder.Binder;
import simu5g.common.carrierAggregation.CarrierAggregation;
import simu5g.nodes.Ue;
import simu5g.nodes.eNodeB;
import simu5g.nodes.PgwStandard;
import simu5g.world.radio.LteChannelControl;
network SimbenchNetwork {
parameters: @display("i=block/network2;bgb=229.2032488891855,288.20141626591794");
submodules:

	channelControl: LteChannelControl{@display("p=100,100");}
	routingRecorder: RoutingTableRecorder{@display("p=100,100");}
	configurator: Ipv4NetworkConfigurator{@display("p=100,100");}
	binder: Binder{@display("p=100,100");}
	carrierAggregation: CarrierAggregation{@display("p=100,100");}
	server: StandardHost{@display("p=100,100");}
	router: Router{@display("p=100,100");}
	pgw: PgwStandard{@display("p=100,100");}
	eNB: eNodeB{@display("p=109,139");}
	household_agent_0: Ue {@display("p=120,10");}
	household_agent_1: Ue {@display("p=229,11");}
	household_agent_2: Ue {@display("p=229,11");}
	household_agent_3: Ue {@display("p=119,99");}
	household_agent_4: Ue {@display("p=118,209");}
	household_agent_5: Ue {@display("p=172,199");}
	household_agent_6: Ue {@display("p=64,98");}
	household_agent_7: Ue {@display("p=65,10");}
	household_agent_8: Ue {@display("p=226,288");}
	household_agent_9: Ue {@display("p=228,100");}
	household_agent_10: Ue {@display("p=184,99");}
	household_agent_11: Ue {@display("p=174,10");}
	household_agent_12: Ue {@display("p=227,199");}
	household_agent_13: Ue {@display("p=10,98");}
	household_agent_14: Ue {@display("p=229,11");}
	household_agent_15: Ue {@display("p=229,11");}
	storage_agent_0: Ue {@display("p=184,99");}
	storage_agent_1: Ue {@display("p=172,199");}
	storage_agent_2: Ue {@display("p=119,99");}
	storage_agent_3: Ue {@display("p=64,98");}
	generation_agent_0: Ue {@display("p=228,100");}
	generation_agent_1: Ue {@display("p=174,10");}
	generation_agent_2: Ue {@display("p=229,11");}
	generation_agent_3: Ue {@display("p=118,209");}
	generation_agent_4: Ue {@display("p=65,10");}
	generation_agent_5: Ue {@display("p=226,288");}
	generation_agent_6: Ue {@display("p=227,199");}
	generation_agent_7: Ue {@display("p=10,98");}
	control_center_agent: StandardHost {@display("p=100,100");}
	market_agent: StandardHost {@display("p=100,100");}
	aggregator_agent: Ue {@display("p=109,139");}
	pdc_agent: Ue {@display("p=109,139");}
	grid_operator_agent: StandardHost {@display("p=100,100");}
	substation_agent: Ue {@display("p=109,139");}
connections:
	server.pppg++ <--> Eth10G <--> router.pppg++;
	router.pppg++ <--> Eth10G <--> pgw.filterGate;
	pgw.pppg++ <--> Eth10G <--> eNB.ppp;
	router.pppg++ <--> Eth10G <--> control_center_agent.pppg++;
	router.pppg++ <--> Eth10G <--> market_agent.pppg++;
	router.pppg++ <--> Eth10G <--> grid_operator_agent.pppg++;
}