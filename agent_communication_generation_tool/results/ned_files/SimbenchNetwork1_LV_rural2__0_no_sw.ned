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
parameters: @display("i=block/network2;bgb=1737.2263554116944,580.1706890978385");
submodules:

	channelControl: LteChannelControl{@display("p=100,100");}
	routingRecorder: RoutingTableRecorder{@display("p=100,100");}
	configurator: Ipv4NetworkConfigurator{@display("p=100,100");}
	binder: Binder{@display("p=100,100");}
	carrierAggregation: CarrierAggregation{@display("p=100,100");}
	server: StandardHost{@display("p=100,100");}
	router: Router{@display("p=100,100");}
	pgw: PgwStandard{@display("p=100,100");}
	eNB: eNodeB{@display("p=863,285");}
	household_agent_0: Ue {@display("p=1237,102");}
	household_agent_1: Ue {@display("p=1626,537");}
	household_agent_2: Ue {@display("p=1517,536");}
	household_agent_3: Ue {@display("p=960,542");}
	household_agent_4: Ue {@display("p=960,542");}
	household_agent_5: Ue {@display("p=1245,368");}
	household_agent_6: Ue {@display("p=1353,535");}
	household_agent_7: Ue {@display("p=207,491");}
	household_agent_8: Ue {@display("p=676,529");}
	household_agent_9: Ue {@display("p=1462,536");}
	household_agent_10: Ue {@display("p=381,526");}
	household_agent_11: Ue {@display("p=1619,83");}
	household_agent_12: Ue {@display("p=1182,102");}
	household_agent_13: Ue {@display("p=1409,369");}
	household_agent_14: Ue {@display("p=905,542");}
	household_agent_15: Ue {@display("p=905,542");}
	household_agent_16: Ue {@display("p=1290,213");}
	household_agent_17: Ue {@display("p=206,580");}
	household_agent_18: Ue {@display("p=720,540");}
	household_agent_19: Ue {@display("p=720,540");}
	household_agent_20: Ue {@display("p=1563,216");}
	household_agent_21: Ue {@display("p=1236,213");}
	household_agent_22: Ue {@display("p=1139,13");}
	household_agent_23: Ue {@display("p=1464,381");}
	household_agent_24: Ue {@display("p=720,540");}
	household_agent_25: Ue {@display("p=720,540");}
	household_agent_26: Ue {@display("p=1004,532");}
	household_agent_27: Ue {@display("p=523,527");}
	household_agent_28: Ue {@display("p=1571,537");}
	household_agent_29: Ue {@display("p=818,530");}
	household_agent_30: Ue {@display("p=1727,217");}
	household_agent_31: Ue {@display("p=1309,545");}
	household_agent_32: Ue {@display("p=1309,545");}
	household_agent_33: Ue {@display("p=1027,366");}
	household_agent_34: Ue {@display("p=1400,214");}
	household_agent_35: Ue {@display("p=1400,214");}
	household_agent_36: Ue {@display("p=983,365");}
	household_agent_37: Ue {@display("p=1238,13");}
	household_agent_38: Ue {@display("p=1408,535");}
	household_agent_39: Ue {@display("p=1454,215");}
	household_agent_40: Ue {@display("p=954,11");}
	household_agent_41: Ue {@display("p=578,539");}
	household_agent_42: Ue {@display("p=855,21");}
	household_agent_43: Ue {@display("p=1510,71");}
	household_agent_44: Ue {@display("p=1041,12");}
	household_agent_45: Ue {@display("p=1617,371");}
	household_agent_46: Ue {@display("p=305,492");}
	household_agent_47: Ue {@display("p=621,528");}
	household_agent_48: Ue {@display("p=173,568");}
	household_agent_49: Ue {@display("p=163,491");}
	household_agent_50: Ue {@display("p=1618,227");}
	household_agent_51: Ue {@display("p=1183,13");}
	household_agent_52: Ue {@display("p=1562,371");}
	household_agent_53: Ue {@display("p=130,568");}
	household_agent_54: Ue {@display("p=1028,211");}
	household_agent_55: Ue {@display("p=1565,72");}
	household_agent_56: Ue {@display("p=899,10");}
	household_agent_57: Ue {@display("p=1309,545");}
	household_agent_58: Ue {@display("p=1309,545");}
	household_agent_59: Ue {@display("p=905,542");}
	household_agent_60: Ue {@display("p=905,542");}
	household_agent_61: Ue {@display("p=929,376");}
	household_agent_62: Ue {@display("p=479,527");}
	household_agent_63: Ue {@display("p=87,490");}
	household_agent_64: Ue {@display("p=87,490");}
	household_agent_65: Ue {@display("p=1401,81");}
	household_agent_66: Ue {@display("p=261,481");}
	household_agent_67: Ue {@display("p=1058,532");}
	household_agent_68: Ue {@display("p=1518,370");}
	household_agent_69: Ue {@display("p=130,479");}
	household_agent_70: Ue {@display("p=1300,368");}
	household_agent_71: Ue {@display("p=1136,367");}
	household_agent_72: Ue {@display("p=10,567");}
	household_agent_73: Ue {@display("p=1072,211");}
	household_agent_74: Ue {@display("p=1200,533");}
	household_agent_75: Ue {@display("p=86,568");}
	household_agent_76: Ue {@display("p=261,569");}
	household_agent_77: Ue {@display("p=1156,533");}
	household_agent_78: Ue {@display("p=1096,12");}
	household_agent_79: Ue {@display("p=1127,212");}
	household_agent_80: Ue {@display("p=1291,103");}
	household_agent_81: Ue {@display("p=436,526");}
	household_agent_82: Ue {@display("p=763,529");}
	household_agent_83: Ue {@display("p=1400,214");}
	household_agent_84: Ue {@display("p=1400,214");}
	household_agent_85: Ue {@display("p=997,11");}
	household_agent_86: Ue {@display("p=960,542");}
	household_agent_87: Ue {@display("p=960,542");}
	household_agent_88: Ue {@display("p=42,567");}
	household_agent_89: Ue {@display("p=1292,14");}
	household_agent_90: Ue {@display("p=1082,366");}
	household_agent_91: Ue {@display("p=304,569");}
	household_agent_92: Ue {@display("p=1345,214");}
	household_agent_93: Ue {@display("p=862,530");}
	household_agent_94: Ue {@display("p=87,490");}
	household_agent_95: Ue {@display("p=87,490");}
	household_agent_96: Ue {@display("p=1255,534");}
	household_agent_97: Ue {@display("p=1682,372");}
	household_agent_98: Ue {@display("p=801,10");}
	household_agent_99: Ue {@display("p=1102,544");}
	household_agent_100: Ue {@display("p=1735,538");}
	household_agent_101: Ue {@display("p=1355,369");}
	household_agent_102: Ue {@display("p=1737,372");}
	household_agent_103: Ue {@display("p=1181,212");}
	household_agent_104: Ue {@display("p=1681,538");}
	household_agent_105: Ue {@display("p=1180,367");}
	household_agent_106: Ue {@display("p=1509,215");}
	household_agent_107: Ue {@display("p=1456,71");}
	household_agent_108: Ue {@display("p=1674,73");}
	household_agent_109: Ue {@display("p=1729,73");}
	household_agent_110: Ue {@display("p=1684,217");}
	generation_agent_0: Ue {@display("p=206,580");}
	generation_agent_1: Ue {@display("p=1464,381");}
	generation_agent_2: Ue {@display("p=1618,227");}
	generation_agent_3: Ue {@display("p=1072,211");}
	generation_agent_4: Ue {@display("p=1291,103");}
	generation_agent_5: Ue {@display("p=1619,83");}
	generation_agent_6: Ue {@display("p=905,542");}
	generation_agent_7: Ue {@display("p=305,492");}
	control_center_agent: StandardHost {@display("p=100,100");}
	market_agent: StandardHost {@display("p=100,100");}
	aggregator_agent: Ue {@display("p=863,285");}
	pdc_agent: Ue {@display("p=863,285");}
	grid_operator_agent: StandardHost {@display("p=100,100");}
	substation_agent: Ue {@display("p=863,285");}
connections:
	server.pppg++ <--> Eth10G <--> router.pppg++;
	router.pppg++ <--> Eth10G <--> pgw.filterGate;
	pgw.pppg++ <--> Eth10G <--> eNB.ppp;
	router.pppg++ <--> Eth10G <--> control_center_agent.pppg++;
	router.pppg++ <--> Eth10G <--> market_agent.pppg++;
	router.pppg++ <--> Eth10G <--> grid_operator_agent.pppg++;
}