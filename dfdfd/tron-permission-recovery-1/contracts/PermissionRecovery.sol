// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title PermissionRecovery
 * @dev 用于恢复 TRON 钱包权限的合约
 *
 * 功能：
 * 1. 保存并记录目标权限（owner / active / threshold）
 * 2. 时间锁机制防止再次被转移
 * 3. 紧急暂停功能
 *
 * 说明：
 * - TRON 账户的权限（owner/active/threshold）是链上账户的属性，智能合约无法直接修改外部账户的权限。
 * - 本合约的作用是：由原始所有者发起并在时间锁后发出事件（包含要设置的 targetActive 和 threshold），
 *   你可以在链外监听该事件或查询合约状态，然后使用原始私钥通过 tronweb/tron-api 调用 TRON 节点的权限修改接口（updateAccountPermission）来真正修改账户权限。
 */

contract PermissionRecovery {
    // ============ 状态变量 ============
    address public originalOwner;           // 原始所有者地址
    address public recoveryAddress;         // 恢复目标地址（最终 owner 地址）
    address public targetActive;            // 要设置的 active 权限地址
    address public emergencyRecoveryAddress; // 紧急恢复地址
    uint256 public threshold;               // 要设置的多签阈值
    uint256 public approverThreshold;       // 多签审批所需的签名数
    uint256 public recoveryTimestamp;       // 恢复时间戳
    uint256 public timeLockDuration;        // 时间锁持续时间（秒）
    bool public isRecoveryInitiated;        // 恢复是否已启动
    bool public isRecoveryCompleted;        // 恢复是否已完成
    bool public isPaused;                   // 是否已暂停
    bool public emergencyRecoveryEnabled;   // 是否允许紧急恢复
    mapping(address => bool) public approvers; // 审批者集合
    mapping(address => bool) public approvals;  // 已审批的地址
    uint256 public approvalCount;           // 当前审批次数

    // ============ 事件 ============
    event RecoveryInitiated(
        address indexed owner,
        address indexed recoveryAddress,
        address indexed targetActive,
        uint256 threshold,
        uint256 timestamp
    );

    event RecoveryCompleted(
        address indexed owner,
        address indexed recoveryAddress,
        address indexed targetActive,
        uint256 threshold,
        uint256 timestamp
    );

    event RecoveryPaused(uint256 timestamp);
    event RecoveryResumed(uint256 timestamp);
    event RecoverySettingsUpdated(address indexed owner, address indexed targetActive, uint256 threshold, uint256 timestamp);
    event RecoveryCancelled(address indexed owner, uint256 timestamp);
    event ApproverAdded(address indexed approver, uint256 threshold, uint256 timestamp);
    event ApprovalReceived(address indexed approver, uint256 count, uint256 timestamp);
    event EmergencyRecoveryTriggered(address indexed initiator, address indexed target, uint256 timestamp);

    // ============ 修饰符 ============
    modifier onlyOriginalOwner() {
        require(msg.sender == originalOwner, "Only original owner can call this function");
        _;
    }

    modifier whenNotPaused() {
        require(!isPaused, "Recovery is currently paused");
        _;
    }

    modifier onlyAfterTimeLock() {
        require(isRecoveryInitiated, "Recovery has not been initiated");
        require(block.timestamp >= recoveryTimestamp + timeLockDuration, "Time lock period has not passed");
        _;
    }

    // ============ 构造函数 ============
    constructor(
        address _originalOwner,
        address _recoveryAddress,
        address _targetActive,
        uint256 _threshold,
        uint256 _timeLockDuration,
        address _emergencyRecoveryAddress,
        uint256 _approverThreshold
    ) {
        require(_originalOwner != address(0), "Original owner cannot be zero address");
        require(_recoveryAddress != address(0), "Recovery address cannot be zero address");
        require(_targetActive != address(0), "Target active cannot be zero address");
        require(_emergencyRecoveryAddress != address(0), "Emergency recovery address cannot be zero address");
        require(_timeLockDuration > 0, "Time lock duration must be greater than 0");
        require(_threshold > 0, "Threshold must be greater than 0");
        require(_approverThreshold > 0, "Approver threshold must be greater than 0");

        originalOwner = _originalOwner;
        recoveryAddress = _recoveryAddress;
        targetActive = _targetActive;
        threshold = _threshold;
        approverThreshold = _approverThreshold;
        timeLockDuration = _timeLockDuration;
        emergencyRecoveryAddress = _emergencyRecoveryAddress;
        emergencyRecoveryEnabled = false;
        isPaused = false;
        isRecoveryInitiated = false;
        isRecoveryCompleted = false;
        approvers[_originalOwner] = true;
        approvals[_originalOwner] = false;
    }

    // ============ 恢复函数 ============
    /**
     * @dev 在发起恢复前可以更新目标设置（仅原始所有者）
     */
    function setTargetSettings(address _targetActive, uint256 _threshold) public onlyOriginalOwner whenNotPaused {
        require(!isRecoveryInitiated, "Cannot change settings after initiation");
        require(!isRecoveryCompleted, "Cannot change settings after completion");
        require(_targetActive != address(0), "Target active cannot be zero address");
        require(_threshold > 0, "Threshold must be greater than 0");
        targetActive = _targetActive;
        threshold = _threshold;

        emit RecoverySettingsUpdated(msg.sender, targetActive, threshold, block.timestamp);
    }

    function initiateRecovery() public onlyOriginalOwner whenNotPaused {
        require(!isRecoveryInitiated, "Recovery already initiated");
        require(!isRecoveryCompleted, "Recovery already completed");

        isRecoveryInitiated = true;
        recoveryTimestamp = block.timestamp;

        emit RecoveryInitiated(originalOwner, recoveryAddress, targetActive, threshold, block.timestamp);
    }

    function completeRecovery() public onlyOriginalOwner onlyAfterTimeLock whenNotPaused {
        require(!isRecoveryCompleted, "Recovery already completed");

        isRecoveryCompleted = true;

        emit RecoveryCompleted(originalOwner, recoveryAddress, targetActive, threshold, block.timestamp);
    }

    function pauseRecovery() public onlyOriginalOwner {
        require(!isPaused, "Recovery is already paused");
        require(!isRecoveryCompleted, "Cannot pause after completion");
        isPaused = true;
        emit RecoveryPaused(block.timestamp);
    }

    function resumeRecovery() public onlyOriginalOwner {
        require(isPaused, "Recovery is not paused");
        require(!isRecoveryCompleted, "Cannot resume after completion");
        isPaused = false;
        emit RecoveryResumed(block.timestamp);
    }

    function cancelRecovery() public onlyOriginalOwner whenNotPaused {
        require(isRecoveryInitiated, "Recovery has not been initiated");
        require(!isRecoveryCompleted, "Recovery already completed");

        isRecoveryInitiated = false;
        recoveryTimestamp = 0;
        approvalCount = 0;
        emergencyRecoveryEnabled = false;

        emit RecoveryCancelled(msg.sender, block.timestamp);
    }

    function addApprover(address _approver) public onlyOriginalOwner whenNotPaused {
        require(_approver != address(0), "Approver cannot be zero address");
        require(!approvers[_approver], "Approver already exists");
        approvers[_approver] = true;
        emit ApproverAdded(_approver, approverThreshold, block.timestamp);
    }

    function approveRecovery() public whenNotPaused {
        require(approvers[msg.sender], "Only approved approver can approve");
        require(isRecoveryInitiated, "Recovery has not been initiated");
        require(!isRecoveryCompleted, "Recovery already completed");
        require(!approvals[msg.sender], "Approver already approved");

        approvals[msg.sender] = true;
        approvalCount += 1;

        emit ApprovalReceived(msg.sender, approvalCount, block.timestamp);
    }

    function triggerEmergencyRecovery() public whenNotPaused {
        require(emergencyRecoveryEnabled, "Emergency recovery is not enabled");
        require(msg.sender == emergencyRecoveryAddress, "Only emergency recovery address can trigger");
        require(isRecoveryInitiated, "Recovery has not been initiated");
        require(!isRecoveryCompleted, "Recovery already completed");

        isRecoveryCompleted = true;
        emit EmergencyRecoveryTriggered(msg.sender, targetActive, block.timestamp);
    }

    function enableEmergencyRecovery() public onlyOriginalOwner {
        require(!emergencyRecoveryEnabled, "Emergency recovery already enabled");
        emergencyRecoveryEnabled = true;
    }

    // ============ 查询函数 ============
    function getRecoveryStatus() public view returns (bool initiated, bool completed, bool paused, uint256 timeLockRemaining) {
        uint256 remaining = 0;
        if (isRecoveryInitiated && !isRecoveryCompleted) {
            uint256 elapsedTime = block.timestamp - recoveryTimestamp;
            if (elapsedTime < timeLockDuration) {
                remaining = timeLockDuration - elapsedTime;
            }
        }

        return (isRecoveryInitiated, isRecoveryCompleted, isPaused, remaining);
    }

    function getRecoveryInfo() public view returns (address _originalOwner, address _recoveryAddress, address _targetActive, uint256 _threshold, uint256 _timeLockDuration, uint256 _recoveryTimestamp) {
        return (originalOwner, recoveryAddress, targetActive, threshold, timeLockDuration, recoveryTimestamp);
    }

    function canCompleteRecovery() public view returns (bool) {
        return isRecoveryInitiated && !isRecoveryCompleted && !isPaused && block.timestamp >= recoveryTimestamp + timeLockDuration;
    }
}
