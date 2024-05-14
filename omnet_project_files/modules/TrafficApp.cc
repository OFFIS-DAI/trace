/*
 * TrafficApp.cc
 *
 *  Created on: 11 Apr 2021
 *      Author: malin
 *
 */

#include <cmath>
#include <omnetpp.h>
#include <omnetpp/platdep/sockets.h>
#include <string.h>
#include <algorithm>
#include <fstream>
#include <json.hpp>

#include "inet/applications/base/ApplicationPacket_m.h"
#include "inet/common/ModuleAccess.h"
#include "inet/common/TagBase_m.h"
#include "inet/common/TimeTag_m.h"
#include "inet/common/lifecycle/ModuleOperations.h"
#include "inet/common/packet/Packet.h"
#include "inet/common/packet/chunk/ByteCountChunk.h"
#include "inet/common/packet/chunk/BytesChunk.h"
#include "inet/networklayer/common/L3AddressResolver.h"
#include "inet/transportlayer/contract/udp/UdpSocket.h"

#include "TrafficApp.h"

// for convenience
using json = nlohmann::json;

Define_Module(TrafficApp);

TrafficApp::TrafficApp() {
}

TrafficApp::~TrafficApp() {
    // Save the simulation results to a JSON file
    simulationResults.saveToJsonFile("results/simulation_results_" + std::string(moduleName) + ".json");
}

void TrafficApp::initialize(int stage) {
    TcpAppBase::initialize(stage);
    if (stage == inet::INITSTAGE_APPLICATION_LAYER) {
        // get name of parent module as string for logging
        moduleName = this->getParentModule()->getName();
        this->initializeTrafficMessages();
    }
}


void TrafficApp::initializeTrafficMessages() {
    std::ifstream f(par("trafficConfigPath").stringValue());
    if (!f.is_open()) {
        return;
    }

    json data = json::parse(f);
    // Extract information from the JSON object

    // Extract sender
    std::string sender = data["sender"];
    if (sender != moduleName) {
        std::cerr << "Sender and module name are not equal!";
    }

    // Extract messageList array
    json messageList = data["messageList"];

    // Iterate over messages in messageList
    for (const auto& message : messageList) {
        // Extract information from each message
        int msgId = message["msgId"];
        int timeSend_ms = message["timeSend_ms"];
        std::string receiver = message["receiver"];
        int receiverPort = message["receiverPort"];
        int packetSize_B = message["packetSize_B"];


        inet::Packet *packet = new inet::Packet("data");
        const auto& trafficPayload = inet::makeShared<CustomTrafficChunk>();
        trafficPayload->setMsgId(msgId);
        trafficPayload->setTimeSend_ms(timeSend_ms);
        trafficPayload->setSender(moduleName);
        trafficPayload->setSenderPort(serverSocket.getLocalPort());
        trafficPayload->setReceiver(receiver.c_str());
        trafficPayload->setReceiverPort(receiverPort);
        trafficPayload->setPacketSize_B(packetSize_B);
        trafficPayload->setChunkLength(inet::B(packetSize_B));
        portToName[receiverPort] = receiver;
        packet->insertAtBack(trafficPayload);
        // Check for "reply" field and set it if present
        if (message.find("reply") != message.end()) {
            auto replyValue = message["reply"];
            int replyAfter_ms = message["replyAfter_ms"];
            trafficPayload->setReply(replyValue);
            trafficPayload->setReplyAfter(replyAfter_ms);
        }

        messageMap[receiverPort][timeSend_ms] = packet;
        connectToTimeToPort[timeSend_ms].push_back(receiverPort);
    }
}

void TrafficApp::handleMessageWhenUp(cMessage *msg)
{
    if(typeid(*msg) == typeid(Timer)) {
        // message is timer object in order to send data over the network
        handleTimer(msg);
    }
    else {
        // message is an event at the socket in the network
        TcpAppBase::socket.processMessage(msg);
    }
}

void TrafficApp::handleTimer(cMessage *msg) {
    if(msg != nullptr and typeid(*msg) == typeid(Timer)) {
        Timer *recvtimer = dynamic_cast<Timer *>(msg);
        switch (recvtimer->getTimerType()) {
        case -1:
            break;
        case 0:
            connect();
            break;

        case 1:
            sendData(recvtimer->getReceiverPort());
            break;

        case 2:
            close();
            break;
        }
    } else {
        throw cRuntimeError("TrafficApp: called handleTimer with non-Timer object.");
    }
    delete msg;
}

