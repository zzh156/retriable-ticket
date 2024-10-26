// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract L2MessageReceiver {
    string public message;

    event MessageUpdated(string newMessage);

    // 构造函数设置默认值为 "no message"
    constructor() {
        message = "no message";
    }

    // 更新消息内容
    function updateMessage(string memory _newMessage) external {
        message = _newMessage;
        emit MessageUpdated(_newMessage);
    }

    // 展示当前的 message 值
    function getMessage() external view returns (string memory) {
        return message;
    }
}
//0x12fBAf906c3c4af268976bF855B2159813909D69