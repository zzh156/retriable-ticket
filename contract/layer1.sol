// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IArbitrumInbox {
    function createRetryableTicket(
        address to,
        uint256 l2CallValue,
        uint256 maxSubmissionCost,
        address excessFeeRefundAddress,
        address callValueRefundAddress,
        uint256 gasLimit,
        uint256 maxFeePerGas,
        bytes calldata data
    ) external payable returns (uint256);
}

contract L1ToL2Message {
    address public l2Target; // layer2 合约地址
    address public inboxAddress = 0xaAe29B0366299461418F5324a79Afc425BE5ae21; // Arbitrum Sepolia inbox 地址

    event RetryableTicketCreated(uint256 indexed ticketId);

    constructor(address _l2Target) {
        l2Target = _l2Target;
    }

    function sendMessageToL2(string memory _message) external payable {
        IArbitrumInbox inbox = IArbitrumInbox(inboxAddress);
        
        bytes memory data = abi.encodeWithSignature("updateMessage(string)", _message);

        uint256 ticketId = inbox.createRetryableTicket{value: msg.value}(
            l2Target,
            0,                      // L2 call value
            10000000000000000,        // maxSubmissionCost
            msg.sender,             // excessFeeRefundAddress
            msg.sender,             // callValueRefundAddress
            1000000,                // gasLimit
            800000000,             // maxFeePerGas
            data
        );

        emit RetryableTicketCreated(ticketId);
    }
}