void TrafficApp::connect()
{
    int currentSimTime = simTime().inUnit(SIMTIME_MS);

    auto it = connectToTimeToPort.find(currentSimTime);

    inet::TcpSocket clientSocket;
    if (it != connectToTimeToPort.end()) {
        std::list<int> ports = connectToTimeToPort[currentSimTime];

        for (auto const& port : ports) {
            std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : connecting to port " << port << endl;
            inet::TcpSocket clientSocket;
            if(clientSockets.find(port) != clientSockets.end()) {
                clientSocket = clientSockets[port];
            }
            else {
                const char *localAddress = par("localAddress");
                int localPort = par("localPort");

                clientSocket.setOutputGate(gate("socketOut"));
                clientSocket.setCallback(this);
                try {
                    clientSocket.bind(
                            localAddress[0] ? inet::L3Address(localAddress) : inet::L3Address(),
                                    localPort);
                } catch(...) {
                    std::cerr << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") socket already bound." << endl;
                }
            }
            // we need a new connId if this is not the first connection
            clientSocket.renewSocket();

            int timeToLive = par("timeToLive");
            if (timeToLive != -1)
                clientSocket.setTimeToLive(timeToLive);

            int dscp = par("dscp");
            if (dscp != -1)
                clientSocket.setDscp(dscp);

            int tos = par("tos");
            if (tos != -1)
                clientSocket.setTos(tos);


            inet::L3Address destination;
            try {
                const char * connectAddress = portToName[port].c_str();

                inet::L3AddressResolver().tryResolve(connectAddress, destination);
                if (destination.isUnspecified()) {
                    std::cerr << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : connecting to " << connectAddress << " and port " << std::to_string(port) << ": cannot resolve destination address" << endl;
                }
                else {
                    std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : connecting to " << connectAddress << "(" << destination.str() << ") and port " << std::to_string(port) << endl;

                    clientSocket.connect(destination, port);

                    numSessions++;
                    emit(connectSignal, 1L);

                }
                clientSockets[port] = clientSocket;
            } catch(...) {
                std::cerr << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : Error when trying to resolve L3 address" << endl;
            }


        }
    }
    // Delete the entry for the specified key
    auto itToDelete = connectToTimeToPort.find(currentSimTime);
    if (itToDelete != connectToTimeToPort.end()) {
        connectToTimeToPort.erase(itToDelete);
        std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : Entry for key " << currentSimTime << " deleted.\n";
    }
    // Find the key with the minimum value
    auto minElement = std::min_element(connectToTimeToPort.begin(), connectToTimeToPort.end(), [](const auto& a, const auto& b) {
        return a.first < b.first and b.second.size() > 0;
    });

    // Check if the map is not empty before accessing the minimum element
    if (minElement != connectToTimeToPort.end()) {
        // schedule self-message for next simTime with messages
        Timer *timer = new Timer();
        timer->setTimerType(0);
        std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : schedule next connect timer for " << minElement->first << endl;
        simtime_t timerSchedulingTime = SimTime(minElement->first, SIMTIME_MS);
        if (timerSchedulingTime < simTime()) {
            std::cerr << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : Timer is to be scheduled in the past for (" << timerSchedulingTime.str() << ")" << endl;
        } else {
            scheduleAt(timerSchedulingTime, timer);
        }
    }
}

void TrafficApp::socketEstablished(inet::TcpSocket *socket) {
    int port = socket->getRemotePort();

    if(clientSockets.find(port) == clientSockets.end()) {
        std::cerr << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : established socket not saved in map: " << socket->getRemotePort() << endl;
    } else {
        auto connectTimer = new Timer();
        // type 1 means send
        connectTimer->setTimerType(1);
        connectTimer->setReceiverPort(port);
        scheduleAt(simTime(), connectTimer);
    }
}

