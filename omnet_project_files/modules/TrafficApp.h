/*
 * TrafficApp.h
 *
 *  Created on: May 25, 2021
 *      Author: malin
 *
 *  The TrafficApp represents the implementation of the application layer (and transport layer)
 *  of the end devices, which represent the agents in coupled simulation on the OMNeT++ side.
 *  The TrafficApp sends messages in OMNeT++ over TCP.
 */

#ifndef TRAFFICAPP_H_
#define TRAFFICAPP_H_

#include <vector>
#include <algorithm>

#include "inet/applications/tcpapp/TcpAppBase.h"
#include "inet/common/lifecycle/LifecycleOperation.h"
#include "inet/common/lifecycle/NodeStatus.h"

#include "messages/Timer_m.h"
#include "../messages/CustomTrafficChunk_m.h"

using namespace omnetpp;

// Define a struct to represent a message
struct MessageResult {
    int msgId;
    int delay;
    int packetSize_B;
    int receivingTime_ms;

    // Constructor to initialize the values
    MessageResult(int _msgId, int _delay, int _packetSize_B, int _receivingTime_ms) : msgId(_msgId), delay(_delay), packetSize_B(_packetSize_B), receivingTime_ms(_receivingTime_ms) {}
};

// Define a struct to represent a additionally sent message
struct MessageSent {
    int msgId;
    int packetSize_B;
    int sendingTime_ms;
    int calculationStart_ms;
    std::string sender;
    std::string receiver;

    // Constructor to initialize the values
    MessageSent(int _msgId, int _packetSize_B, int _sendingTime_ms, int _calculationStart_ms, std::string _sender, std::string _receiver) : msgId(_msgId), packetSize_B(_packetSize_B), sendingTime_ms(_sendingTime_ms), calculationStart_ms(_calculationStart_ms), sender(_sender), receiver(_receiver) {}
};

// Define a data class to store simulation results
class SimulationResults {
public:
    // Function to add a message to the list
    void addMessage(int msgId, int delay, int packetSize_B, int receivingTime_ms) {
        messages.emplace_back(msgId, delay, packetSize_B, receivingTime_ms);
    }
    // Function to add a message to the list
    void addMessageSent(int msgId, int packetSize_B, int sendingTime_ms, int calculationStart_ms, std::string sender, std::string receiver) {
        messagesSent.emplace_back(msgId, packetSize_B, sendingTime_ms, calculationStart_ms, sender, receiver);
    }
    // Function to serialize to JSON
    nlohmann::json toJson() const {
        nlohmann::json jsonResult;
        for (const auto& message : messages) {
            jsonResult.push_back({
                {"msgId", message.msgId},
                {"delay_ms", message.delay},
                {"packetSize_B", message.packetSize_B},
                {"receivingTime_ms", message.receivingTime_ms}
            });
        }
        for (const auto& message : messagesSent) {
            jsonResult.push_back({
                {"msgId", message.msgId},
                {"packetSize_B", message.packetSize_B},
                {"sendingTime_ms", message.sendingTime_ms},
                {"calculationStart_ms", message.calculationStart_ms},
                {"sender", message.sender},
                {"receiver", message.receiver},
                {"type", "reply"}
            });
        }
        return jsonResult;
    }

    // Function to save to a JSON file
    void saveToJsonFile(const std::string& filename) const {
        std::ofstream file(filename);
        if (file.is_open()) {
            file << std::setw(4) << toJson() << std::endl;
            file.close();
            std::cout << "Simulation results saved to " << filename << std::endl;
        } else {
            std::cerr << "Error opening file: " << filename << std::endl;
        }
    }


private:
    std::vector<MessageResult> messages;
    std::vector<MessageSent> messagesSent;
};


class TrafficApp : public inet::TcpAppBase {
private:
    inet::TcpSocket serverSocket;
    std::map<int, std::list<int>> connectToTimeToPort;
    std::map<int, std::string> portToName;
    std::map<int, inet::TcpSocket> clientSockets;
    std::map<int,std::list<Timer *>> timer;

    int curMsgId = 0;


    std::map<const int, std::map<int, inet::Packet *>> messageMap; // <receiverPort, <time to send, packetToSend>

    const char* moduleName = "";

    // Create a SimulationResults object
    SimulationResults simulationResults;

public:
    TrafficApp();
    ~TrafficApp();

protected:


    /**
     * Initialize module and register at Scheduler.
     */
    void initialize(int stage) override;

    virtual void initializeTrafficMessages();
    /**
     * Return number of init stages.
     */
    int numInitStages() const override { return (inet::NUM_INIT_STAGES); }
    /**
     * Overwrites message of TcpAppBase to be able to receive messages from CosimaScheduler
     */
    void handleMessageWhenUp(cMessage *msg) override;
    /**
     * Handle timer for TCP connection.
     */
    virtual void handleTimer(cMessage *msg) override;
    /**
     * Is called as soon as socket connection is established.
     */
    virtual void socketEstablished(inet::TcpSocket *socket) override;
    /**
     * Data arrived at the socket over network.
     * The delay is to be calculated and send back to coupled simulation.
     */
    virtual void socketDataArrived(inet::TcpSocket *socket, inet::Packet *msg, bool urgent) override;
    /**
     * Socket is closed, cancel timer message.
     */
    virtual void socketClosed(inet::TcpSocket *socket) override;
    /**
     * Socket connection failed, cancel timer message.
     */
    virtual void socketFailure(inet::TcpSocket *socket, int code) override;
    /**
     * Set up server socket for incoming connections.
     */
    virtual void handleStartOperation(inet::LifecycleOperation *operation) override;
    /**
     * Cancel timer event in stop operation.
     */
    virtual void handleStopOperation(inet::LifecycleOperation *operation) override;
    /**
     * Cancel timer event in crash operation.
     */
    virtual void handleCrashOperation(inet::LifecycleOperation *operation) override;
    /**
     * Send data over inet network.
     */
    virtual void sendData(int receiverPort);

    /**
     * Is called to connect to another client.
     */
    void connect() override;

    /**
     * Is to be called at the end of the simulation.
     */
    virtual void finish() override;


};




#endif /* TRAFFICAPP_H_ */
