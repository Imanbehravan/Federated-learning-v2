// SPDX-License-Identifier: MIT

pragma solidity ^0.8.18;

contract Aggregator{
    uint256 public inputDimension = 0;
    uint256 public outputDimension = 0;
    uint256 public numParticipants = 0;
    uint256 public numClientsRegistered = 0;
    uint256 public roundNum = 0;
    uint256 public roundTime = 0;
    uint256 public roundStartTimeStamp = 0;
    uint256 public updateCounter = 0;
    uint256 public prevRoundUpdateCount = 0;
    uint256 public check = 0;
    int256 public Precision = 0;
    int256 public learning_rate = 0;
    int256 batchSize = 0;
    uint256 numRound = 0;
    bool public registerCheck = true; 
    mapping(uint256 => string) public clientsModelsHash;
    // mapping(uint256 => string) public clientsModelsBiasHash;
    mapping(address => uint256) public clients;
    mapping(uint256 => bool) public roundUpdateList;
    mapping(address => bool) public registeredAddressList;
    mapping(address => bytes32) public receivedFacts;
    
    constructor(uint256 inputDim, uint256 outputDim, uint256 participantsCount, 
    int256 _precision, int256 learningRate, int256 _batchSize,uint256 _numRound, uint256 updateInterval){
        inputDimension = inputDim;
        outputDimension = outputDim;
        numParticipants = participantsCount;
        roundTime = updateInterval;
        Precision = _precision;
        learning_rate = learningRate;
        batchSize = _batchSize;
        numRound = _numRound;

        for (uint256 i=0; i < numParticipants; i++ ){
            clientsModelsHash[i] = "000";
        }

    }
    
    function register() external{
        require(registerCheck, "no need for new worker.");
        require(!registeredAddressList[address(msg.sender)], "you have already registered.");
        clients[address(msg.sender)] = numClientsRegistered;
        roundUpdateList[numClientsRegistered] = false;
        numClientsRegistered = numClientsRegistered + 1;
        registeredAddressList[address(msg.sender)] = true;
        if (numClientsRegistered == numParticipants){
            registerCheck = false; 
            roundStartTimeStamp = block.timestamp;
            roundNum ++;
        }
    }

    function update_without_proof(string memory modelHash) public returns(bool){
        //checkZKP
        bool updateStatus = false;
        if (!registerCheck){
            if (block.timestamp - roundStartTimeStamp <= roundTime){
                uint256 clientIndex = clients[address(msg.sender)];
                if (!roundUpdateList[clientIndex]){
                    clientsModelsHash[clientIndex] = modelHash;
                    //clientsModelsBiasHash[clientIndex] = bias;
                    roundUpdateList[clientIndex] = true;
                    updateCounter ++;
                    updateStatus = true;
                    if (updateCounter == numParticipants){
                        prevRoundUpdateCount = updateCounter;
                        this.initNewRound();
                    }
                }
            }

            if ((block.timestamp - roundStartTimeStamp) > roundTime){
                this.initNewRound();
            }
        }
            
        return updateStatus;
    }

    function update_with_proof(string memory modelHash, bytes32 fact) public returns(bool){
        ////////////////////////////////////////////////
        //check to see if the fact is registered or not
        // verifier contract address: (0x8f97970aC5a9aa8D130d35146F5b59c4aef57963)
        receivedFacts[msg.sender] = fact;
        ////////////////////////////////////////////////
        bool updateStatus = false;
        if (!registerCheck){
            if (block.timestamp - roundStartTimeStamp <= roundTime){
                uint256 clientIndex = clients[address(msg.sender)];
                if (!roundUpdateList[clientIndex]){
                    clientsModelsHash[clientIndex] = modelHash;
                    //clientsModelsBiasHash[clientIndex] = bias;
                    roundUpdateList[clientIndex] = true;
                    updateCounter ++;
                    updateStatus = true;
                    if (updateCounter == numParticipants){
                        prevRoundUpdateCount = updateCounter;
                        this.initNewRound();
                    }
                }
            }

            if ((block.timestamp - roundStartTimeStamp) > roundTime){
                this.initNewRound();
            }
        }
            
        return updateStatus;
    }

    
    function initNewRound() external{
        check = check + 1;
        roundStartTimeStamp = block.timestamp;
        updateCounter = 0;
        roundNum ++;
        for (uint256 i=0; i < numParticipants; i++){
            roundUpdateList[i] = false;
        }
    }

    // function getWeights() public view returns(string[] memory){
    //     string[] memory weightsHash = new string[](prevRoundUpdateCount) ;
    //     uint256 _index = 0;
    //     for (uint256 i=0; i <= prevRoundUpdateCount; i++){
    //         weightsHash[_index] = clientsModelsWeightsHash[_index];
    //         _index ++;
    //     }
    //     return weightsHash;
    // }

    // function getBias() public view returns(string[] memory){
    //     string[] memory biasHash = new string[](prevRoundUpdateCount) ;
    //     uint256 _index = 0;
    //     for (uint256 i=0; i <= prevRoundUpdateCount; i++){
    //         biasHash[_index] = clientsModelsBiasHash[_index];
    //         _index ++;
    //     }
    //     return biasHash;
    // }

    function getModelHAsh() public view returns(string[] memory){
        string[] memory modelHash = new string[](prevRoundUpdateCount) ;
        uint256 _index = 0;
        for (uint256 i=0; i < prevRoundUpdateCount; i++){
            modelHash[_index] = clientsModelsHash[_index];
            _index ++;
        }
        return modelHash;
    }

    function getRoundNumber() external returns(uint256){
        return roundNum;
    }

    function getPrecision()external returns(int256){
        return Precision;
    }

    function getLearningRate()external returns(int256){
        return learning_rate;
    }

    function getBatchSize()external returns(int256){
        return batchSize;
    }

    function getRigesterCheck() external returns(bool){
        return registerCheck;
    }


    function roundUpdateOutstanding(address client) external returns(bool){
        uint256 clientIndex = clients[client];
        return roundUpdateList[clientIndex];
    }
    
    
}