void TrafficApp::socketDataArrived(inet::TcpSocket *socket, inet::Packet *msg, bool urgent) {
    std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : in socket data arrived for module " << moduleName << " and packet " << msg << endl;

    int delay = simTime().inUnit(SIMTIME_MS) - msg->getSendingTime().inUnit(SIMTIME_MS);
    int bytes = msg->getByteLength();

    if (msg->getArrivalGate() == gate("socketIn")) {
        inet::Packet *recvPacket = dynamic_cast<inet::Packet *>(msg);
        packetsRcvd++;
        bytesRcvd += msg->getByteLength();
        emit(inet::packetReceivedSignal, msg);


        if (recvPacket != nullptr) {
            inet::b offset = inet::b(0);  // start from the beginning

            while (auto chunk = recvPacket->peekAt(offset)->dupShared()) {  // for each chunk
                auto length = chunk->getChunkLength();

                if (chunk->getClassName() == std::string("inet::SliceChunk")) {
                    auto newPacket = recvPacket->peekData<inet::SliceChunk>();
                    auto encapsulatedChunk = newPacket->getChunk().get();
                    if (encapsulatedChunk->getClassName() == std::string("CustomTrafficChunk")) {
                        auto trafficChunk = encapsulatedChunk->peek<CustomTrafficChunk>(inet::b(0), encapsulatedChunk->getChunkLength());
                        int msgId = trafficChunk->getMsgId();
                        int delay = simTime().inUnit(SIMTIME_MS) - trafficChunk->getTimeSend_ms();
                        if (delay < 0) {
                            std::cout << "!! arrrival time " << simTime().inUnit(SIMTIME_MS) << " and send time " << trafficChunk->getTimeSend_ms() << endl;
                        }
                        int currentTime = simTime().inUnit(SIMTIME_MS);
                        simulationResults.addMessage(msgId, delay, bytes, currentTime);
                        if (trafficChunk->getReply()) {
                            inet::Packet *packet = new inet::Packet("data");
                            const auto& trafficPayload = inet::makeShared<CustomTrafficChunk>();
                            int newMsgId = curMsgId + serverSocket.getLocalPort() * 100;
                            curMsgId = curMsgId + 1;
                            trafficPayload->setMsgId(newMsgId);
                            int sendTime = currentTime + trafficChunk->getReplyAfter();
                            trafficPayload->setTimeSend_ms(sendTime);
                            trafficPayload->setSender(moduleName);
                            trafficPayload->setReceiver(trafficChunk->getSender());
                            trafficPayload->setSenderPort(serverSocket.getLocalPort());
                            trafficPayload->setReceiverPort(trafficChunk->getSenderPort());
                            trafficPayload->setPacketSize_B(trafficChunk->getPacketSize_B());
                            trafficPayload->setChunkLength(inet::B(trafficChunk->getPacketSize_B()));
                            packet->insertAtBack(trafficPayload);
                            portToName[trafficChunk->getSenderPort()] = trafficChunk->getSender();

                            std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : send reply to " << trafficChunk->getSender() << " with port " << trafficChunk->getSenderPort() << endl;

                            std::cout << "current time: " << simTime().inUnit(SIMTIME_MS) << ", sending time: " << sendTime << endl;
                            messageMap[trafficChunk->getSenderPort()][sendTime] = packet;
                            connectToTimeToPort[sendTime].push_back(trafficChunk->getSenderPort());
                            Timer *timer = new Timer();
                            timer->setTimerType(0);
                            std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : schedule next connect timer for " << sendTime << endl;
                            simtime_t timerSchedulingTime = SimTime(sendTime, SIMTIME_MS);
                            if (timerSchedulingTime < simTime()) {
                                std::cerr << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : Timer is to be scheduled in the past for (" << timerSchedulingTime.str() << ")" << endl;
                            } else {
                                scheduleAt(timerSchedulingTime, timer);
                            }
                            simulationResults.addMessageSent(newMsgId, trafficChunk->getPacketSize_B(), sendTime, simTime().inUnit(SIMTIME_MS), moduleName, trafficChunk->getSender());
                        }
                        break;
                    }
                    else if (encapsulatedChunk->getClassName() == std::string("inet::SequenceChunk")) {
                        inet::SequenceChunk *encapsulatedSequenceChunk = dynamic_cast<inet::SequenceChunk *>(encapsulatedChunk);
                        auto queue = encapsulatedSequenceChunk->getChunks();
                        for (int i=0; i < queue.size(); i++) {
                            auto item = queue[i];
                            auto itemget = item.get();
                            if (itemget->getClassName() == std::string("inet::SliceChunk")) {
                                const inet::SliceChunk *encapsulatedSliceChunk = dynamic_cast<const inet::SliceChunk *>(itemget);
                                auto trafficChunkInSliceChunk = encapsulatedSliceChunk->getChunk();
                                auto trafficChunk = trafficChunkInSliceChunk->peek<CustomTrafficChunk>(inet::b(0), trafficChunkInSliceChunk->getChunkLength());
                                int msgId = trafficChunk->getMsgId();
                                int delay = simTime().inUnit(SIMTIME_MS) - trafficChunk->getTimeSend_ms();
                                if (delay < 0) {
                                    std::cout << "!! arrrival time " << simTime().inUnit(SIMTIME_MS) << " and send time " << trafficChunk->getTimeSend_ms() << endl;
                                }
                                int currentTime = simTime().inUnit(SIMTIME_MS);
                                simulationResults.addMessage(msgId, delay, bytes, currentTime);
                                if (trafficChunk->getReply()) {
                                    inet::Packet *packet = new inet::Packet("data");
                                    const auto& trafficPayload = inet::makeShared<CustomTrafficChunk>();
                                    int newMsgId = curMsgId + serverSocket.getLocalPort() * 100;
                                    curMsgId = curMsgId + 1;
                                    trafficPayload->setMsgId(newMsgId);
                                    int sendTime = currentTime + trafficChunk->getReplyAfter();
                                    trafficPayload->setTimeSend_ms(sendTime);
                                    trafficPayload->setSender(moduleName);
                                    trafficPayload->setSenderPort(serverSocket.getLocalPort());
                                    trafficPayload->setReceiver(trafficChunk->getSender());
                                    trafficPayload->setReceiverPort(trafficChunk->getSenderPort());
                                    trafficPayload->setPacketSize_B(trafficChunk->getPacketSize_B());
                                    trafficPayload->setChunkLength(inet::B(trafficChunk->getPacketSize_B()));
                                    packet->insertAtBack(trafficPayload);

                                    portToName[trafficChunk->getSenderPort()] = trafficChunk->getSender();

                                    std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : send reply to " << trafficChunk->getSender() << " with port " << trafficChunk->getSenderPort() << endl;
                                    std::cout << "current time: " << simTime().inUnit(SIMTIME_MS) << ", sending time: " << sendTime << endl;


                                    messageMap[trafficChunk->getSenderPort()][sendTime] = packet;
                                    connectToTimeToPort[sendTime].push_back(trafficChunk->getSenderPort());
                                    Timer *timer = new Timer();
                                    timer->setTimerType(0);
                                    std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : schedule next connect timer for " << sendTime << endl;
                                    simtime_t timerSchedulingTime = SimTime(sendTime, SIMTIME_MS);
                                    if (timerSchedulingTime < simTime()) {
                                        std::cerr << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : Timer is to be scheduled in the past for (" << timerSchedulingTime.str() << ")" << endl;
                                    } else {
                                        scheduleAt(timerSchedulingTime, timer);
                                    }
                                    simulationResults.addMessageSent(newMsgId, trafficChunk->getPacketSize_B(), sendTime, simTime().inUnit(SIMTIME_MS), moduleName, trafficChunk->getSender());
                                }
                                return;
                            }
                        }
                    }
                } else if (chunk->getClassName() == std::string("CustomTrafficChunk")) {
                    auto trafficChunk = chunk->peek<CustomTrafficChunk>(inet::b(0), chunk->getChunkLength());
                    int msgId = trafficChunk->getMsgId();
                    int delay = simTime().inUnit(SIMTIME_MS) - trafficChunk->getTimeSend_ms();
                    if (delay < 0) {
                        std::cout << "!! arrrival time " << simTime().inUnit(SIMTIME_MS) << " and send time " << trafficChunk->getTimeSend_ms() << endl;
                    }
                    int currentTime = simTime().inUnit(SIMTIME_MS);
                    simulationResults.addMessage(msgId, delay, bytes, currentTime);
                    if (trafficChunk->getReply()) {
                        inet::Packet *packet = new inet::Packet("data");
                        const auto& trafficPayload = inet::makeShared<CustomTrafficChunk>();
                        int newMsgId = curMsgId + serverSocket.getLocalPort() * 100;
                        curMsgId = curMsgId + 1;
                        trafficPayload->setMsgId(newMsgId);
                        int sendTime = currentTime + trafficChunk->getReplyAfter();
                        trafficPayload->setTimeSend_ms(sendTime);
                        trafficPayload->setSender(moduleName);
                        trafficPayload->setSenderPort(serverSocket.getLocalPort());
                        trafficPayload->setReceiver(trafficChunk->getSender());
                        trafficPayload->setReceiverPort(trafficChunk->getSenderPort());
                        trafficPayload->setPacketSize_B(trafficChunk->getPacketSize_B());
                        trafficPayload->setChunkLength(inet::B(trafficChunk->getPacketSize_B()));
                        packet->insertAtBack(trafficPayload);

                        std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : send reply to " << trafficChunk->getSender() << " with port " << trafficChunk->getSenderPort() << endl;
                        std::cout << "current time: " << simTime().inUnit(SIMTIME_MS) << ", sending time: " << sendTime << endl;

                        portToName[trafficChunk->getSenderPort()] = trafficChunk->getSender();
                        messageMap[trafficChunk->getSenderPort()][sendTime] = packet;
                        connectToTimeToPort[sendTime].push_back(trafficChunk->getSenderPort());
                        Timer *timer = new Timer();
                        timer->setTimerType(0);
                        std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : schedule next connect timer for " << sendTime << endl;
                        simtime_t timerSchedulingTime = SimTime(sendTime, SIMTIME_MS);
                        if (timerSchedulingTime < simTime()) {
                            std::cerr << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : Timer is to be scheduled in the past for (" << timerSchedulingTime.str() << ")" << endl;
                        } else {
                            scheduleAt(timerSchedulingTime, timer);
                        }
                        simulationResults.addMessageSent(newMsgId, trafficChunk->getPacketSize_B(), sendTime, simTime().inUnit(SIMTIME_MS), moduleName, trafficChunk->getSender());
                    }
                    break;
                }
                else {
                    offset += chunk->getChunkLength();
                    if (offset >= recvPacket->getTotalLength()) {
                        // could not find chunk
                        std::cerr << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : couldn't find Chunk in message. " << endl;
                        break;
                    }

                }
            }
        }
    }

    TcpAppBase::socketDataArrived(socket, msg, urgent);
    socket->close();
}

void TrafficApp::sendData(int receiverPort) {
    if(clientSockets.find(receiverPort) != clientSockets.end()) {
        inet::TcpSocket clientSocket;
        clientSocket = clientSockets[receiverPort];

        int currentTime = simTime().inUnit(SIMTIME_MS);
        int minimumTime = 100000000;
        for(const auto& elem : messageMap[receiverPort])
        {
            if (elem.first < minimumTime) {
                minimumTime = elem.first;
            }
        }
        if (minimumTime > simTime().inUnit(SIMTIME_MS)) {
            std::cout << moduleName << "(" << simTime().inUnit(SIMTIME_MS) << ") : send packet later at " << minimumTime << endl;
        }
        else if (messageMap[receiverPort].count(minimumTime)) {
            inet::Packet *packet = messageMap[receiverPort][minimumTime];
            std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : send data " << packet << endl;
            int numBytes = packet->getByteLength();
            emit(inet::packetSentSignal, packet);
            clientSocket.send(packet);
            packetsSent++;
            bytesSent += numBytes;
            if (packet->getOwner() == this) {
                delete packet;
            }
            messageMap[receiverPort].erase(minimumTime);
        } else {
            std::cerr << moduleName << " " <<"(" << simTime().inUnit(SIMTIME_MS) << ") : minimum time not in map. " << endl;
        }
    } else {
        std::cerr << moduleName << " " <<"(" << simTime().inUnit(SIMTIME_MS) << ") : receiver port " << receiverPort << " not found in sockets." << endl;

    }
}

void TrafficApp::socketClosed(inet::TcpSocket *socket) {
    TcpAppBase::socketClosed(socket);
    if (operationalState == State::STOPPING_OPERATION && !this->socket.isOpen())
        startActiveOperationExtraTimeOrFinish(par("stopOperationExtraTime"));
}

void TrafficApp::socketFailure(inet::TcpSocket *socket, int code) {
    TcpAppBase::socketFailure(socket, code);
}

void TrafficApp::handleStartOperation(inet::LifecycleOperation *operation) {
    const char *localAddress = par("localAddress");
    int localPort = par("localPort");

    serverSocket.setOutputGate(gate("socketOut"));
    serverSocket.setCallback(this);
    serverSocket.bind(
            localAddress[0] ? inet::L3Address(localAddress) : inet::L3Address(),
                    localPort);
    serverSocket.listen();
    simtime_t start = simTime();
    auto timerMsg = new Timer();
    // type 0 means connect
    timerMsg->setTimerType(0);
    scheduleAt(start, timerMsg);
}

void TrafficApp::handleStopOperation(inet::LifecycleOperation *operation) {
    if (socket.isOpen()) close();
    delayActiveOperationFinish(par("stopOperationTimeout"));
}

void TrafficApp::handleCrashOperation(inet::LifecycleOperation *operation) {
}

void TrafficApp::finish() {
    std::cout << moduleName << " " << "(" << simTime().inUnit(SIMTIME_MS) << ") : received "
            << packetsRcvd << " packets and sent " << packetsSent << " packets " << endl;
}
